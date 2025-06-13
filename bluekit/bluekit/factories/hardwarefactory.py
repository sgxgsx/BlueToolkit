import yaml
from os import listdir
from os.path import isfile, join

from bluekit.constants import HARDWARE_DIRECTORY
from bluekit.models.hardware import Hadrware


class HardwareFactory:
    def __init__(self, hardware_dir: str = HARDWARE_DIRECTORY):
        self.hardware_dir = hardware_dir
        self.hardware = None

    def get_all_hardware_profiles(self, force_reload=False):
        if self.hardware is None or force_reload:
            onlyfiles = [
                join(self.hardware_dir, f)
                for f in listdir(self.hardware_dir)
                if isfile(join(self.hardware_dir, f))
            ]

            hardware_profiles = []
            for filename in onlyfiles:
                hardware_profiles.append(self.read_hardware(filename))
            self.hardware = hardware_profiles
        return self.hardware

    def read_hardware(self, filename):
        f = open(filename, "r")
        details = yaml.safe_load(f)
        f.close()
        return Hadrware(details)
