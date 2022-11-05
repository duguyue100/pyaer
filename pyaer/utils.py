"""Utilities Functions.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from typing import Any
from typing import Dict
from typing import List
from typing import Union
from typing import Optional
import sys
from importlib.abc import Loader
from importlib.util import spec_from_file_location
from importlib.util import module_from_spec
import json
import os
import time
from collections import OrderedDict

import yaml
from yaml import SafeLoader
from yaml import SafeDumper

import pyaer
from pyaer import log

logger = log.get_logger("utils", pyaer.LOG_LEVEL)


def get_nanotime():
    return str(int(time.time() * 1e9)).encode("utf-8")


def import_custom_module(custom_file: str, custom_class: str) -> Any:
    """Load custom module by file path.

    # Args:
        custom_file: absolute file path to the custom module file.
        custom_class: the class name to import that is in the custom_file
    """
    module_name = os.path.basename(custom_file).split(".")[0]
    spec = spec_from_file_location(module_name, custom_file)
    if spec is not None:
        module = module_from_spec(spec)
        sys.modules[module_name] = module
        assert isinstance(spec.loader, Loader)
        spec.loader.exec_module(module)

    return getattr(module, custom_class)


def parse_type(custom_str: str) -> Union[int, float, bool, str]:
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


def parse_custom_args(custom_args: List[str]) -> Dict[str, Any]:
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
        zip(
            [opt.replace("-", "") for opt in custom_args[::2]],
            [parse_type(val) for val in custom_args[1::2]],
        )
    )

    return custom_args_dict


def ordered_yml_load(stream: str) -> Dict[str, Any]:
    """Load YAML configs in order."""

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return OrderedDict(loader.construct_pairs(node))

    SafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )

    return yaml.load(stream, SafeLoader)


def ordered_yml_dump(data, stream=None, **kwds):
    """Dump YAML configs in order."""

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items()
        )

    SafeDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, SafeDumper, **kwds)


def expandpath(path: str) -> str:
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Loads JSON string.

    # Args:
        file_path: the absolute path to the JSON string.
    """
    try:
        json_obj = json.load(open(file_path))
        return json_obj
    except IOError:
        return None


def write_json(file_path: str, json_obj: Dict[str, Any]) -> bool:
    """Writes JSON string.

    # Arguments
        file_path: the absolute path to the JSON string.
        json_obj: a dictionary
    """
    try:
        with open(file_path, "w") as f:
            json.dump(json_obj, f)
            f.close()
        return True
    except IOError:
        return False
