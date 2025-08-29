# BRAKTOOTH_GET_EXPLOITS = "./bin/bt_exploiter --list-exploits"
# BRAKTOOTH_GENERIC_EXPLOIT = "./bin/bt_exploiter --host-port=/dev/ttyUSB1 --target={target} --exploit={exploit} --random_bdaddress"


TOOLKIT_INSTALL_DIR = "/usr/share/BlueToolkit"
BLUEKIT_INSTALL_DIR = TOOLKIT_INSTALL_DIR + "/bluekit"
LOG_FILE = TOOLKIT_INSTALL_DIR + "/.logs/bluetoolkit.log"


TARGET_DIR = TOOLKIT_INSTALL_DIR + "/data/tests/{target}"
OUTPUT_DIR = TARGET_DIR + "/{exploit}/"
REPORT_OUTPUT_FILE = OUTPUT_DIR + "output_report.json"
FULL_REPORT_OUTPUT_FILE = TARGET_DIR + "output_report_full.json"

# Target here is redundant
CHECKPOINT_PATH = TARGET_DIR + ".checkpoint_{target}.json"


# Exploits and hardware directories
EXPLOIT_DIR = TOOLKIT_INSTALL_DIR + "/exploits"
HARDWARE_DIR = TOOLKIT_INSTALL_DIR + "/hardware"


class ReturnCode:
    ERROR = 0
    NOT_VULNERABLE = 1
    VULNERABLE = 2
    UNDEFINED = 3
    UNKNOWN_STATE = 4
    NOT_TESTED = 5
    SKIPPED = 6


class ExploitType:
    RECON = "Recon"
    DOS = "DoS"
    POC = "PoC"
    MANUAL = "Manual"


# TOOLKIT_INSTALLATION_DIRECTORY = "/usr/share/BlueToolkit"
# # checkpointers = (
# #     TOOLKIT_INSTALLATION_DIRECTORY + "/data/tests/{target}/.checkpoint_{target}.json"
# # )
# OUTPUT_DIRECTORY = TOOLKIT_INSTALLATION_DIRECTORY + "/data/tests/{target}/{exploit}/"
# TARGET_DIRECTORY = TOOLKIT_INSTALLATION_DIRECTORY + "/data/tests/{target}/"
# REPORT_OUTPUT_FILE = OUTPUT_DIRECTORY + "output_report.json"
# MACHINE_READABLE_REPORT_OUTPUT_FILE = TARGET_DIRECTORY + "whole-output.json"
# LOG_FILE = TOOLKIT_INSTALLATION_DIRECTORY + "/.logs/application.log"

# # Exploits and hardware directories
# EXPLOIT_DIRECTORY = TOOLKIT_INSTALLATION_DIRECTORY + "/exploits"
# HARDWARE_DIRECTORY = TOOLKIT_INSTALLATION_DIRECTORY + "/hardware"


ADDITIONAL_RECON_DATA_FILE = "additional_data.log"
SKIP_DIRECTORIES = ["recon"]  # skip these directories when getting exploit names


class ConnVerifier:
    MAX_DOS_TESTS = 5
    TIMEOUT = 30

    TARGET_NOT_AVAILABLE = 0b0000  # 0
    TARGET_CONNECTABLE = 0b0001  # 1
    TARGET_PAIRABLE = 0b0010  # 2
    TARGET_ADVERTISING = 0b0100  # 4


MAX_CHARS_DATA_TRUNCATION = 80
DOS_TEST_DATA_RETURN = "Down - {} , Unpairable - {}"


DEFAULT_CONNECTOR = " "


SDPTOOL_INFO = ("sdptool browse {target}", "sdpinfo.log")

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
