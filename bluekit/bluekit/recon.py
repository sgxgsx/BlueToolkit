import json
import subprocess
import argparse
import re
import logging
import time
import signal
from pybtool.device import Device
from pybtool.constants import (
    BLE_ROLE_CENTRAL,
    BLE_ROLE_PERIPHERAL,
    BT_MODE_BLE,
    BT_MODE_BREDR,
)


from pathlib import Path
from bluekit.verifyconn import check_device_status

from bluekit.constants import (
    OUTPUT_DIRECTORY,
)
from bluekit.constants import LOG_FILE
from pybtool.constants import BT_MODE_DUAL


logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


class Recon:
    # def __init__(self):

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
        dev = Device(role=BLE_ROLE_CENTRAL, bt_mode=BT_MODE_DUAL)
        dev.power_on()
        #     device.power_off()
        # # Initialize the device, default dev ID is 0
        # device = BcDevice()
        res = {}
        complete = False
        start_time = time.time()
        while not complete:
            # Check if dev is advertising
            res["type"] = dev.scan(timeout=5, target=target)
            if res["type"] is not None:
                res["advertising"] = True
            print(f"Recon.py -> found device type: {res['type']}")
            # Check if dev is connectable, default expect random address
            if dev.connect(
                target, bt_type=BT_MODE_BLE if res["type"] == "BLE" else BT_MODE_BREDR
            ):
                print("Connected")

                res["connectable"] = True
                # Tries to get the version and vendor
                res["version"], res["vendor"] = dev.get_remote_version()
                logging.info("Recon.py -> got version and vendor")

                # Tries to get the ll/lmp remote features
                features = dev.get_remote_features()
                print("Recon.py -> got remote features")
                if res["type"] == "BREDR":
                    res["lmp_features"] = features
                else:
                    res["ll_features"] = features

                # Tries to get the pairing features (TODO: decode the value)
                res["pairable"], res["pairing_features"] = dev.pair()
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

        return data["lmp_features"] if data["type"] == "BREDR" else data["ll_features"]


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
