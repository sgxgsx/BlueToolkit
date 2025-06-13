import os
import pkg_resources
import sys
import argparse
import logging
import signal

from tqdm import tqdm
from pathlib import Path
from tabulate import tabulate
from colorama import Fore

from bluekit.constants import (
    CURRENT_DIRECTORY,
    TOOLKIT_BLUEEXPLOITER_INSTALLATION_DIRECTORY,
    TOOLKIT_INSTALLATION_DIRECTORY,
)
from bluekit.constants import LOG_FILE, OUTPUT_DIRECTORY, BLUING_BR_LMP
from bluekit.factories.exploitfactory import ExploitFactory
from bluekit.factories.hardwarefactory import HardwareFactory
from bluekit.engine.engine import Engine
from bluekit.verifyconn import check_device_status
from bluekit.checkpoint import Checkpoint
from bluekit.setupverfication.setupverification import SetupVerifier
from bluekit.recon import Recon, COMMANDS, load_recon_data
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
        self.setupverifier = SetupVerifier()
        self.recon = Recon()
        self.report = Report(self)

    def bluekit_signal_handler(self, sig, frame):
        print("Ctrl+C detected. Creating a checkpoint and exiting")
        self.preserve_state()
        os.chdir(CURRENT_DIRECTORY)
        sys.exit()

    # important to initialize parameters
    def set_parameters(self, parameters: list):
        self.parameters = parameters

    def set_explude_exploits(self, exclude_exploits: list):
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
        return self.exploitFactory.get_all_exploits()

    def get_available_hardware(self):
        return self.hardwareFactory.get_all_hardware_profiles()

    def check_setup(self):
        available_hardware = self.get_available_hardware()
        hardware_verfied = self.setupverifier.verify_setup_multiple_hardware(
            available_hardware
        )
        print("Hardware availability:")
        for hardware in available_hardware:
            print(f"{hardware.name} - status - {hardware_verfied[hardware.name]}")

    def get_exploits_with_setup(self):
        available_exploits = self.get_available_exploits()
        available_hardware = self.get_available_hardware()
        hardware_verfied = self.setupverifier.verify_setup_multiple_hardware(
            available_hardware
        )
        return [
            exploit
            for exploit in available_exploits
            if hardware_verfied[exploit.hardware]
        ]

    def get_exploits_with_setup_exploits(self, exploits):
        available_hardware = self.get_available_hardware()
        hardware_verfied = self.setupverifier.verify_setup_multiple_hardware(
            available_hardware
        )
        return [exploit for exploit in exploits if hardware_verfied[exploit.hardware]]

    def print_available_exploits(self):
        available_exploits = self.get_available_exploits()
        available_hardware = self.get_available_hardware()
        hardware_verfied = self.setupverifier.verify_setup_multiple_hardware(
            available_hardware
        )

        available_exploits = sorted(available_exploits, key=lambda x: x.type)
        available_exploits = sorted(available_exploits, key=lambda x: x.hardware)
        available_exploits = sorted(
            available_exploits, key=lambda x: not hardware_verfied[x.hardware]
        )

        headers = [
            "Index",
            "Exploit",
            "Type",
            "Hardware",
            "Available",
            "BT min",
            "BT max",
        ]
        table_data = []
        index = 1
        for exploit in available_exploits:
            symbol = "❌"
            if hardware_verfied[exploit.hardware]:
                symbol = "✅"
            table_data.append(
                [
                    f"{index}",
                    f"{exploit.name}",
                    f"{exploit.type}",
                    f"{exploit.hardware}",
                    f"{symbol}",
                    f"{exploit.bt_version_min}",
                    f"{exploit.bt_version_max}",
                ]
            )
            index += 1

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
            self.check_target(target)
            response_code, data = self.test_exploit(target, exploits[i], parameters)
            # done TODO add results data to done_exploits
            self.done_exploits.append([exploits[i].name, response_code, data])
            logging.info(
                "Blueexploiter.test_one_by_one -> done exploits - "
                + str(self.done_exploits)
            )
            self.report.save_data(
                exploit_name=exploits[i].name,
                target=target,
                data=data,
                code=response_code,
            )

    def check_target(self, target):
        cont = True
        while cont:
            for _ in range(10):
                status = check_device_status(target)
                if status in (1, 4):
                    logging.info(
                        "Blueexploiter.check_target -> Device does not accept pairing"
                    )
                elif status in (0, 3):
                    logging.info(
                        "Blueexploiter.check_target -> Device does not accept connections"
                    )
                else:
                    return True

            while True:
                cmd = input(
                    "Device is might not be available. Do you want to try again? (Y/n):"
                )
                if cmd.lower() == "y":
                    logging.info("Trying to verify connectivity again")
                    break
                elif cmd.lower() == "n":
                    logging.info("Backing up")
                    self.preserve_state()
                    sys.exit()
                else:
                    logging.info("Invalid input. Please enter 'Y' or 'n'.")

    def command_input(self) -> None:
        command = input(
            "The target device is not available. Try restoring the connectivity. After that enter 1 of the following commands: continue, backup:\n"
        )
        if command == "continue":
            print("Trying to verify connectivity again")
        elif command == "backup":
            print("Backing up")
            self.preserve_state()
            raise SystemExit
        else:
            print("Didn't understand your input")

    # Start testing from a checkpoint
    def start_from_a_checkpoint(self, target) -> None:
        if self.check_if_checkpoint(target):
            exploit_pool = self.load_state(
                target
            )  # Maybe it would be wise to check whether the hardware is still available

            self.test_one_by_one(self.target, self.parameters, exploit_pool)

    # Start testing from a normal call (testing all exploits)
    def start_from_cli_all(self, target, parameters) -> None:
        logging.info(f"start_from_cli_all -> Target: {target}")
        available_exploits = self.get_available_exploits()
        exploits_with_setup = self.exploit_filter(
            target=target, exploits=self.get_exploits_with_setup()
        )

        print(
            f"There are {len(exploits_with_setup)} out of {len(available_exploits)} exploits available.\n"
        )
        print(
            f"Running the following exploits: {[exploit.name for exploit in exploits_with_setup]}"
        )

        exploit_pool = exploits_with_setup
        self.parameters = parameters
        self.target = target
        self.test_one_by_one(target, self.parameters, exploit_pool)

    def exploit_filter(self, target, exploits) -> list:
        # Check if recon files exist by attempting to get version
        vendor, version, type = load_recon_data(target)
        # version = self.recon.determine_bluetooth_version(target)

        # If version is None, it means recon files don't exist - run recon
        if version is None:
            print("Recon data not found. Running recon...")
            self.recon.run_recon(target)
            vendor, version, type = load_recon_data(target)
            if version is None:
                print(
                    "Recon failed to get device information. Please ensure the device is available and try again."
                )
                return []
        else:
            # Get path to recon file for logging
            recon_file = os.path.join(
                OUTPUT_DIRECTORY.format(target=target, exploit="recon"),
                "recon.json",
            )
            print(f"Recon data found - {recon_file}")

        logging.info(
            f"start_from_cli_all -> available exploit amount - {len(exploits)}"
        )
        logging.info(
            f"start_from_cli_all -> exploits to scan amount - {len(self.exploits_to_scan)}"
        )

        if len(self.exploits_to_scan) > 0:
            exploits = [
                exploit for exploit in exploits if exploit.name in self.exploits_to_scan
            ]
        elif len(self.exclude_exploits) > 0:  # not checked if --exploits is provided
            exploits = [
                exploit
                for exploit in exploits
                if exploit.name not in self.exclude_exploits
            ]  # suboptimal implementation, but should be fine
        logging.info(
            f"start_from_cli_all -> available exploit again amount - {len(exploits)}"
        )

        exploits = [exploit for exploit in exploits if exploit.mass_testing]

        if version is not None:
            logging.info(f"Target Bluetooth version: {version}")
            exploits = [
                exploit
                for exploit in exploits
                if float(exploit.bt_version_min)
                <= float(version)
                <= float(exploit.bt_version_max)
            ]
            logging.info(f"Only {len(exploits)} exploits can be used")

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
            exploits=self.get_exploits_with_setup_exploits(exploit_pool),
        )
        available_exploits = self.get_available_exploits()

        print(
            f"There are {len(exploit_pool) + len(self.done_exploits)} / {len(available_exploits)} exploits left. {len(self.done_exploits)} have already been tested.\n"
        )
        print(
            f"Running the following exploits: {[exploit.name for exploit in exploit_pool]}"
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
        self.report.generate_machine_readable_report(target=target)


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
    parser.add_argument(
        "-v", "--verbosity", required=False, type=str, help="Verbosity level"
    )
    parser.add_argument(
        "-ex",
        "--excludeexploits",
        required=False,
        nargs="+",
        default=[],
        type=str,
        help="Exclude exploits, example --exclude exploit1, exploit2",
    )
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
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    logging.info("Started")

    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    logging.info(script_dir)
    distribution = pkg_resources.get_distribution("bluekit")

    logging.info(str(distribution))
    logging.info(str(distribution.location))
    logging.info(Path(__file__))

    logging.info("Additional parameters -> " + str(args.rest))

    addition_parameters = args.rest  # maybe args.rest[1:] is needed, not sure.

    # Store original working directory
    original_dir = os.getcwd()
    os.chdir(TOOLKIT_INSTALLATION_DIRECTORY)
    blueExp = BlueKit()
    # Pass original directory to BlueKit
    blueExp.original_dir = original_dir
    if args.listexploits:
        blueExp.print_available_exploits()
    elif args.checksetup:
        blueExp.check_setup()
    elif args.target:
        target = args.target.lower()
        if len(args.hardware) > 0:
            blueExp.set_exploits_hardware(args.hardware)
            logging.info("Provided --hardware parameter -> " + str(args.hardware))
        elif len(args.exploits) > 0:
            blueExp.set_exploits(args.exploits)
            logging.info("Provided --exploit parameter -> " + str(args.exploits))
        elif len(args.excludeexploits) > 0:  # scips --exclude if --exploits is provided
            blueExp.set_explude_exploits(args.excludeexploits)
            logging.info("Provided --exclude parameter -> " + str(args.excludeexploits))

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

    os.chdir(CURRENT_DIRECTORY)


if __name__ == "__main__":
    main()
