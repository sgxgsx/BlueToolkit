import time
from bluekit.constants import ConnVerifier, ReturnCode

from pybtool.device import Device
from pybtool.constants import (
    BLE_ROLE_CENTRAL,
    BLE_ROLE_PERIPHERAL,
    BT_MODE_BLE,
    BT_MODE_BREDR,
    BT_MODE_DUAL,
)


def print_device_status(status: int):
    if status == 0:
        return "Device not advertising and not connectable"

    parts = []

    if status & ConnVerifier.TARGET_ADVERTISING:
        parts.append("advertising")
    else:
        parts.append("not advertising")

    if status & ConnVerifier.TARGET_CONNECTABLE:
        parts.append("connectable")
    else:
        parts.append("not connectable")

    if status & ConnVerifier.TARGET_PAIRABLE:
        parts.append("pairable")
    else:
        parts.append("not pairable")

    print("Device " + ", ".join(parts))


def check_device_status(target: str, only_conn: bool = False) -> int:
    """
    Check the status of a Bluetooth device by scanning, connecting, and pairing.
    """
    # Initialize the device, default dev ID is 0
    dev = Device(role=BLE_ROLE_CENTRAL, bt_mode=BT_MODE_DUAL)
    dev.power_on()

    retval = ConnVerifier.TARGET_NOT_AVAILABLE

    if dev.scan(target=target):
        retval = ConnVerifier.TARGET_ADVERTISING

    if dev.connect(target):
        retval = retval | ConnVerifier.TARGET_CONNECTABLE

    if retval & ConnVerifier.TARGET_CONNECTABLE and not only_conn:
        if dev.pair():
            retval = retval | ConnVerifier.TARGET_PAIRABLE

    dev.disconnect()
    dev.power_off()

    return retval


def dos_checker(target: str):
    try:
        for i in range(ConnVerifier.MAX_DOS_TESTS):
            status = check_device_status(target, only_conn=True)
            if (
                status & ConnVerifier.TARGET_CONNECTABLE
                or status & ConnVerifier.TARGET_PAIRABLE
            ):
                return ReturnCode.NOT_VULNERABLE, str(i)
            time.sleep(0.5)
            # TODO: what if it is advertising only?

        return ReturnCode.VULNERABLE, str(i)
    except Exception as e:
        return ReturnCode.ERROR, str(e)
