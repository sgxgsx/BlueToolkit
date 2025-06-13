import os
from pathlib import Path


BRAKTOOTH_HOME = (
    "/home/weil/Desktop/University/Thesis/toolkit/modules/tools/braktooth/wdissector"
)
BRAKTOOTH_LOG_DIR = "/home/weil/Desktop/University/Thesis/toolkit/modules/tools/braktooth/wdissector/logs/Bluetooth/"
BRAKTOOTH_CHECK_SETUP = "ls /dev/ttyUSB*"
BRAKTOOTH_GET_EXPLOITS = "./bin/bt_exploiter --list-exploits"
BRAKTOOTH_GENERIC_EXPLOIT = "./bin/bt_exploiter --host-port=/dev/ttyUSB1 --target={target} --exploit={exploit} --random_bdaddress"


RETURN_CODE_ERROR = 0
RETURN_CODE_NOT_VULNERABLE = 1
RETURN_CODE_VULNERABLE = 2
RETURN_CODE_UNDEFINED = 3
RETURN_CODE_NONE_OF_4_STATE_OBSERVED = 4
RETURN_CODE_NOT_TESTED = 5


TYPE_DOS = "DoS"
TYPE_POC = "PoC"
TYPE_MANUAL = "Manual"


#### Directories


# TOOLKIT_INSTALLATION_DIRECTORY = '/home/weil/Desktop/University/Thesis/toolkit'       # change during installation
# location = open("/usr/share/BlueToolkit/.installation_directory.conf").read().strip()
# TOOLKIT_BLUEEXPLOITER_INSTALLATION_DIRECTORY = TOOLKIT_INSTALLATION_DIRECTORY + '/bluekit'
# CHECKPOINT_PATH = '/home/weil/Desktop/University/Thesis/data/tests/{target}/.braktooth_checkpoint_{target}.json'
# OUTPUT_DIRECTORY = '/home/weil/Desktop/University/Thesis/data/tests/{target}/{exploit}/'


TOOLKIT_INSTALLATION_DIRECTORY = "/usr/share/BlueToolkit"
TOOLKIT_BLUEEXPLOITER_INSTALLATION_DIRECTORY = (
    TOOLKIT_INSTALLATION_DIRECTORY + "/bluekit"
)
CHECKPOINT_PATH = (
    TOOLKIT_INSTALLATION_DIRECTORY + "/data/tests/{target}/.checkpoint_{target}.json"
)
OUTPUT_DIRECTORY = TOOLKIT_INSTALLATION_DIRECTORY + "/data/tests/{target}/{exploit}/"
TARGET_DIRECTORY = TOOLKIT_INSTALLATION_DIRECTORY + "/data/tests/{target}/"
REPORT_OUTPUT_FILE = OUTPUT_DIRECTORY + "output_report.json"
MACHINE_READABLE_REPORT_OUTPUT_FILE = TARGET_DIRECTORY + "whole-output.json"
LOG_FILE = TOOLKIT_INSTALLATION_DIRECTORY + "/.logs/application.log"

# Exploits and hardware directories
EXPLOIT_DIRECTORY = TOOLKIT_INSTALLATION_DIRECTORY + "/exploits"
HARDWARE_DIRECTORY = TOOLKIT_INSTALLATION_DIRECTORY + "/hardware"


CURRENT_DIRECTORY = os.getcwd()
ADDITIONAL_RECON_DATA_FILE = "additional_data.log"
SKIP_DIRECTORIES = ["recon"]  # skip these directories when getting exploit names


TIMEOUT = 40
NUMBER_OF_DOS_TESTS = 10
MAX_CHARS_DATA_TRUNCATION = 80
MAX_NUMBER_OF_DOS_TEST_TO_FAIL = 5  # > 30 seconds reported as vulnerable
DOS_TEST_DATA_RETURN = "Down - {} , Unpairable - {}"


DEFAULT_CONNECTOR = " "


COMMAND_INFO = "hcitool info {target}"
COMMAND_CONNECT = (
    TOOLKIT_BLUEEXPLOITER_INSTALLATION_DIRECTORY + "/bluekit/reconnect.sh {target}"
)
REGEX_COMMAND_CONNECT = "Device {target} Connected: yes"


HCITOOL_INFO = ("hcitool info {target}", "hciinfo.log")
SDPTOOL_INFO = ("sdptool browse {target}", "sdpinfo.log")
BLUING_BR_SDP = ("bluing br --sdp {target}", "bluing_sdp.log")
BLUING_BR_LMP = ("bluing br --lmp-features {target}", "bluing_lmp.log")
REGEX_BT_VERSION = "Bluetooth Core Specification [0-9]{1}(\.){0,1}[0-9]{0,1}\ "
REGEX_BT_VERSION_HCITOOL = "\(0x[0-f]{1}\) LMP Subversion:"
REGEX_BT_MANUFACTURER = "Manufacturer name: .*\n"


REGEX_EXPLOIT_OUTPUT_DATA = b"BLUEEXPLOITER DATA:.*\n"
REGEX_EXPLOIT_OUTPUT_DATA_CODE = b" code=[0-4],"
REGEX_EXPLOIT_OUTPUT_DATA_DATA = b", data=.*"


VERSION_TABLE = {
    "0x0": 1.0,
    "0x1": 1.1,
    "0x2": 1.2,
    "0x3": 2.0,
    "0x4": 2.1,
    "0x5": 3.0,
    "0x6": 4.0,
    "0x7": 4.1,
    "0x8": 4.2,
    "0x9": 5.0,
    "0xa": 5.1,
    "0xb": 5.2,
    "0xc": 5.3,
    "0xd": 5.4,
}
