import unittest

from bluekit.constants import TOOLKIT_BLUEEXPLOITER_INSTALLATION_DIRECTORY
from bluekit.bluekit import BlueKit
from bluekit.factories.hardwarefactory import HardwareFactory
from bluekit.factories.exploitfactory import ExploitFactory
from bluekit.models.exploit import Exploit
from bluekit.engine.engine import Engine
from bluekit.checkpoint import Checkpoint


# done TODO add max_timeout to the following tests
test_data = {
    "parameters": ["--target", "AA:AA:AA:AA:AA:AA", "--somethingelse", "test"],
    "parameters_exception": ["--another", "test", "--somethingelse", "test"],
    "target": "AA:AA:AA:AA:AA:AA",
    "hardware": {
        "name": "esp32",
        "description": "ESP 32 board for braktooth exploits",
        "setup_verification": "",
        "working_directory": "/braktooth/wdissector",
        "bt_version_min": 4.0,
        "bt_version_max": 5.3,
    },
    "exploit": {
        "name": "braktooth_knob",
        "author": "Braktooth team",
        "type": "PoC",
        "max_testing": 20,
        "mass_testing": True,
        "bt_version_min": 4.0,
        "bt_version_max": 5.3,
        "hardware": "esp32",
        "command": "./bin/bt_exploiter --host-port=/dev/ttyUSB1 --exploit=knob --random_bdaddress",
        "parameters": [
            {
                "name": "--target",
                "type": "str",
                "name_required": True,
                "help": "Target MAC address",
                "required": True,
                "is_target_param": True,
                "parameter_connector": "=",
            }
        ],
        "log_pull": {
            "in_command": False,
            "from_directory": True,
            "relative_directory": True,
            "pull_directory": "braktooth/wdissector/logs/Bluetooth",
        },
    },
    "exploit2": {
        "name": "internalblue_knob",
        "author": "Internalblue team",
        "type": "PoC",
        "mass_testing": True,
        "bt_version_min": 4.0,
        "bt_version_max": 5.2,
        "hardware": "nexus5",
        "command": "internalblue_KNOB.sh",
        "parameters": [
            {
                "name": "target",
                "name_required": False,
                "type": "str",
                "help": "Target MAC address",
                "required": True,
                "is_target_param": True,
                "parameter_connector": " ",
            },
            {
                "name": "directory",
                "name_required": False,
                "type": "str",
                "help": "Directory to save output",
                "required": True,
                "is_target_param": False,
                "parameter_connector": " ",
            },
        ],
        "log_pull": {"in_command": True, "pull_parameter": "directory"},
    },
    "done_exploits": ["internalblue_knob"],
    "checkpoint_preserve": {
        "exploits": [
            {
                "name": "braktooth_knob",
                "author": "Braktooth team",
                "type": "PoC",
                "mass_testing": True,
                "bt_version_min": 4.0,
                "bt_version_max": 5.3,
                "hardware": "esp32",
                "command": "./bin/bt_exploiter --host-port=/dev/ttyUSB1 --exploit=knob --random_bdaddress",
                "parameters": [
                    {
                        "name": "--target",
                        "type": "str",
                        "name_required": True,
                        "help": "Target MAC address",
                        "required": True,
                        "is_target_param": True,
                        "parameter_connector": "=",
                    }
                ],
                "log_pull": {
                    "in_command": False,
                    "from_directory": True,
                    "relative_directory": True,
                    "pull_directory": "braktooth/wdissector/logs/Bluetooth",
                },
            },
            {
                "name": "internalblue_knob",
                "author": "Internalblue team",
                "type": "PoC",
                "mass_testing": True,
                "bt_version_min": 4.0,
                "bt_version_max": 5.2,
                "hardware": "nexus5",
                "command": "internalblue_KNOB.sh",
                "parameters": [
                    {
                        "name": "target",
                        "name_required": False,
                        "type": "str",
                        "help": "Target MAC address",
                        "required": True,
                        "is_target_param": True,
                        "parameter_connector": " ",
                    },
                    {
                        "name": "directory",
                        "name_required": False,
                        "type": "str",
                        "help": "Directory to save output",
                        "required": True,
                        "is_target_param": False,
                        "parameter_connector": " ",
                    },
                ],
                "log_pull": {"in_command": True, "pull_parameter": "directory"},
            },
        ],
        "parameters": ["--target", "AA:AA:AA:AA:AA:AA", "--somethingelse", "test"],
        "done_exploits": ["internalblue_knob"],
        "target": "AA:AA:AA:AA:AA:AA",
    },
}


class TestHardwareFactory(unittest.TestCase):
    def test_get_all_hardware_profiles(self):
        hf = HardwareFactory()
        hf_profiles = hf.get_all_hardware_profiles()
        for hardware in hf_profiles:
            self.assertIn(hardware.name, ["esp32", "nexus5"])

    def test_read_profile(self):
        hf = HardwareFactory()
        hf_profile = hf.read_hardware("./hardware/esp32.yaml")
        self.assertEqual(hf_profile.name, "esp32")


class TestExploitFactory(unittest.TestCase):
    def test_get_all_hardware_profiles(self):
        ef = ExploitFactory()
        ef_profiles = ef.get_all_exploits()
        for exploit in ef_profiles:
            self.assertIn(exploit.name, ["braktooth_knob", "internalblue_knob"])

    def test_read_exploit(self):
        ef = ExploitFactory()
        ef_profile = ef.read_exploit("./exploits/braktooth_knob.yaml")
        self.assertEqual(ef_profile.name, "braktooth_knob")


class TestBlueExploiter(unittest.TestCase):
    # Check whether there are certain exploits in a directory
    def test_get_exploits(self):
        be = BlueKit()
        av_exploits = be.get_available_exploits()
        for exploit in av_exploits:
            self.assertIn(exploit.name, ["braktooth_knob", "internalblue_knob"])

    def test_get_hardware(self):
        be = BlueKit()
        av_hardware = be.get_available_hardware()
        for hardware in av_hardware:
            self.assertIn(hardware.name, ["esp32", "nexus5"])


class TestEngine(unittest.TestCase):
    def test_construct_exploit_command_exception(self):
        details = test_data["exploit"]
        exploit = Exploit(details)
        engine = Engine()
        engine.check_pull_location(test_data["target"], exploit.name)
        pull_in_command = exploit.log_pull["in_command"]
        self.assertRaises(
            Exception,
            engine.construct_exploit_command,
            (
                test_data["target"],
                exploit,
                test_data["parameters_exception"],
                pull_in_command,
            ),
        )

    def test_construct_exploit_command(self):
        details = test_data["exploit"]
        exploit = Exploit(details)
        engine = Engine()
        pull_in_command = exploit.log_pull["in_command"]
        engine.check_pull_location(test_data["target"], exploit.name)
        command = engine.construct_exploit_command(
            test_data["target"], exploit, test_data["parameters"], pull_in_command
        )
        # print(command)
        self.assertListEqual(
            command,
            [
                "./bin/bt_exploiter",
                "--host-port=/dev/ttyUSB1",
                "--exploit=knob",
                "--random_bdaddress",
                "--target=AA:AA:AA:AA:AA:AA",
            ],
        )

    def test_construct_exploit_2_command(self):
        details = test_data["exploit2"]
        exploit = Exploit(details)
        engine = Engine()
        engine.check_pull_location(test_data["target"], exploit.name)
        pull_in_command = exploit.log_pull["in_command"]
        command = engine.construct_exploit_command(
            test_data["target"], exploit, test_data["parameters"], pull_in_command
        )
        print(command)
        self.assertListEqual(
            command,
            [
                "internalblue_KNOB.sh",
                "AA:AA:AA:AA:AA:AA",
                "/home/weil/Desktop/University/Thesis/data/tests/AA:AA:AA:AA:AA:AA/internalblue_knob/",
            ],
        )


class TestCheckpoint(unittest.TestCase):
    def test_preserve_state(self):
        be = BlueKit()
        av_exploits = be.get_available_exploits()
        chp = Checkpoint()
        doc = chp.preserve_state(
            exploits=av_exploits,
            done_exploits=test_data["done_exploits"],
            target=test_data["target"],
            parameters=test_data["parameters"],
        )
        self.assertDictEqual(doc, test_data["checkpoint_preserve"])

    def test_load_state(self):
        be = BlueKit()
        av_exploits = be.get_available_exploits()
        chp = Checkpoint()
        exploit_pool, exploits, target, parameters = chp.load_state(test_data["target"])


unittest.main()
