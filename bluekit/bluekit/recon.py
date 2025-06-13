import json
import subprocess
import argparse
import re
import logging
import time
import signal
from pybtool.device import Device

from pathlib import Path
from bluekit.verifyconn import check_device_status

from bluekit.constants import (
    HCITOOL_INFO,
    SDPTOOL_INFO,
    BLUING_BR_SDP,
    OUTPUT_DIRECTORY,
)
from bluekit.constants import LOG_FILE, REGEX_BT_MANUFACTURER

COMMANDS = [HCITOOL_INFO, SDPTOOL_INFO, BLUING_BR_SDP]
invaisive_commands = [HCITOOL_INFO]

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


class Recon:
    def __init__(self, mode: str = "classic"):
        self.mode = mode

    def check_target(self, target: str):
        status = check_device_status(target)
        if status == 0:
            print("Device not advertising and not connectable")
        elif status == 1:
            print("Device not advertising, connectable but not pairable")
        elif status == 2:
            print("Device not advertising, connectable and pairable")
        elif status == 3:
            print("Device advertising but not connectable")
        elif status == 4:
            print("Device advertising and connectable but not pairable")
        elif status == 5:
            print("Device advertising, connectable and pairable")

    def run_command(self, target, command, filename):
        print(f"Running command -> {command}")
        try:
            output = subprocess.check_output(
                command.format(target=target), shell=True
            ).decode()
            f = open(filename, "w")
            f.write(output)
            f.close()
            return True
        except subprocess.CalledProcessError:
            # Silently fail - errors are handled at the recon level
            return False

    def run_recon(
        self, target: str, dev: Device = None, save: bool = True, timeout: int = 20
    ) -> bool:
        """
        Run the recon process on the target device.
        Checks for the following:
        - Advertising
        - Connectable
        - Pairable
        - LMP version
        - Manufacturer
        - LMP features
        - Pairing features (i.e., I/O capabilities)
        """
        if dev is None and self.mode == "classic":
            dev = Device()
        elif dev is None and self.mode == "le":
            # device = BcDevice()
            logging.error("LE recon not implemented yet")
            return False

        dev.power_on()
        #     device.power_off()
        # # Initialize the device, default dev ID is 0
        # device = BcDevice()
        res = {}
        complete = False
        start_time = time.time()
        while not complete:
            # Check if dev is advertising
            res[f"type"] = dev.scan(timeout=5, target=target)
            if res[f"type"] is not None:
                res[f"advertising"] = True
            # Check if dev is connectable, default expect random address
            if dev.connect(target):
                res[f"connectable"] = True
                # Tries to get the version and vendor
                res["version"], res["vendor"] = dev.get_remote_version()
                logging.info("Recon.py -> got version and vendor")

                # Tries to get the ll/lmp remote features
                features = dev.get_remote_features()
                print("Recon.py -> got remote features")
                if self.mode == "classic":
                    res["lmp_features"] = features
                else:
                    res["ll_features"] = features

                # Tries to get the pairing features (TODO: decode the value)
                res[f"pairable"], res[f"pairing_features"] = dev.pair()
                logging.info("Recon.py -> got pairing features")

                dev.disconnect()
                if not any(value is None for value in res.values()):  # Success
                    logging.info("Recon.py -> run_recon terminated successfully")
                    complete = True
                elif time.time() - start_time > timeout:  # Timeout
                    logging.info("Recon.py -> run_recon timed out")
                    break

        if complete and save:
            log_dir = OUTPUT_DIRECTORY.format(target=target, exploit="recon")
            Path(log_dir).mkdir(exist_ok=True, parents=True)
            try:
                with open(f"{log_dir}recon.json", "w") as f:
                    json.dump(res, f, indent=4)  # indent for pretty formatting
                print(f"Recon.py -> recon data saved to {log_dir}")

            except Exception as e:
                logging.error(f"Error writing to {f'{log_dir}recon.json'}: {e}")

        dev.power_off()

        return complete

    # TODO: remove dependenci from hcidump
    def start_hcidump(self):
        logging.info("Starting hcidump -X...")
        process = subprocess.Popen(
            ["hcidump", "-X"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return process

    def stop_hcidump(self, process):
        logging.info("Stopping hcidump -X...")
        process.send_signal(subprocess.signal.SIGINT)
        output, _ = process.communicate()
        logging.info("hcidump -> " + str(output.decode()))
        logging.info("hcidump -X stopped.")
        return output

    def get_hcidump(self, target):
        hcidump_process = self.start_hcidump()
        try:
            time.sleep(1)
            check_device_status(target=target)
        finally:
            return self.stop_hcidump(hcidump_process).decode().split("\n")

    def get_capabilities(self, target):
        data = load_recon_data_full(target)
        if data is None:
            self.run_recon(target=target)
            data = load_recon_data_full(target)
            if data is None:
                logging.error("Device data not available")
                return None

        return data["pairing_features"]["io_capabilities"]

    def get_remote_features(self, target):
        data = load_recon_data_full(target)
        if data is None:
            self.run_recon(target=target)
            data = load_recon_data_full(target)
            if data is None:
                logging.error("Device data not available")
                return None

        return data["lmp_features"] if self.mode == "classic" else data["ll_features"]


def load_recon_data_full(target: str):
    file_path = OUTPUT_DIRECTORY.format(target=target, exploit="recon") + "recon.json"
    if not Path(file_path).exists():
        logging.error(f"Recon data file {file_path} does not exist.")
        return None
    with open(file_path, "r") as f:
        return json.load(f)


def load_recon_data(target: str):
    data = load_recon_data_full(target)
    if data is None:
        return None, None, None
    return data["vendor"], data["version"], data["type"]


# def get_capabilities(self, target):
#     output = self.get_hcidump(target)
#     # Our capability is set as NoInputNoOutput so the other one should be a target device capability
#     capabilities = set()
#     numb_of_capabilities = 0
#     for line in output:
#         if line.strip().startswith("Capability:"):
#             capabilities.add(line.strip().split(" ")[1])
#             numb_of_capabilities += 1
#     logging.info(
#         "recon.py -> found the following capabilities " + str(capabilities)
#     )
#     if len(capabilities) == 0:
#         logging.info("recon.py -> most likely legacy pairing")
#         return None
#     elif numb_of_capabilities == 1:
#         logging.info("recon.py -> got only 1 capability " + str(capabilities))
#         return capabilities.pop()
#     capabilities.remove("NoInputNoOutput")
#     capability = None
#     if len(capabilities) == 0:
#         return "NoInputNoOutput"
#     else:
#         return capabilities.pop()

# def scan_additional_recon_data(self, target):
#     # collect additional data - for now it's only capability

#     capability = self.get_capabilities(target=target)

#     log_dir = OUTPUT_DIRECTORY.format(target=target, exploit="recon")
#     Path(log_dir).mkdir(exist_ok=True, parents=True)
#     filename = log_dir + ADDITIONAL_RECON_DATA_FILE
#     f = open(filename, "w")
#     f.write(capability)
#     f.close()
