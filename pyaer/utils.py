"""Utilities Functions.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
import json
import numpy as np

import pyaer
from pyaer import log
from pyaer import libcaer

logger = log.get_logger("utils", pyaer.LOG_LEVEL)


def load_json(file_path):
    """Load JSON string.

    # Arguments
        file_path: `str`<br/>
            the absolute path to the JSON string.

    # Returns
        json_obj: `dict`<br/>
            A JSON object
    """
    try:
        json_obj = json.load(open(file_path))
        return json_obj
    except IOError:
        return None


def write_json(file_path, json_obj):
    """Write JSON string.

    # Arguments
        file_path: `str`<br/>
            the absolute path to the JSON string.
        json_obj: `dict`<br/>
            a dictionary

    # Returns
        flag : bool
            True if saved successfully
            False otherwise
    """
    try:
        with open(file_path, "w") as f:
            json.dump(json_obj, f)
            f.close()
        return True
    except IOError:
        return False


def load_dvs_bias(file_path, verbose=False):
    """Load bias for DVS128.

    # Arguments
        file_path : `str`<br/>`
            the absolute path to the JSON string.

    # Returns
        bias_obj: `dict`<br/>
            A dictionary that contains valid DVS128 bias.
    """
    bias_obj = load_json(file_path)

    if bias_obj is not None:
        if verbose:
            for key, value in bias_obj.iteritems():
                logger.debug("%s: %d" % (key, value))
        # TODO: to check validity of the bias file
        return bias_obj
    else:
        return None


def load_davis_bias(file_path, verbose=False):
    """Load DAVIS bias.

    TODO: to investigate bias differences between 240C and 346.

    # Arguments
        file_path : `str`<br/>`
            the absolute path to the JSON string.

    # Returns
        bias_obj: `dict`<br/>
            A dictionary that contains valid DAVIS bias.
    """
    bias_obj = load_json(file_path)

    if bias_obj is not None:
        if verbose:
            for key, value in bias_obj.iteritems():
                logger.debug("%s: %d" % (key, value))
        # TODO: to check validity of the bias file
        return bias_obj
    else:
        return None


def load_dynapse_bias(file_path, verbose=False):
    """Load DYNAPSE bias.

    # Arguments
        file_path: `str`<br/>`
            the absolute path to the JSON string.

    # Returns
        bias_obj: `dict`<br/>
            A dictionary that contains valid DYNAPSE bias.
    """
    bias_obj = load_json(file_path)

    if bias_obj is not None:
        if verbose:
            for key, value in bias_obj.iteritems():
                logger.debug("%s: %d" % (key, value))
        # TODO: to check validity of the bias file
        return bias_obj
    else:
        return None


def discover_devices(device_type, max_devices=100):
    """Automatic discover devices.

    # Arguments
        device_type: `int`<br/>
            * -1 - CAER_DEVICE_DISCOVER_ALL<br/>
            *  0 - CAER_DEVICE_DVS128<br/>
            *  1 - CAER_DEVICE_DAVIS_FX2<br/>
            *  2 - CAER_DEVICE_DAVIS_FX3<br/>
            *  3 - CAER_DEVICE_DYNAPSE<br/>
            *  4 - CAER_DEVICE_DAVIS<br/>
            *  5 - CAER_DEVICE_EDVS<br/>
            *  6 - CAER_DEVICE_DAVIS_RPI<br/>

    # Returns
        discovered_devices: `numpy.ndarray`<br/>
            a (num_devices, 3) array<br/>
            the first column is device type<br/>
            the second column is device USB bus number or
                                 serial port name for EDVS
                                 (cannot detect string, set to 0)<br/>
            the third column is device USB device address or
                                serial Baud rate (if EDVS)<br/>
            discovered devices type with the order
            Note that the array has the data type uint64,
            please reformat the number if necessary.
        num_devices: `int`<br/>
            number of available devices
    """
    discovered_devices = libcaer.device_discover(
        device_type, (max_devices+1)*3)

    discovered_devices = discovered_devices.reshape((max_devices+1), 3)
    num_devices = np.argwhere(discovered_devices == 42)[0][0]

    return discovered_devices[:num_devices], num_devices
