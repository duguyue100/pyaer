"""Utilities Functions.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
import json
from scipy import stats

import pyaer
from pyaer import log

logger = log.get_logger("utils", pyaer.LOG_LEVEL)


def load_json(file_path):
    """Load JSON string.

    # Parameters
    file_path : str
        the absolute path to the JSON string.

    # Returns
    json_obj : dict
        A JSON object
    """
    try:
        json_obj = json.load(open(file_path))
        return json_obj
    except IOError:
        return None


def write_json(file_path, json_obj):
    """Write JSON string.

    # Parameters
    file_path : str
        the absolute path to the JSON string.
    json_obj : dict
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

    # Parameters
    file_path : str
        the absolute path to the JSON string.

    # Returns
    bias_obj : dict
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

    # Parameters
    file_path : str
        the absolute path to the JSON string.

    # Returns
    bias_obj : dict
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

    # Parameters
    file_path : str
        the absolute path to the JSON string.

    # Returns
    bias_obj : dict
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


def clip(n, lower, upper):
    """Return clipped value between lower and upper bound."""
    return max(lower, min(n, upper))


def mean(frame):
    """Calculate the mean of a frame.

    # Parameters
    frame : numpy.ndarray
        the input frame

    # Returns
    mean_val : float
        the mean value.
    """
    if frame is None:
        return 0.

    return frame.mean()


def trim_mean(frame, proportion_to_cut=0):
    """Remove percentiles of data before computing the mean.

    # Parameters
    frame : numpy.ndarray
        the input frame
    proportion_to_cut : float
        percentage of data to cut.

    # Returns
    mean_val : float
        the mean value.
    """
    if frame is None:
        return 0.

    return stats.trim_mean(frame.flatten(), proportion_to_cut)
