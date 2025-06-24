import ast
import json
import logging
import shutil
import sys
import threading
import time
import os
import re
from typing import IO
import psutil
import subprocess
import signal

from bluekit.logger import Logger

sys.path.append("..")

from pathlib import Path

from bluekit.models.exploit import Exploit
from bluekit.constants import (
    ConnVerifier,
    OUTPUT_DIR,
    DEFAULT_CONNECTOR,
    TOOLKIT_INSTALL_DIR,
    REGEX_EXPLOIT_OUTPUT_DATA,
)
from bluekit.constants import ReturnCode, ExploitType
from bluekit.constants import (
    REGEX_EXPLOIT_OUTPUT_DATA_DATA,
    REGEX_EXPLOIT_OUTPUT_DATA_CODE,
)
from bluekit.verifyconn import dos_checker


class Engine:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pull_location = None

    def build_exploit_command(
        self,
        target: str,
        exploit: Exploit,
        parameters: list,
        pull_in_command=False,
    ) -> str:
        exploit_command = exploit.command.strip().split(" ")

        parameters_dict = self.process_additional_paramters(parameters)
        parameters_list = self.get_parameters_list(parameters)

        pull_directory_not_added = True  # default pull_directory for pull_in_command=True in case directory parameter not provided
        for param in exploit.parameters:
            if param["name"] in parameters_list:
                self.logger.info(
                    f"Engine.construct_exploit_command -> parameter_name in parameter_List {param}"
                )

                """
                if pull_in_command and param['name'] == exploit.log_pull['pull_parameter']:                    # Additional complexity as an unnecessary, but simple and fast "hack"
                    if param['name_required']:
                        if param['parameter_connector'] != DEFAULT_CONNECTOR:
                            exploit_command.append(param['name'] + param['parameter_connector'] + self.pull_location)
                        else:
                            exploit_command.append(param['name'])
                            exploit_command.append(self.pull_location)
                    else:
                        exploit_command.append(self.pull_location)
                else:
                """
                if param["name_required"]:
                    if param["parameter_connector"] != DEFAULT_CONNECTOR:
                        exploit_command.append(
                            param["name"]
                            + param["parameter_connector"]
                            + parameters_dict[param["name"]]
                        )
                    else:
                        exploit_command.append(param["name"])
                        exploit_command.append(parameters_dict[param["name"]])
                else:
                    exploit_command.append(parameters_dict[param["name"]])
                parameters_list.remove(param["name"])
                parameters_dict.pop(param["name"])
            elif param["is_target_param"]:
                if param["name_required"]:
                    if param["parameter_connector"] != DEFAULT_CONNECTOR:
                        exploit_command.append(
                            param["name"] + param["parameter_connector"] + target
                        )
                    else:
                        exploit_command.append(param["name"])
                        exploit_command.append(target)
                else:
                    exploit_command.append(target)
            elif (
                pull_in_command and param["name"] == exploit.log_pull["pull_parameter"]
            ):
                if param["name_required"]:
                    self.logger.info("name required -> ")
                    if param["parameter_connector"] != DEFAULT_CONNECTOR:
                        exploit_command.append(
                            param["name"]
                            + param["parameter_connector"]
                            + self.pull_location
                        )
                    else:
                        exploit_command.append(param["name"])
                        exploit_command.append(self.pull_location)
                else:
                    self.logger.info("append")
                    exploit_command.append(self.pull_location)
                pull_directory_not_added = False
            elif param["required"]:
                self.logger.error(
                    f"Parameter {param['name']} is required, but was not found in your command"
                )

                raise Exception(
                    f"Parameter {param['name']} is required, but was not found in your command"
                )

        return exploit_command

    def run_test(self, target: str, exploit: Exploit, parameters: list) -> tuple:
        self.check_pull_location(target, exploit.name)

        pull_in_command = exploit.log_pull["in_command"]

        exploit_command = self.build_exploit_command(
            target, exploit, parameters, pull_in_command=pull_in_command
        )

        self.logger.info(f"Testing {exploit.name}")

        new_directory = None

        if exploit.directory["change"]:
            new_directory = TOOLKIT_INSTALL_DIR
            new_directory += "/" if exploit.directory["directory"][0] != "/" else ""
            new_directory += exploit.directory["directory"]

        data = self.execute_command(
            exploit_command,
            timeout=exploit.max_timeout,
            directory=new_directory,
        )

        if exploit.type == ExploitType.DOS:
            # TODO: possible gray-box check here if we have access to the target device
            response_code, data = dos_checker(target)
        else:
            # TODO: modify data to optimize processing
            response_code, data = self.process_raw_data(data, exploit.name)
            self.logger.info(f"Result data: {data}")

        if not pull_in_command:
            self.pull_information(target, exploit)

        return response_code, data

    def read_output_to_list(self, pipe: IO[str], output_list):
        try:
            for line in iter(pipe.readline, ""):
                output_list.append(line.strip())
        except ValueError as _:
            # Ignore errors
            pass

        pipe.close()

    def execute_command(
        self,
        exploit_command: list,
        timeout: int = ConnVerifier.TIMEOUT,
        directory: str = None,
    ) -> str:
        if directory is not None:
            os.chdir(directory)
        else:
            os.chdir(TOOLKIT_INSTALL_DIR)

        command = None
        stdout_lines = []
        try:
            command = subprocess.Popen(
                exploit_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
                text=True,  # Decode stdout/stderr as text automatically
                bufsize=1,
            )

            stdout_thread = threading.Thread(
                target=self.read_output_to_list, args=(command.stdout, stdout_lines)
            )
            # stderr_thread = threading.Thread(
            #     target=self.read_output_to_list, args=(command.stderr, stderr_lines)
            # )

            stdout_thread.start()
            # stderr_thread.start()

            # TODO: these are set to DEBUG by default
            # self.logger.info(f"Executing {exploit_command} with timeout {timeout}")
            _ = command.wait(timeout=timeout)
            # Not using return code for now

        except Exception as e:
            self.logger.warning(f"{e}")
            os.killpg(os.getpgid(command.pid), signal.SIGKILL)
            time.sleep(1)

        # # TODO: if the stderr is not empty I want to report it in the report maybe ?

        if directory is not None:
            os.chdir(TOOLKIT_INSTALL_DIR)

        return "".join(stdout_lines)

    def process_raw_data(self, data, exploit_name: str) -> tuple:
        return_code = ReturnCode.UNKNOWN_STATE
        output_data = ""
        parsed_data = {}

        # Ideally an exploit should terminate with a JSON string such as
        # {"return_code": code, "return_data": "data"}
        # If not, we need to have a fallback mechanism to process the output

        try:
            # TODO: if data is empty, return error directly
            if data:
                pyobj = ast.literal_eval(data)
                if isinstance(pyobj, dict):
                    parsed_data = json.loads(json.dumps(pyobj))

        except Exception as _:
            # self.logger.error(f"Error processing the raw output: {e}")
            parsed_data = self.process_custom_output(data, exploit_name)

        return_code = parsed_data.get("return_code", ReturnCode.UNKNOWN_STATE)
        output_data = parsed_data.get("return_data", "")

        return return_code, output_data

    def pull_information(self, target, exploit: Exploit) -> None:
        # Basically copy from 1 directory to another one
        if self.pull_location is None:
            self.check_pull_location(target, exploit.name)

        if exploit.log_pull["from_directory"]:
            directory = TOOLKIT_INSTALL_DIR
            if exploit.log_pull["relative_directory"]:
                pull_dir = exploit.log_pull["pull_directory"]
                if not pull_dir.startswith("/"):
                    directory += "/"
                directory = directory + pull_dir
            else:
                directory = exploit.log_pull["pull_directory"]

            shutil.copytree(directory, self.pull_location, dirs_exist_ok=True)
        else:
            self.logger.debug("pull from_directory is not yet implemented")
            return

    def pull_information_from_file(self, target, exploit: Exploit) -> None:
        if self.pull_location is None:
            self.check_pull_location(target, exploit.name)

    def process_additional_paramters(self, parameters: list) -> dict:
        self.logger.debug(f"Process additional parameters: {parameters}")
        return {parameters[i]: parameters[i + 1] for i in range(0, len(parameters), 2)}

    def get_parameters_list(self, parameters: list) -> list:
        return [parameters[i] for i in range(0, len(parameters), 2)]

    def check_pull_location(self, target: str, exploit_name: str) -> None:
        self.pull_location = OUTPUT_DIR.format(target=target, exploit=exploit_name)
        Path(self.pull_location).mkdir(parents=True, exist_ok=True)

    def process_custom_output(self, data, exploit_name) -> None:
        """
        Process custom output from the exploit command.
        This is a placeholder for any specific processing logic needed for custom outputs.
        """
        # TODO: this could be made dynamic with the vulnerability conditions inside the exploit yaml
        if "braktooth" in exploit_name:
            # Custom processing logic for Braktooth
            if "Device vulnerable" in data:
                return {
                    "return_code": ReturnCode.VULNERABLE,
                    "return_data": "Device is vulnerable.",
                }
            else:
                return {
                    "return_code": ReturnCode.NOT_VULNERABLE,
                    "return_data": "Device is not vulnerable.",
                }
        else:
            # Fallback processing for other exploits
            self.logger.warning(
                f"Custom output processing not implemented for {exploit_name}"
            )
            return {
                "return_code": ReturnCode.UNKNOWN_STATE,
                "return_data": "",
            }
