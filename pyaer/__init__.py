"""Properly init the package.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
import os

from pyaer import log
from pyaer.__about__ import __version__
from pyaer.__about__ import __author__

FILE_PATH = os.path.realpath(__file__)
CURR_PATH = os.path.dirname(os.path.realpath(__file__))
PKG_PATH = os.path.dirname(CURR_PATH)

# System logging level
LOG_LEVEL = log.DEBUG

try:
    from pyaer import libcaer_wrap as libcaer
except ImportError:
    raise ImportError("libcaer might not be in the LD_LIBRARY_PATH "
                      "or your numpy might not be the required version."
                      "Try to load _libcaer_wrap.so from the package "
                      "directory, this will provide more information.")
