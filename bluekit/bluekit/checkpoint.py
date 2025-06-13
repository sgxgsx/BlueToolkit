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
        json.dump(doc, checkpoint, indent=6)
        checkpoint.close()
        return doc

    # Loading a checkpoint
    def load_state(self, target) -> None:
        logging.info("Loading checkpoint state")
        checkpoint = open(
            CHECKPOINT_PATH.format(target=target),
        )
        doc = json.load(checkpoint)
        logging.info("Checkpoint state loaded")
        logging.info(
            "Checkpoint - load_state -> document done_exploits -> "
            + str(doc["done_exploits"])
        )
        done_exploits_intermediate = [
            exploit[0] for exploit in doc["done_exploits"]
        ]  # get exploit names

        exploits = [
            ExploitFactory.construct_exploit(exploit) for exploit in doc["exploits"]
        ]
        exploit_pool = [
            exploit
            for exploit in exploits
            if exploit.name not in done_exploits_intermediate
        ]

        return (
            exploit_pool,
            doc["done_exploits"],
            doc["parameters"],
            doc["target"],
            doc["exploits_to_scan"],
            doc["exclude_exploits"],
        )
