import json
import logging
import shutil
from tabulate import tabulate
from colorama import Fore, Style
import os


from bluekit.constants import (
    TARGET_DIR,
    REPORT_OUTPUT_FILE,
    SKIP_DIRECTORIES,
    MAX_CHARS_DATA_TRUNCATION,
    OUTPUT_DIR,
    FULL_REPORT_OUTPUT_FILE,
    ReturnCode,
)

from bluekit.factories.exploitfactory import ExploitFactory


def report_data(code, data):
    # logging.info(f"return_code={code}, return_data={data}")
    data = {"return_code": code, "return_data": data}
    print(f"{data}")


def report_not_vulnerable(data):
    report_data(ReturnCode.NOT_VULNERABLE, data)


def report_vulnerable(data):
    report_data(ReturnCode.VULNERABLE, data)


def report_none_of_4_state_observed(data):
    report_data(ReturnCode.UNKNOWN_STATE, data)


def report_error(data):
    report_data(ReturnCode.ERROR, data)


def report_undefined(data):
    report_data(ReturnCode.UNDEFINED, data)


class Report:
    def __init__(self, exploit_factory: ExploitFactory = None):
        self.exploitFactory = exploit_factory or ExploitFactory()
        self.logger = logging.getLogger(self.__class__.__name__)

    def save_data(self, exploit_name, target, data, code):
        doc = {"code": code, "data": data}
        filename = REPORT_OUTPUT_FILE.format(target=target, exploit=exploit_name)
        self.logger.debug(f"Saving report to {filename}")

        jsonfile = open(filename, "w")

        json.dump(doc, jsonfile, indent=4)
        jsonfile.close()

    def read_data(self, exploit_name, target):
        filename = REPORT_OUTPUT_FILE.format(target=target, exploit=exploit_name)
        if os.path.isfile(filename):
            self.logger.debug(f"Loading report {filename}")

            jsonfile = open(
                filename,
            )
            doc = json.load(jsonfile)
            return doc["code"], doc["data"]
        return None, None

    def get_done_exploits(self, target):
        exploits = [
            entry.name
            for entry in os.scandir(TARGET_DIR.format(target=target))
            if entry.is_dir() and entry.name not in SKIP_DIRECTORIES
        ]
        return exploits

    def generate_report(self, target):
        done_exploits = self.get_done_exploits(target=target)
        all_exploits = self.exploitFactory.get_exploits()
        skipped_exploits = [
            exploit.name
            for exploit in all_exploits
            if exploit.name not in done_exploits
        ]

        # self.logger.info(f"Tested exploits: {done_exploits}")
        # self.logger.info(f"All exploits {all_exploits}")
        # self.logger.info(f"Skipped exploits {skipped_exploits}")

        headers = ["Index", "Exploit", "Result", "Data"]
        table_data = []
        for idx, exploit in enumerate(all_exploits):
            if exploit.name in skipped_exploits:
                table_data.append(
                    [
                        idx + 1,
                        f"{Fore.WHITE}{exploit.name}{Style.RESET_ALL}",
                        f"{Fore.WHITE}Not tested{Style.RESET_ALL}",
                        "",
                    ]
                )
                continue

            code, data = self.read_data(exploit_name=exploit.name, target=target)

            if code is None:
                code = ReturnCode.UNKNOWN_STATE
                data = "Error during loading the report"
            if data is None:
                data = "Error with data"
            symbol = ""
            if code == ReturnCode.VULNERABLE:
                symbol = "❗"
            elif code == ReturnCode.ERROR or code == ReturnCode.UNKNOWN_STATE:
                symbol = "⚠️"

            if code == ReturnCode.VULNERABLE:
                table_data.append(
                    [
                        idx + 1,
                        f"{Fore.RED}{exploit.name}{Style.RESET_ALL}",
                        f"{Fore.RED}Vulnerable{symbol}{Style.RESET_ALL}",
                        data[:MAX_CHARS_DATA_TRUNCATION],
                    ]
                )
            elif code == ReturnCode.NOT_VULNERABLE:
                table_data.append(
                    [
                        idx + 1,
                        f"{Fore.GREEN}{exploit.name}{Style.RESET_ALL}",
                        f"{Fore.GREEN}Not vulnerable{symbol}{Style.RESET_ALL}",
                        data[:MAX_CHARS_DATA_TRUNCATION],
                    ]
                )
            elif code == ReturnCode.ERROR:
                table_data.append(
                    [
                        idx + 1,
                        f"{Fore.CYAN}{exploit.name}{Style.RESET_ALL}",
                        f"{Fore.CYAN}Error{symbol}{Style.RESET_ALL}",
                        data[:MAX_CHARS_DATA_TRUNCATION],
                    ]
                )
            elif code == ReturnCode.UNDEFINED:
                table_data.append(
                    [
                        idx + 1,
                        f"{Fore.WHITE}{exploit.name}{Style.RESET_ALL}",
                        f"{Fore.WHITE}Undefined{symbol}{Style.RESET_ALL}",
                        data[:MAX_CHARS_DATA_TRUNCATION],
                    ]
                )
            elif code == ReturnCode.UNKNOWN_STATE:
                table_data.append(
                    [
                        idx + 1,
                        f"{Fore.WHITE}{exploit.name}{Style.RESET_ALL}",
                        f"{Fore.WHITE}Toolkit error{symbol}{Style.RESET_ALL}",
                        data[:MAX_CHARS_DATA_TRUNCATION],
                    ]
                )
            else:
                table_data.append(
                    [
                        idx + 1,
                        f"{Fore.WHITE}{exploit.name}{Style.RESET_ALL}",
                        f"{Fore.WHITE}Toolkit error during report generation{symbol}{Style.RESET_ALL}",
                        data[:MAX_CHARS_DATA_TRUNCATION],
                    ]
                )

        # for skipped_exploit in skipped_exploits:
        #     table_data.append(
        #         [
        #             index,
        #             f"{Fore.WHITE}{skipped_exploit}{Style.RESET_ALL}",
        #             f"{Fore.WHITE}Not tested{Style.RESET_ALL}",
        #             "",
        #         ]
        #     )
        #     index += 1

        self.logger.debug(f"Report table\n{table_data}")

        table = tabulate(
            table_data,
            headers,
            tablefmt="pretty",
            colalign=("center", "left", "left", "left"),
        )

        return table

    def get_manufacturer(self, target) -> str:
        file = os.path.join(
            OUTPUT_DIR.format(target=target, exploit="recon"), "recon.json"
        )
        if os.path.isfile(file):
            with open(file, "r") as f:
                data = json.load(f)
                return data["vendor"]

    def get_bt_version(self, target) -> float:
        file = os.path.join(
            OUTPUT_DIR.format(target=target, exploit="recon"), "recon.json"
        )
        if os.path.isfile(file):
            with open(file, "r") as f:
                data = json.load(f)
                return data["version"]

    def generate_machine_readable_report(self, target: str, directory: str):
        done_exploits = self.get_done_exploits(target=target).sort(key=lambda x: x[2])
        all_exploits = self.exploitFactory.get_exploits()
        skipped_exploits = [
            exploit.name
            for exploit in all_exploits
            if exploit.name not in done_exploits
        ]

        self.logger.debug(f"Tested exploits: {done_exploits}")
        self.logger.debug(f"Available exploits: {all_exploits}")
        self.logger.debug(f"Skipped exploits: {skipped_exploits}")

        index = 1
        # done_exploits.sort(key=lambda x: x[2])

        output_json = {}
        done_exploits_json = []
        skipped_exploits_json = []
        for exploit in done_exploits:
            code, data = self.read_data(exploit_name=exploit, target=target)
            done_exploits_json.append(
                {
                    "index": index,
                    "name": exploit,
                    "code": code if code is not None else ReturnCode.UNKNOWN_STATE,
                    "data": data if code is not None else "Error with data",
                }
            )
            index += 1
        for skipped_exploit in skipped_exploits:
            skipped_exploits_json.append(
                {
                    "index": index,
                    "name": skipped_exploit,
                    "code": ReturnCode.SKIPPED,
                    "data": "Not tested",
                }
            )
            index += 1

        output_json["done_exploits"] = done_exploits_json
        output_json["skipped_exploits"] = skipped_exploits_json
        output_json["manually_added_exploits"] = list()
        output_json["bt_version"] = self.get_bt_version(target=target)
        output_json["manufacturer"] = self.get_manufacturer(target=target)
        output_json["mac_address"] = target
        output_json["vehicle_name"] = ""
        output_json["vehicle manufacturer"] = ""
        output_json["parent_company"] = ""
        output_json["year_manufactured"] = 1

        # Save the report in the default location
        source_file = FULL_REPORT_OUTPUT_FILE.format(target=target)
        jsonfile = open(source_file, "w")
        json.dump(output_json, jsonfile, indent=4)
        jsonfile.close()

        # Verify the file was created
        if not os.path.isfile(source_file):
            self.logger.error(f"Failed to create report at {source_file}")
            return

        self.logger.debug(f"Report saved at {source_file}")

        # Copy the report to current directory with MAC address in filename

        # Get the original directory from BlueKit instance
        dest_file = os.path.join(directory, f"{target}_report.json")
        try:
            shutil.copy2(source_file, dest_file)
            # Allow non-root users to read the file
            os.chmod(dest_file, 0o664)
            self.logger.debug(f"Successfully saved report to {dest_file}")
        except Exception as e:
            self.logger.error(f"Error copying report to current directory: {str(e)}")
