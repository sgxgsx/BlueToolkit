import subprocess


def check_setup() -> bool:
    try:
        output = subprocess.check_output("adb devices -l", text=True, shell=True)
        if "device:hammerhead" in output:  # hammerhead is the codename for Nexus 5
            return True

    except subprocess.CalledProcessError as _:
        pass

    return False


if __name__ == "__main__":
    print(check_setup())
