import logging
import os
from typing import Optional

# It's good practice to define the default format string as a constant.
DEFAULT_LOG_FORMAT = "[%(levelname)s] %(name)s: %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class Logger:
    def __init__(
        self, name: str, log_level: int = logging.INFO, log_file: Optional[str] = None
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.logger.propagate = False
        if not self.logger.handlers:
            formatter = logging.Formatter(
                fmt=DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT
            )

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

            if log_file:
                log_dir = os.path.dirname(log_file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)

                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

    def get(self) -> logging.Logger:
        return self.logger
