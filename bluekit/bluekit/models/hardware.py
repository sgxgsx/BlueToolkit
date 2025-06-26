import subprocess
from bluekit.constants import HARDWARE_DIR


class Hardware:
    def __init__(self, details):
        self.name = details["name"]
        self.description = details["description"]
        self.working_directory = details["working_directory"]
        self.bt_version_min = details["bt_version_min"]
        self.bt_version_max = details["bt_version_max"]
        self.setup_verification = details["setup_verification"]
        if self.setup_verification:
            self.setup_verification = HARDWARE_DIR + "/" + self.setup_verification
            self.is_verified = False
        else:
            self.is_verified = True

    def check_setup(self):
        if self.setup_verification:
            out = subprocess.check_output(
                ["python3", self.setup_verification], text=True
            )
            self.is_verified = True if out.strip() == "True" else False
