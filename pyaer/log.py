"""Logger for PyAER.

NOTE: this is different from libcaer's logger.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
import logging

# remap logging levels for easy access
NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


def get_logger(logger_name, logger_level, stream=None):
    """Get a logger for the script.

    Using stream handler.

    # Arguments
        logger_name: `str`<br/>
            the name of the logger
        logger_level: `int`<br/>
            the minimial level that trigger the logger.
        stream: `data stream`<br/>
            if None, sys.stderr will be used.

    # Returns
        logger: `logging.Logger`<br/>
            return a logger to handel the logging in the script.
    """
    logger = logging.getLogger(name=logger_name)
    logger.setLevel(level=logger_level)

    ch = logging.StreamHandler(stream)
    ch.setLevel(level=logger_level)

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y/%m/%d %I:%M:%S %p')
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
