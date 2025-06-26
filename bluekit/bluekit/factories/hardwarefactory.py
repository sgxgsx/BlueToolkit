import yaml
import os
from bluekit.constants import HARDWARE_DIR
from bluekit.models.hardware import Hardware


class HardwareFactory:
    def __init__(self, hardware_dir: str = HARDWARE_DIR):
        self.hardware_dir = hardware_dir
        self.hardware = None

    def get_hardware_profiles(self, force_reload=False):
        if self.hardware is None or force_reload:
            files = [
                entry.path for entry in os.scandir(self.hardware_dir) if entry.is_file()
            ]

            self.hardware = [
                HardwareFactory.read_hardware(file)
                for file in files
                if file.endswith(".yaml") or file.endswith(".yml")
            ]

            for hw in self.hardware:
                hw.check_setup()

        return self.hardware

    @staticmethod
    def read_hardware(filename):
        with open(filename, "r") as f:
            details = yaml.safe_load(f)
        return Hardware(details)
