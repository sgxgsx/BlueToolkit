import importlib
import os
import sys
import argparse
import logging
import signal

from tqdm import tqdm
from tabulate import tabulate
from colorama import Fore

from bluekit.logger import Logger
from bluekit.constants import (
    TOOLKIT_INSTALL_DIR,
)
from bluekit.constants import LOG_FILE, OUTPUT_DIR, ConnVerifier
from bluekit.factories.exploitfactory import ExploitFactory
from bluekit.factories.hardwarefactory import HardwareFactory
from bluekit.engine.engine import Engine
from bluekit.verifyconn import check_device_status
from bluekit.checkpoint import Checkpoint
from bluekit.recon import Recon, load_recon_data
from bluekit.report import Report


class BlueKit:
    def __init__(self) -> None:
        signal.signal(signal.SIGINT, self.bluekit_signal_handler)
        self.done_exploits = []
        self.exclude_exploits = []
        self.exploits_to_scan = []
        self.target = None
        self.parameters = None
        self.exploitFactory = ExploitFactory()
        self.hardwareFactory = HardwareFactory()
        self.engine = Engine()
        self.checkpoint = Checkpoint()
        self.recon = Recon()
        self.report = Report(self.exploitFactory)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.original_dir = os.getcwd()

    def bluekit_signal_handler(self, sig, frame):
        print("Ctrl+C detected. Creating a checkpoint and exiting")
        self.preserve_state()
        os.chdir(os.getcwd())
        sys.exit()

    # important to initialize parameters
    def set_parameters(self, parameters: list):
        self.parameters = parameters

    def set_exclude_exploits(self, exclude_exploits: list):
        self.exclude_exploits = exclude_exploits

    def set_exploits(self, exploits_to_scan: list):
        self.exploits_to_scan = exploits_to_scan

    def set_exploits_hardware(self, hardware: list):
        available_exploits = self.get_available_exploits()
        available_exploits = [
            exploit for exploit in available_exploits if exploit.hardware in hardware
        ]
        self.set_exploits(available_exploits)

    def get_available_exploits(self):
        return self.exploitFactory.get_exploits()

    def get_available_hardware(self):
        return self.hardwareFactory.get_hardware_profiles()

    def check_setup(self):
        available_hardware = self.get_available_hardware()

        for hardware in available_hardware:
            self.logger.info(f"{hardware.name} - status - {hardware.is_verified}")

    def get_exploits_with_setup(self, exploits: list = None):
        if exploits is None:
            exploits = self.get_available_exploits()
        verified_hardware = [
            hw.name for hw in self.get_available_hardware() if hw.is_verified
        ]
        return [
            exploit for exploit in exploits if exploit.hardware in verified_hardware
        ]

    def print_available_exploits(self):
        available_exploits = self.get_available_exploits()

        verified_hardware = [
            hw.name for hw in self.get_available_hardware() if hw.is_verified
        ]

        available_exploits.sort(
            key=lambda x: (
                x.hardware not in verified_hardware,
                x.hardware,
                x.type,
            ),
        )

        headers = [
            "Index",
            "Exploit",
            "Type",
            "Hardware",
            "Available",
            "BT min",
            "BT max",
            "BT Type",
        ]
        table_data = [
            [
                idx + 1,
                exploit.name,
                exploit.type,
                exploit.hardware,
                "✅" if exploit.hardware in verified_hardware else "❌",
                exploit.bt_version_min,
                exploit.bt_version_max,
                exploit.bt_type,
            ]
            for idx, exploit in enumerate(available_exploits)
        ]

        table = tabulate(
            table_data,
            headers,
            tablefmt="pretty",
            colalign=("center", "left", "left", "left"),
        )
        print(table)

    def test_exploit(self, target, current_exploit, parameters) -> tuple:
        return self.engine.run_test(target, current_exploit, parameters)

    def test_one_by_one(self, target, parameters, exploits) -> None:
        for i in tqdm(range(0, len(exploits), 1), desc="Testing exploits"):
            if self.check_target(target):
                response_code, data = self.test_exploit(target, exploits[i], parameters)
                # done TODO add results data to done_exploits
                self.done_exploits.append([exploits[i].name, response_code, data])
                self.logger.debug(f"{self.done_exploits} exploits done")
                self.report.save_data(
                    exploit_name=exploits[i].name,
                    target=target,
                    data=data,
                    code=response_code,
                )
            else:
                self.preserve_state()
                sys.exit()

    def check_target(self, target):
        while True:
            for _ in range(ConnVerifier.MAX_DOS_TESTS):
                status = check_device_status(
                    target, only_conn=True
                )  # Does not check pairability
                if status & ConnVerifier.TARGET_CONNECTABLE:
                    return True

            while True:
                cmd = input("Device not available. Do you want to try again? (Y/n):")
                if cmd.lower() in ("y", "", " "):
                    self.logger.debug("Trying to verify connectivity again")
                    break

                if cmd.lower() == "n":
                    return False

                print("Invalid input. Please enter 'y' or 'n'.")

    # Start testing from a checkpoint
    def start_from_a_checkpoint(self, target) -> None:
        if self.check_if_checkpoint(target):
            exploit_pool = self.load_state(
                target
            )  # Maybe it would be wise to check whether the hardware is still available

            self.test_one_by_one(self.target, self.parameters, exploit_pool)

    # Start testing from a normal call (testing all exploits)
    def start_from_cli_all(self, target, parameters) -> None:
        available_exploits = self.get_available_exploits()
        exploits_with_setup = self.exploit_filter(
            target=target, exploits=self.get_exploits_with_setup()
        )

        self.logger.info(
            f"{len(exploits_with_setup)} / {len(available_exploits)} exploits available."
        )
        self.logger.debug(
            f"Running {[exploit.name for exploit in exploits_with_setup]}"
        )

        exploit_pool = exploits_with_setup
        self.parameters = parameters
        self.target = target
        self.test_one_by_one(target, self.parameters, exploit_pool)

    def exploit_filter(self, target, exploits) -> list:
        # Check if recon files exist by attempting to get version
        vendor, version, bt_type = load_recon_data(target)
        # version = self.recon.determine_bluetooth_version(target)

        # If version is None, it means recon files don't exist - run recon
        if version is None:
            self.recon.run_recon(target)
            vendor, version, bt_type = load_recon_data(target)
            if version is None:
                self.logger.warning(
                    "No device information available. Ensure the device is available and try again."
                )
                return []
        else:
            # Get path to recon file for logging
            recon_file = os.path.join(
                OUTPUT_DIR.format(target=target, exploit="recon"),
                "recon.json",
            )
            self.logger.debug(f"Recon data found in {recon_file}")

        self.logger.debug(
            f"There are {len(exploits)} available, of which {len(self.exploits_to_scan)} to be tested"
        )

        if len(self.exploits_to_scan) > 0:
            self.logger.debug("Filtering requested exploits (flag --exploits)")
            exploits = [
                exploit for exploit in exploits if exploit.name in self.exploits_to_scan
            ]
        elif len(self.exclude_exploits) > 0:  # not checked if --exploits is provided
            self.logger.debug("Filtering excluded exploits (flag --exclude-exploits)")
            exploits = [
                exploit
                for exploit in exploits
                if exploit.name not in self.exclude_exploits
            ]  # suboptimal implementation, but should be fine

        exploits = [exploit for exploit in exploits if exploit.mass_testing]

        if bt_type is not None:
            exploits = [exploit for exploit in exploits if exploit.bt_type == bt_type]
            version = None if float(version) == 0.0 else version

        if version is not None:
            exploits = [
                exploit
                for exploit in exploits
                if float(exploit.bt_version_min)
                <= float(version)
                <= float(exploit.bt_version_max)
            ]

        self.logger.debug(f"Only {len(exploits)} exploits can be used")

        return exploits

    # Check whether a checkpoint exists
    def check_if_checkpoint(self, target) -> bool:
        return self.checkpoint.check_if_checkpoint(target)

    # Create a checkpoint
    def preserve_state(self) -> None:
        self.checkpoint.preserve_state(
            self.get_available_exploits(),
            self.done_exploits,
            self.target,
            self.parameters,
            self.exploits_to_scan,
            self.exclude_exploits,
        )

    # Loading a checkpoint
    def load_state(self, target) -> None:
        (
            exploit_pool,
            self.done_exploits,
            self.parameters,
            self.target,
            self.exploits_to_scan,
            self.exclude_exploits,
        ) = self.checkpoint.load_state(target)
        exploit_pool = self.exploit_filter(
            target=self.target,
            exploits=self.get_exploits_with_setup(exploits=exploit_pool),
        )
        available_exploits = self.get_available_exploits()

        self.logger.info(
            f"There are {len(exploit_pool) + len(self.done_exploits)} / {len(available_exploits)} exploits left. {len(self.done_exploits)} have already been tested.\n"
        )
        self.logger.debug(
            f"Running exploits: {[exploit.name for exploit in exploit_pool]}"
        )

        return exploit_pool

    def run_recon(self, target):
        self.recon.run_recon(target)

    def generate_report(self, target):
        # Generate and print the CLI table report only
        table = self.report.generate_report(target=target)
        print("\nReport for target device:\n")
        print(table)

    def generate_machine_readable_report(self, target):
        self.report.generate_machine_readable_report(
            target=target, directory=self.original_dir
        )


class TqdmLoggingHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            if sys.stdout.isatty():
                tqdm.write(msg, file=sys.stdout)
            else:
                # Fallback to standard print if not a TTY (e.g., running in IDE output window or redirected)
                print(msg, file=sys.stdout)
            self.flush()  # Ensure the message is written immediately
        except Exception:
            self.handleError(record)


def setup_logging(log_level: int = logging.INFO):
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(
        fmt="[%(levelname)s][%(name)s] %(message)s",
    )

    # handler = logging.StreamHandler(sys.stdout)
    handler = TqdmLoggingHandler(log_level)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--target", required=False, type=str, help="target MAC address"
    )
    parser.add_argument(
        "-l",
        "--listexploits",
        required=False,
        action="store_true",
        help="List exploits or not",
    )
    parser.add_argument(
        "-c",
        "--checksetup",
        required=False,
        action="store_true",
        help="Check whether Braktooth is available and setup",
    )
    parser.add_argument(
        "-ct",
        "--checktarget",
        required=False,
        action="store_true",
        help="Check connectivity and availability of the target",
    )
    parser.add_argument(
        "-ch",
        "--checkpoint",
        required=False,
        action="store_true",
        help="Start from a checkpoint",
    )
    parser.add_argument("-d", "--debug", required=False, type=str, help="Debug level")
    parser.add_argument(
        "-e",
        "--exploits",
        required=False,
        nargs="+",
        default=[],
        type=str,
        help="Scan only for provided --exploits exploit1, exploit2; --exclude is not taken into account",
    )
    parser.add_argument(
        "-ex",
        "--exclude-exploits",
        required=False,
        nargs="+",
        default=[],
        type=str,
        help="Exclude exploits, example --exclude-exploits exploit1, exploit2",
    )

    parser.add_argument(
        "-r", "--recon", required=False, action="store_true", help="Run a recon script"
    )
    parser.add_argument(
        "-re",
        "--report",
        required=False,
        action="store_true",
        help="Create a report for a target device",
    )
    parser.add_argument(
        "-rej",
        "--reportjson",
        required=False,
        action="store_true",
        help="Create a report for a target device",
    )
    parser.add_argument(
        "-hh",
        "--hardware",
        required=False,
        nargs="+",
        default=[],
        type=str,
        help="Scan only for provided exploits based on hardware --hardware hardware1 hardware2; --exclude and --exploit are not taken into account",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=importlib.metadata.version("bluekit"),
        help="Display bluekit version",
    )
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    setup_logging()

    # script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    # logging.info(script_dir)
    distribution = importlib.metadata.version("bluekit")

    logging.info(f"Using {distribution}")
    # logging.info(Path(__file__))

    logging.debug("Additional parameters -> " + str(args.rest))

    addition_parameters = args.rest  # maybe args.rest[1:] is needed, not sure.
    # Store original working directory
    blueExp = BlueKit()
    os.chdir(TOOLKIT_INSTALL_DIR)
    # Pass original directory to BlueKit
    if args.listexploits:
        blueExp.print_available_exploits()
    elif args.checksetup:
        blueExp.check_setup()
    elif args.target:
        target = args.target.lower()

        if len(args.hardware) > 0:
            blueExp.set_exploits_hardware(args.hardware)
            # logging.info("Provided --hardware parameter -> " + str(args.hardware))
        elif len(args.exploits) > 0:
            blueExp.set_exploits(args.exploits)
            # logging.info("Provided --exploit parameter -> " + str(args.exploits))
        elif (
            len(args.exclude_exploits) > 0
        ):  # scips --exclude if --exploits is provided
            blueExp.set_exclude_exploits(args.exclude_exploits)
            # logging.info("Provided --exclude parameter -> " + str(args.excludeexploits))

        if args.checktarget:
            blueExp.check_target(target)
        else:
            if args.recon:
                blueExp.run_recon(target)
            elif args.report:
                blueExp.generate_report(target)
            elif args.reportjson:
                blueExp.generate_machine_readable_report(target)
            elif args.checkpoint:
                blueExp.start_from_a_checkpoint(target)
            else:
                blueExp.start_from_cli_all(target, addition_parameters)
    else:
        parser.print_help()

    os.chdir(os.getcwd())


if __name__ == "__main__":
    main()
