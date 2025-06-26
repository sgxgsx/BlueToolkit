import subprocess


def check_setup() -> bool:
    try:
        output = subprocess.check_output("lsusb", shell=True, text=True)
        if "c0ca:c01a" in output:
            return True

    except subprocess.CalledProcessError as _:
        pass

    return False


if __name__ == "__main__":
    print(check_setup())
