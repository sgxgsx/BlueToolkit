import json
import logging
from pathlib import Path
from bluekit.constants import CHECKPOINT_PATH
from bluekit.factories.exploitfactory import ExploitFactory


class Checkpoint:
    def check_if_checkpoint(self, target) -> bool:
        checkpoint = Path(CHECKPOINT_PATH.format(target=target))
        if checkpoint.is_file():
            logging.info("Checkpoint file exists")
            return True
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
        logging.debug("Checkpoint - preserve_state -> document -> " + str(doc))
        checkpoint = open(CHECKPOINT_PATH.format(target=target), "w")
        json.dump(doc, checkpoint, indent=4)
        checkpoint.close()

    # Loading a checkpoint
    def load_state(self, target) -> None:
        logging.info("Loading checkpoint state")
        checkpoint = open(
            CHECKPOINT_PATH.format(target=target),
        )
        doc = json.load(checkpoint)
        logging.info("Checkpoint state loaded")
        logging.info(
            f"Checkpoint - load_state -> document done_exploits -> {doc['done_exploits']}"
        )

        done_exploit_names = {exploit[0] for exploit in doc["done_exploits"]}

        exploit_pool = [
            constructed_exploit
            for exploit_data in doc["exploits"]
            if (constructed_exploit := ExploitFactory.construct_exploit(exploit_data)).name not in done_exploit_names
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
