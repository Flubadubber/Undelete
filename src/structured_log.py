import datetime
import json
import logging
import uuid
from logging import Logger
from typing import Final, Dict


class StructuredLog:
    _logger: Final[Logger] = logging.getLogger(str(uuid.uuid4()))

    def __init__(self, level: str, message: str, additional_props: Dict) -> None:
        self._timestamp: Final[
            str
        ] = f"{datetime.datetime.utcnow().replace(microsecond=0).isoformat()}Z"
        self._level: Final[str] = level
        self._message: Final[str] = message
        self._additional_props: Final[Dict] = additional_props

    def __str__(self) -> str:
        return json.dumps(
            obj={
                **{
                    "timestamp": self._timestamp,
                    "level": self._level,
                    "message": self._message,
                },
                **self._additional_props,
            },
            ensure_ascii=False,
        )

    @classmethod
    def set_log_level(cls, level: int) -> None:
        cls._logger.setLevel(level=level)

    @classmethod
    def debug(cls, message: str, **kwargs) -> None:
        cls._logger.debug(
            msg=StructuredLog(level="DEBUG", message=message, additional_props=kwargs)
        )

    @classmethod
    def info(cls, message: str, **kwargs) -> None:
        cls._logger.info(
            msg=StructuredLog(level="INFO", message=message, additional_props=kwargs)
        )

    @classmethod
    def warn(cls, message: str, **kwargs) -> None:
        cls._logger.warning(
            msg=StructuredLog(level="WARN", message=message, additional_props=kwargs)
        )

    @classmethod
    def error(cls, message: str, **kwargs) -> None:
        cls._logger.error(
            msg=StructuredLog(level="ERROR", message=message, additional_props=kwargs)
        )

    @classmethod
    def critical(cls, message: str, **kwargs) -> None:
        cls._logger.critical(
            msg=StructuredLog(level="CRITICAL", message=message,
                              additional_props=kwargs)
        )
