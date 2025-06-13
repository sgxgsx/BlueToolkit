import subprocess
import argparse
import re
import os
from pathlib import Path

from bluekit.constants import (
    COMMAND_CONNECT,
    COMMAND_INFO,
    REGEX_COMMAND_CONNECT,
    NUMBER_OF_DOS_TESTS,
    MAX_NUMBER_OF_DOS_TEST_TO_FAIL,
)
from bluekit.constants import (
    RETURN_CODE_NOT_VULNERABLE,
    RETURN_CODE_ERROR,
    RETURN_CODE_NONE_OF_4_STATE_OBSERVED,
    RETURN_CODE_UNDEFINED,
    RETURN_CODE_VULNERABLE,
)
from bluekit.constants import OUTPUT_DIRECTORY
from pybtool.device import Device

RETVAL_TARGET_NOT_AVAILABLE = 0
RETVAL_TARGET_CONN_ONLY = 1
RETVAL_TARGET_PAIRABLE = 2
RETVAL_TARGET_ADV_ONLY = 3
RETVAL_TARGET_ADV_CONN = 4
RETVAL_TARGET_ADV_CONN_PAIRABLE = 5


def check_device_status(target: str) -> int:
    """
    Check the status of a Bluetooth device by scanning, connecting, and pairing.
    Returns:
        int:
            0: Not found, not connectable
            1: Not found, connectable, not pairable
            2: Not found, connectable, pairable
            3: Found, not connectable
            4: Found, connectable, not pairable
            5: Found, connectable, pairable
    """
    # Initialize the device, default dev ID is 0
    dev = Device()
    dev.power_on()

    scan_success = dev.scan(target=target)
    connect_success = dev.connect(target)

    if not connect_success:
        return 0 if not scan_success else 3

    pair_success = dev.pair()

    if not pair_success:
        return 1 if not scan_success else 4

    dev.disconnect()
    dev.power_off()

    return 2 if not scan_success else 5


def dos_checker(target: str):
    try:
        not_available = 0
        while True:
            # for i in range(NUMBER_OF_DOS_TESTS):
            status = check_device_status(target)
            if status in (1, 2, 4, 5):  # Connectable and/or pairable
                return RETURN_CODE_NOT_VULNERABLE, str(not_available)

            not_available += 1

            if (
                not_available > MAX_NUMBER_OF_DOS_TEST_TO_FAIL
                or not_available > NUMBER_OF_DOS_TESTS
            ):
                return RETURN_CODE_VULNERABLE, str(not_available)
    except Exception as e:
        return RETURN_CODE_ERROR, str(e)


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "-t", "--target", required=False, type=str, help="target MAC address"
#     )
#     parser.add_argument(
#         "-a", "--availability", required=False, type=bool, help="check availability"
#     )
#     parser.add_argument(
#         "-c", "--connectivity", required=False, type=bool, help="check connectivity"
#     )
#     args = parser.parse_args()

#     if args.target:
#         if args.availability:
#             check_availability(args.target)
#         if args.connectivity:
#             check_connectivity(args.target)

#     else:
#         parser.print_help()
