import json
import logging
import time
from pybtool.device import Device
from pybtool.constants import (
    BLE_ROLE_CENTRAL,
    BLE_ROLE_PERIPHERAL,
    BT_MODE_BLE,
    BT_MODE_BREDR,
)


from pathlib import Path
from bluekit.verifyconn import check_device_status, print_device_status

from bluekit.constants import OUTPUT_DIR, LOG_FILE
from pybtool.constants import BT_MODE_DUAL


# logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


class Recon:
    def __init__(self):
        self.logger = logging.getLogger(
            self.__class__.__name__
        )  # Logger(name=self.__class__.__name__, log_level=logging.INFO).get()

    def check_target(self, target: str):
        status = check_device_status(target)
        print_device_status(status)

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

        res = {}
        complete = False
        start_time = time.time()
        while not complete:
            # Check if dev is advertising
            res["type"] = dev.scan(timeout=5, target=target)
            if res["type"] is not None:
                res["advertising"] = True
            self.logger.debug(f"Device {target} is advertising as {res['type']}")
            # Check if dev is connectable, default expect random address
            if dev.connect(
                target, bt_type=BT_MODE_BLE if res["type"] == "BLE" else BT_MODE_BREDR
            ):
                res["connectable"] = True
                self.logger.debug(f"Device {target} is connectable")

                # Tries to get the version and vendor
                res["version"], res["vendor"] = dev.get_remote_version()

                # Tries to get the ll/lmp remote features
                features = dev.get_remote_features()

                res["lmp_ll_features"] = features

                # Tries to get the pairing features (TODO: decode the value)
                res["pairable"], res["pairing_features"] = dev.pair()
                self.logger.debug(f"Device {target} is pairable")

                dev.disconnect()
                if not any(value is None for value in res.values()):  # Success
                    complete = True
                elif time.time() - start_time > timeout:  # Timeout
                    logging.error("run_recon -> timeout")
                    break

        if complete and save:
            log_dir = OUTPUT_DIR.format(target=target, exploit="recon")
            Path(log_dir).mkdir(exist_ok=True, parents=True)
            try:
                with open(f"{log_dir}recon.json", "w") as f:
                    json.dump(res, f, indent=4)  # indent for pretty formatting

                self.logger.info(f"Saving recon data to {log_dir}")

            except Exception as e:
                self.logger.error(f"Error writing to {log_dir}: {e}")

        dev.power_off()

        return complete

    def get_capabilities(self, target):
        data = load_recon_data_full(target)
        if data is None:
            self.run_recon(target=target)
            data = load_recon_data_full(target)
            if data is None:
                self.logger.error("Device data not available")
                return None
        return data["pairing_features"]["io_capabilities"]

    def get_remote_features(self, target):
        if data := load_recon_data_full(target) is None:
            self.run_recon(target=target)
            if data := load_recon_data_full(target) is None:
                logging.error("Device data not available")
                return None

        return data["lmp_ll_features"]


def load_recon_data_full(target: str):
    file_path = OUTPUT_DIR.format(target=target, exploit="recon") + "recon.json"
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
