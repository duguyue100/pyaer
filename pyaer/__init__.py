"""Properly init the package.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function
import os

FILE_PATH = os.path.realpath(__file__)
CURR_PATH = os.path.dirname(os.path.realpath(__file__))
PKG_PATH = os.path.dirname(CURR_PATH)
LIBCAER_PATH = os.path.join(PKG_PATH, "libcaer", "build")
LIBCAER_INCLUDE_PATH = os.path.join(PKG_PATH, "include")
LIBCAER_LIB_PATH = os.path.join(PKG_PATH, "lib")

try:
    import libcaer_wrap
except ImportError:
    raise ImportError("libcaer is not in the LD_LIBRARAY_PATH")
