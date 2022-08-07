"""Logger for PyAER.

NOTE: this is different from libcaer's logger.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
import logging
from logging import Logger
from typing import Optional
from typing import TextIO

# Remaps logging levels for easy access.
NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


def get_logger(
    logger_name: Optional[str], logger_level: int, stream: Optional[TextIO] = None
) -> Logger:
    """Gets a logger for the script.

    Args:
        logger_name: the name of the logger.
        logger_level: the minimal level that trigger the logger.
        stream: If None, sys.stderr will be used.

    Returns:
        A logger to handel the logging in the script.
    """
    logger = logging.getLogger(name=logger_name)
    logger.setLevel(level=logger_level)

    ch = logging.StreamHandler(stream)
    ch.setLevel(level=logger_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y/%m/%d %I:%M:%S %p",
    )
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
