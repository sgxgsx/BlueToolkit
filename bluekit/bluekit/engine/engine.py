import logging
import shutil
import sys
import time
import os
import re
import psutil
import subprocess
import signal

sys.path.append("..")

from pathlib import Path

from bluekit.models.exploit import Exploit
from bluekit.constants import (
    TIMEOUT,
    OUTPUT_DIRECTORY,
    DEFAULT_CONNECTOR,
    TOOLKIT_INSTALLATION_DIRECTORY,
    TYPE_DOS,
    REGEX_EXPLOIT_OUTPUT_DATA,
)
from bluekit.constants import (
    RETURN_CODE_ERROR,
    RETURN_CODE_UNDEFINED,
    RETURN_CODE_NONE_OF_4_STATE_OBSERVED,
    RETURN_CODE_NOT_VULNERABLE,
    RETURN_CODE_VULNERABLE,
)
from bluekit.constants import (
    REGEX_EXPLOIT_OUTPUT_DATA_DATA,
    REGEX_EXPLOIT_OUTPUT_DATA_CODE,
)
from bluekit.verifyconn import dos_checker


class Engine:
    def __init__(self):
        self.logger = logging.getLogger("mylogger")
        self.logger.setLevel(logging.DEBUG)
        self.pull_location = None

    def construct_exploit_command(
        self,
        target: str,
        current_exploit: Exploit,
        parameters: list,
        pull_in_command=False,
    ) -> str:
        exploit_command = current_exploit.command.split(" ")

        parameters_dict = self.process_additional_paramters(parameters)
        parameters_list = self.get_parameters_list(parameters)

        pull_directory_not_added = True  # default pull_directory for pull_in_command=True in case directory parameter not provided

        for param in current_exploit.parameters:
            if param["name"] in parameters_list:
                logging.info(
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
                    logging.info("name required -> ")
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
                    logging.info("append")
                    exploit_command.append(self.pull_location)
                pull_directory_not_added = False
            elif param["required"]:
                self.logger.error(
                    "Parameter {} is required, but was not found in your command".format(
                        param["name"]
                    )
                )
                raise Exception(
                    "Parameter {} is required, but was not found in your command".format(
                        param["name"]
                    )
                )

        logging.info(
            "Engine.construct_exploit_command -> exploit_command list -> "
            + str(exploit_command)
        )
        logging.info(
            "Engine.construct_exploit_command -> exploit command together -> {}".format(
                " ".join(exploit_command)
            )
        )

        return exploit_command

    def run_test(self, target: str, current_exploit: Exploit, parameters: list) -> None:
        self.check_pull_location(target, current_exploit.name)

        pull_in_command = current_exploit.log_pull["in_command"]

        # Tdone ODO extract timing information and exploit type here

        exploit_command = self.construct_exploit_command(
            target, current_exploit, parameters, pull_in_command=pull_in_command
        )

        print(f"Running exploit {current_exploit.name}")

        if current_exploit.directory["change"]:
            new_directory = TOOLKIT_INSTALLATION_DIRECTORY
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

        if current_exploit.type == TYPE_DOS:
            # Possible to add a gray-box check here!!!!
            response_code, data = dos_checker(target)
        else:
            logging.info("Engine.run_test -> data " + str(data))
            response_code, data = self.process_raw_data(data, if_failed)

        if not pull_in_command:
            self.pull_information(target, current_exploit)

        return response_code, data

    def execute_command(
        self,
        target: str,
        exploit_command: list,
        exploit_name: str,
        timeout=TIMEOUT,
        change_directory=False,
        directory=None,
    ) -> tuple:
        pid = None
        if change_directory:
            os.chdir(directory)
            logging.info("Engine.execute_command -> chdir to {}".format(directory))
        else:
            os.chdir(TOOLKIT_INSTALLATION_DIRECTORY)

        data = False, b""

        try:
            self.logger.info(
                "Starting the next exploit - name {} and command {}".format(
                    exploit_name, exploit_command
                )
            )
            command = subprocess.Popen(
                " ".join(exploit_command),
                stdout=subprocess.PIPE,
                shell=True,
                preexec_fn=os.setsid,
            )  # for some reason doesn't accept tokenized exploit_command (leads to a bug)
            pid = command.pid

            logging.info(
                "Engine.execute_command -> sleeping for {} seconds".format(timeout)
            )

            new_xdata = command.wait(timeout=timeout)
            new_data = command.communicate()
            logging.info(
                "Engine.execute_command -> command.communicate " + str(new_data)
            )
            if type(new_data) is int:
                print(new_data)
            else:
                new_data = new_data[0]
            data = True, new_data
        except subprocess.TimeoutExpired as e:
            logging.info(
                "Engine.execute_command -> Killing the exploit and sleeping for another 1 second"
            )
            for child in psutil.Process(pid).children(recursive=True):
                child.kill()
            os.killpg(os.getpgid(command.pid), signal.SIGTERM)
            time.sleep(1)

        if change_directory:
            os.chdir(TOOLKIT_INSTALLATION_DIRECTORY)

        logging.info("Engine.execute_command -> data -> " + str(data))
        return data

    def execute_manual_exploit(
        self,
        target,
        exploit_command,
        exploit_name,
        timeout=TIMEOUT,
        change_directory=False,
        directory=None,
    ) -> tuple:
        pid = None
        if change_directory:
            os.chdir(directory)
            logging.info("Engine.execute_command -> chdir to {}".format(directory))
        else:
            os.chdir(TOOLKIT_INSTALLATION_DIRECTORY)

        data = False, b""

        try:
            self.logger.info(
                "Starting the next exploit - name {} and command {}".format(
                    exploit_name, exploit_command
                )
            )
            command = subprocess.Popen(
                " ".join(exploit_command),
                stdout=subprocess.PIPE,
                shell=True,
                preexec_fn=os.setsid,
            )  # for some reason doesn't accept tokenized exploit_command (leads to a bug)
            pid = command.pid

            logging.info(
                "Engine.execute_command -> sleeping for {} seconds".format(timeout)
            )

            new_data = command.communicate()[0]
            logging.info(
                "Engine.execute_command -> command.communicate " + str(new_data)
            )
            data = True, new_data
        except subprocess.TimeoutExpired as e:
            logging.info(
                "Engine.execute_command -> Killing the exploit and sleeping for another 1 second"
            )
            for child in psutil.Process(pid).children(recursive=True):
                child.kill()
            os.killpg(os.getpgid(command.pid), signal.SIGTERM)
            time.sleep(1)

        if change_directory:
            os.chdir(TOOLKIT_INSTALLATION_DIRECTORY)

        logging.info("Engine.execute_command -> data -> " + str(data))
        return data

    def process_raw_data(self, data, if_failed):
        # INEFFICIENTLY processes data line by line (there is room for improvement)
        try:
            # TODO: if data is empty, return error directly
            mm = re.compile(REGEX_EXPLOIT_OUTPUT_DATA)
            output = mm.search(data).group()
            print(output)
            logging.info(
                "Engine.process_raw_data -> Found data from the exploit {}".format(
                    output
                )
            )

            mm2 = re.compile(REGEX_EXPLOIT_OUTPUT_DATA_CODE)
            mm3 = re.compile(REGEX_EXPLOIT_OUTPUT_DATA_DATA)

            output2 = int(mm2.search(output).group().rstrip(b",").split(b"=")[1])
            logging.info(
                "Engine.process_raw_data -> Found data from the exploit, code -> {}".format(
                    output2
                )
            )
            output3 = (mm3.search(output).group().split(b"=")[1]).decode()
            logging.info(
                "Engine.process_raw_data -> Found data from the exploit, data -> {}".format(
                    output3
                )
            )

            return int(output2), output3
        except Exception as e:
            logging.info(
                "Engine.process_raw_data -> Error during extracting information from the regex "
                + str(e)
            )
            return (
                RETURN_CODE_NONE_OF_4_STATE_OBSERVED,
                "Error during extracting information from the regex",
            )

    def pull_information(self, target, current_exploit: Exploit) -> None:
        # Basically copy from 1 directory to another one
        if self.pull_location is None:
            self.check_pull_location(target, current_exploit.name)

        if current_exploit.log_pull["from_directory"]:
            directory = TOOLKIT_INSTALLATION_DIRECTORY
            if current_exploit.log_pull["relative_directory"]:
                pull_dir = current_exploit.log_pull["pull_directory"]
                if not pull_dir.startswith("/"):
                    directory += "/"
                directory = directory + pull_dir
            else:
                directory = current_exploit.log_pull["pull_directory"]

            shutil.copytree(directory, self.pull_location, dirs_exist_ok=True)
        else:
            self.logger.info("from_directory: false, is not yet implemented")
            return
            raise Exception("from_directory: false, is not yet implemented")

    def pull_information_from_file(self, target, current_exploit: Exploit) -> None:
        if self.pull_location is None:
            self.check_pull_location(target, current_exploit.name)

    def process_additional_paramters(self, parameters: list) -> dict:
        logging.info(
            "Engine.process_additional_paramters -> list parameters " + str(parameters)
        )
        param_dict = {}
        for i in range(0, len(parameters), 2):
            param_dict[parameters[i]] = parameters[i + 1]
        return param_dict

    def get_parameters_list(self, parameters: list) -> list:
        return [parameters[i] for i in range(0, len(parameters), 2)]

    def check_pull_location(self, target, current_exploit_name):
        self.pull_location = OUTPUT_DIRECTORY.format(
            target=target, exploit=current_exploit_name
        )
        Path(self.pull_location).mkdir(parents=True, exist_ok=True)
