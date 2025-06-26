import glob


def check_setup() -> bool:
    try:
        output = glob.glob("/dev/ttyUSB*")
        if any(dev in output for dev in ["/dev/ttyUSB0", "/dev/ttyUSB1"]):
            return True

    except Exception as _:
        pass

    return False


if __name__ == "__main__":
    print(check_setup())
