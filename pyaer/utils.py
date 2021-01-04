"""Utilities Functions.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
import os
from collections import OrderedDict
import json
import yaml
import time
import importlib.util as imutil
import numpy as np

import pyaer
from pyaer import log
from pyaer import libcaer

logger = log.get_logger("utils", pyaer.LOG_LEVEL)


def get_nanotime():
    return str(int(time.time()*1e9)).encode("utf-8")


def import_custom_module(custom_file, custom_class):
    """Load custom module by file path.

    # Arguments
        custom_file: str
            absolute file path to the custom module file.
        custom_class: str
            the class name to import that is in the custom_file
    """
    module_name = os.path.basename(custom_file).split(".")[0]
    spec = imutil.spec_from_file_location(module_name, custom_file)
    custom_pub = imutil.module_from_spec(spec)
    spec.loader.exec_module(custom_pub)

    return getattr(custom_pub, custom_class)


def parse_type(custom_str):
    """Parse custom string to its corresponding type."""

    # check integer
    try:
        return int(custom_str)
    except ValueError:
        pass

    # check float
    try:
        return float(custom_str)
    except ValueError:
        pass

    # check boolean
    if custom_str in ["True", "False"]:
        return custom_str == "True"

    # Return string
    return custom_str


def parse_custom_args(custom_args):
    """Parse custom arguments.

    NOTE: DO NOT USE "-" IN YOUR CUSTOM ARGUMENTS

    # Arguments
        custom_args: list
            the custom args supplied by parse_known_args()
            function

    # Returns
        custom_args_dict: dict
            a dictionary that contains formatted custom args.
    """
    # empty list
    if len(custom_args) == 0:
        return {}

    custom_args_dict = dict(
        zip([opt.replace("-", "") for opt in custom_args[::2]],
            [parse_type(val) for val in custom_args[1::2]]))

    return custom_args_dict


def ordered_yml_load(stream, Loader=yaml.SafeLoader,
                     object_pairs_hook=OrderedDict):
    """Load YAML configs in order."""
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)

    return yaml.load(stream, OrderedLoader)


def ordered_yml_dump(data, stream=None, Dumper=yaml.SafeDumper, **kwds):
    """Dump YAML configs in order."""
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def expandpath(path):
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


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


def load_dvxplorer_bias(file_path, verbose=False):
    """Load DVXPLORER bias.

    # Arguments
        file_path : `str`<br/>`
            the absolute path to the JSON string.

    # Returns
        bias_obj: `dict`<br/>
            A dictionary that contains valid DVXPLORER bias.
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


def load_evk_bias(file_path, verbose=False):
    """Load EVK bias.

    # Arguments
        file_path : `str`<br/>`
            the absolute path to the JSON string.

    # Returns
        bias_obj: `dict`<br/>
            A dictionary that contains valid EVK bias.
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
