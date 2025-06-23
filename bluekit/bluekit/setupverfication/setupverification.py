import subprocess
import logging
import glob


class SetupVerifier:
    logger = logging.getLogger(__qualname__)

    def verify_setup(self, hardware) -> bool:
        if hardware.needs_setup_verification:
            if hardware.name not in hardware_verfier:
                self.logger.warning(f"Hardware - {hardware.name} is not registered")
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
            output = glob.glob("/dev/ttyUSB*")
            if any(dev in output for dev in ["/dev/ttyUSB0", "/dev/ttyUSB1"]):
                return True

            SetupVerifier.logger.info("ESP32 is not connected or not available")
        except subprocess.CalledProcessError as e:
            SetupVerifier.logger.info(f"Error checking esp32 setup {e}")
        return False

    @staticmethod
    def check_setup_nexus5() -> bool:
        try:
            output = subprocess.check_output("adb devices -l", shell=True).decode()
            if "device:hammerhead" in output:  # hammeread is the codename for Nexus 5
                return True

            SetupVerifier.logger.info("Nexus5 is not connected or not available")

        except subprocess.CalledProcessError as e:
            SetupVerifier.logger.info(f"Error checking nexus5 setup: {e}")

        return False


# Add your hardware verification function
hardware_verfier = {
    "esp32": SetupVerifier.check_setup_esp32,
    "nexus5": SetupVerifier.check_setup_nexus5,
}
