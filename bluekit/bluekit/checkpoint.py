import json
import logging
import os
from bluekit.constants import CHECKPOINT_PATH
from bluekit.factories.exploitfactory import ExploitFactory


class Checkpoint:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def check_if_checkpoint(self, target) -> bool:
        if os.path.isfile(CHECKPOINT_PATH.format(target=target)):
            return True
        self.logger.debug(f"No checkpoint found for target: {target}")
        return False

    # Create a checkpoint
    def preserve_state(
        self,
        exploits,
        done_exploits,
        target,
        parameters,
        exploits_to_scan,
        exclude_exploits,
    ) -> None:
        if target is None:
            return
        # why are we saving the whole exploit? we just need the name technically
        doc = {
            "exploits": [exploit.to_json() for exploit in exploits],
            "parameters": parameters,
            "done_exploits": done_exploits,
            "target": target,
            "exploits_to_scan": exploits_to_scan,
            "exclude_exploits": exclude_exploits,
        }
        checkpoint = open(CHECKPOINT_PATH.format(target=target), "w")
        json.dump(doc, checkpoint, indent=4)
        checkpoint.close()

        self.logger.debug(f"Preserving state for {target}")

    # Loading a checkpoint
    def load_state(self, target) -> None:
        checkpoint = open(
            CHECKPOINT_PATH.format(target=target),
        )
        doc = json.load(checkpoint)
        self.logger.debug(
            f"Checkpoint state loaded for {target}. {len(doc['done_exploits'])} exploits already tested."
        )

        done_exploit_names = {exploit[0] for exploit in doc["done_exploits"]}

        exploit_pool = [
            constructed_exploit
            for exploit_data in doc["exploits"]
            if (
                constructed_exploit := ExploitFactory.construct_exploit(exploit_data)
            ).name
            not in done_exploit_names
        ]
        # done_exploits_intermediate = [
        #     exploit[0] for exploit in doc["done_exploits"]
        # ]  # get exploit names

        # exploits = [
        #     ExploitFactory.construct_exploit(exploit) for exploit in doc["exploits"]
        # ]
        # exploit_pool = [
        #     exploit
        #     for exploit in exploits
        #     if exploit.name not in done_exploits_intermediate
        # ]

        return (
            exploit_pool,
            doc["done_exploits"],
            doc["parameters"],
            doc["target"],
            doc["exploits_to_scan"],
            doc["exclude_exploits"],
        )
