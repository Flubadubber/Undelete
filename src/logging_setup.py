import logging

from src.structured_log import StructuredLog


class LoggingSetup:
    @staticmethod
    def setup(level: int) -> None:
        logging.basicConfig(format="%(message)s")
        StructuredLog.set_log_level(level=level)
