import ast
import json
import logging
import shutil
import sys
import time
import os
import re
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

    def construct_exploit_command(
        self,
        target: str,
        current_exploit: Exploit,
        parameters: list,
        pull_in_command=False,
    ) -> str:
        exploit_command = current_exploit.command.strip().split(" ")

        parameters_dict = self.process_additional_paramters(parameters)
        parameters_list = self.get_parameters_list(parameters)

        pull_directory_not_added = True  # default pull_directory for pull_in_command=True in case directory parameter not provided
        for param in current_exploit.parameters:
            if param["name"] in parameters_list:
                self.logger.info(
                    f"Engine.construct_exploit_command -> parameter_name in parameter_List {param}"
                )

                """
                if pull_in_command and param['name'] == current_exploit.log_pull['pull_parameter']:                    # Additional complexity as an unnecessary, but simple and fast "hack"
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
                pull_in_command
                and param["name"] == current_exploit.log_pull["pull_parameter"]
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

        self.logger.info(f"Exploit command -> {' '.join(exploit_command)}")

        return exploit_command

    def run_test(self, target: str, current_exploit: Exploit, parameters: list) -> None:
        self.check_pull_location(target, current_exploit.name)

        pull_in_command = current_exploit.log_pull["in_command"]

        # Tdone ODO extract timing information and exploit type here

        exploit_command = self.construct_exploit_command(
            target, current_exploit, parameters, pull_in_command=pull_in_command
        )

        self.logger.info(f"Testing {current_exploit.name}")

        if current_exploit.directory["change"]:
            new_directory = TOOLKIT_INSTALL_DIR
            if not current_exploit.directory["directory"].startswith("/"):
                new_directory += "/"
            new_directory += current_exploit.directory["directory"]

            if_failed, data = self.execute_command(
                target,
                exploit_command,
                current_exploit.name,
                timeout=current_exploit.max_timeout,
                change_directory=True,
                directory=new_directory,
            )
        else:
            if_failed, data = self.execute_command(
                target,
                exploit_command,
                current_exploit.name,
                timeout=current_exploit.max_timeout,
            )

        if current_exploit.type == ExploitType.DOS:
            # TODO: possible gray-box check here if we have access to the target device
            response_code, data = dos_checker(target)
        else:
            # TODO: modify data to optimize processing
            self.logger.debug(f"Result data: {data}")
            response_code, data = self.process_raw_data(data, if_failed)

        if not pull_in_command:
            self.pull_information(target, current_exploit)

        return response_code, data

    def execute_command(
        self,
        target: str,
        exploit_command: list,
        exploit_name: str,
        timeout=ConnVerifier.TIMEOUT,
        change_directory=False,
        directory=None,
    ) -> tuple:
        if change_directory:
            os.chdir(directory)
            self.logger.debug(f"Moving workdir to {directory}")
        else:
            os.chdir(TOOLKIT_INSTALL_DIR)

        command = None
        try:
            command = subprocess.Popen(
                exploit_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
            )

            # TODO: these are set to DEBUG by default
            self.logger.info(f"Executing {exploit_command} with timeout {timeout}")
            stdout, stderr = command.communicate(timeout=timeout)

            self.logger.info(f"Command output: {stdout.strip()}")
            # TODO: if the stderr is not empty I want to report it in the report maybe ?
            self.logger.info(f"Command error: {stderr}")

            data = True, stdout
        except Exception as e:
            self.logger.warning(f"{e}")
            # for child in psutil.Process(pid).children(recursive=True):
            #     child.kill()
            os.killpg(os.getpgid(command.pid), signal.SIGTERM)
            time.sleep(1)
            data = False, b""

        returncode = command.returncode if command else -1

        if change_directory:
            os.chdir(TOOLKIT_INSTALL_DIR)

        self.logger.debug(f"Command result: {data}")
        return data

    # def execute_manual_exploit(
    #     self,
    #     target,
    #     exploit_command,
    #     exploit_name,
    #     timeout=ConnVerifier.TIMEOUT,
    #     change_directory=False,
    #     directory=None,
    # ) -> tuple:
    #     pid = None
    #     if change_directory:
    #         os.chdir(directory)
    #         self.logger.info("Engine.execute_command -> chdir to {}".format(directory))
    #     else:
    #         os.chdir(TOOLKIT_INSTALL_DIR)

    #     data = False, b""

    #     try:
    #         self.logger.info(
    #             "Starting the next exploit - name {} and command {}".format(
    #                 exploit_name, exploit_command
    #             )
    #         )
    #         command = subprocess.Popen(
    #             " ".join(exploit_command),
    #             stdout=subprocess.PIPE,
    #             shell=True,
    #             preexec_fn=os.setsid,
    #         )  # for some reason doesn't accept tokenized exploit_command (leads to a bug)
    #         pid = command.pid

    #         self.logger.info(
    #             "Engine.execute_command -> sleeping for {} seconds".format(timeout)
    #         )

    #         new_data = command.communicate()[0]
    #         self.logger.info(
    #             "Engine.execute_command -> command.communicate " + str(new_data)
    #         )
    #         data = True, new_data
    #     except subprocess.TimeoutExpired as e:
    #         self.logger.info(
    #             "Engine.execute_command -> Killing the exploit and sleeping for another 1 second"
    #         )
    #         for child in psutil.Process(pid).children(recursive=True):
    #             child.kill()
    #         os.killpg(os.getpgid(command.pid), signal.SIGTERM)
    #         time.sleep(1)

    #     if change_directory:
    #         os.chdir(TOOLKIT_INSTALL_DIR)

    #     self.logger.info("Engine.execute_command -> data -> " + str(data))
    #     return data

    def process_raw_data(self, data, if_failed):
        return_code = ReturnCode.UNKNOWN_STATE
        output_data = ""

        try:
            # TODO: if data is empty, return error directly
            if not data:
                parsed_data = {}
            else:
                pyobj = ast.literal_eval(data.strip().decode("utf-8"))
                if isinstance(pyobj, dict):
                    parsed_data = json.loads(json.dumps(pyobj))

            return_code = parsed_data.get("return_code", ReturnCode.UNKNOWN_STATE)
            output_data = parsed_data.get("output_data", "")

        except Exception as e:
            self.logger.error(f"Error processing the raw output: {e}")
            output_data = "Error processing the raw output"

        return return_code, output_data

    def pull_information(self, target, current_exploit: Exploit) -> None:
        # Basically copy from 1 directory to another one
        if self.pull_location is None:
            self.check_pull_location(target, current_exploit.name)

        if current_exploit.log_pull["from_directory"]:
            directory = TOOLKIT_INSTALL_DIR
            if current_exploit.log_pull["relative_directory"]:
                pull_dir = current_exploit.log_pull["pull_directory"]
                if not pull_dir.startswith("/"):
                    directory += "/"
                directory = directory + pull_dir
            else:
                directory = current_exploit.log_pull["pull_directory"]

            shutil.copytree(directory, self.pull_location, dirs_exist_ok=True)
        else:
            self.logger.debug("from_directory: is not yet implemented")
            return
            raise Exception("from_directory: false, is not yet implemented")

    def pull_information_from_file(self, target, current_exploit: Exploit) -> None:
        if self.pull_location is None:
            self.check_pull_location(target, current_exploit.name)

    def process_additional_paramters(self, parameters: list) -> dict:
        self.logger.debug(f"Process additional parameters: {parameters}")
        return {parameters[i]: parameters[i + 1] for i in range(0, len(parameters), 2)}

    def get_parameters_list(self, parameters: list) -> list:
        return [parameters[i] for i in range(0, len(parameters), 2)]

    def check_pull_location(self, target, current_exploit_name):
        self.pull_location = OUTPUT_DIR.format(
            target=target, exploit=current_exploit_name
        )
        Path(self.pull_location).mkdir(parents=True, exist_ok=True)
