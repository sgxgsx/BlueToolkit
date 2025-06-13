import subprocess
import logging

BRAKTOOTH_CHECK_SETUP = "ls /dev/ttyUSB*"

INTERNABLUE_CHECK_SETUP = "adb devices"
INTERNABLUE_CHECK_SETUP_GET_NEXUS = "adb -s {device} shell getprop"


class SetupVerifier:
    def verify_setup(self, hardware) -> bool:
        if hardware.needs_setup_verification:
            if hardware.name not in hardware_verfier:
                logging.warning(f"Hardware - {hardware.name} is not registered")
                return False

            return hardware_verfier[hardware.name]()

        return True

    def verify_setup_multiple_hardware(self, multiple_hardware) -> dict:
        hardware_verification = {}
        for hardware in multiple_hardware:
            hardware_verification[hardware.name] = self.verify_setup(hardware)
        return hardware_verification

    @staticmethod
    def check_setup_esp32() -> bool:
        try:
            output = (
                subprocess.check_output(
                    BRAKTOOTH_CHECK_SETUP, shell=True, stderr=subprocess.PIPE
                )
                .decode()
                .split("\n")[:-1]
            )
            if "/dev/ttyUSB0" in output and "/dev/ttyUSB1" in output:
                print("ESP32 Setup is ready")
                return True
            logging.info(
                "SetupVerfier -> check_setup_esp32 -> ESP32 No available ports"
            )
        except subprocess.CalledProcessError as e:
            logging.info(
                "SetupVerfier -> check_setup_esp32 -> Error during checking esp32 setup"
            )
        return False

    @staticmethod
    def check_setup_nexus5() -> bool:
        try:
            output = subprocess.check_output(
                INTERNABLUE_CHECK_SETUP, shell=True
            ).decode()
            for i in output.split("\n"):
                if "\tdevice" in i:
                    device = i.split("\t")[0]
                    output2 = subprocess.check_output(
                        INTERNABLUE_CHECK_SETUP_GET_NEXUS.format(device=device),
                        shell=True,
                        stderr=subprocess.PIPE,
                    ).decode()
                    try:
                        output2.index("[ro.product.model]: [Nexus 5]")
                        print("Nexus 5 is available")
                        return True
                    except ValueError as e:
                        pass
        except subprocess.CalledProcessError as e:
            logging.info(
                "SetupVerfier -> check_setup_nexus5 -> Error during checking nexus5 setup"
            )
        logging.info("SetupVerfier -> check_setup_nexus5 -> Setup is not ready")
        return False


# Add your hardware verification function
hardware_verfier = {
    "esp32": SetupVerifier.check_setup_esp32,
    "nexus5": SetupVerifier.check_setup_nexus5,
}
