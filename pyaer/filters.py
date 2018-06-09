"""Implementation of software filters in libcaer.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import

from pyaer import libcaer


class DVSNoise(object):
    """Software DVS background activity filter."""
    def __init__(self,
                 size_x,
                 size_y):
        """DVS Noise.

        Parameters
        ----------
        size_x : uint16
            maximum X axis resolution.
        size_y : uint16
            maximum Y axis resolution.
        """
        self.size_x = size_x
        self.size_y = size_y
        self.handle = None

        self.initialize()

        if self.handle is None:
            raise ValueError("Software background activity filter"
                             "initialization failed.")

    def initialize(self):
        """Initialize."""
        if self.handle is None:
            self.handle = libcaer.caerFilterDVSNoiseInitialize(
                    sizeX=self.size_x, sizeY=self.size_y)

    def destroy(self):
        """Destroy DVS noise filter to free up memory."""
        libcaer.caerFilterDVSNoiseDestroy(self.handle)

    def set_bias(self, bias_obj):
        """Configure filter.

        Parameters
        ----------
        bias_obj : dict
            A dictionary that contains the configuration of
            the filter
        """
        self.set_config(
            libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_TWO_LEVELS,
            bias_obj["sw_background_activity_two_levels"])
        self.set_config(
            libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_SUPPORT_MIN,
            bias_obj["sw_background_activity_support_min"])
        self.set_config(
            libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_SUPPORT_MAX,
            bias_obj["sw_background_activity_support_max"])
        self.set_config(
            libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_TIME,
            bias_obj["sw_background_activity_time"])
        self.set_config(
            libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_ENABLE,
            bias_obj["sw_background_activity_enable"])

        self.set_config(
            libcaer.CAER_FILTER_DVS_REFRACTORY_PERIOD_TIME,
            bias_obj["sw_refractory_period_time"])
        self.set_config(
            libcaer.CAER_FILTER_DVS_REFRACTORY_PERIOD_ENABLE,
            bias_obj["sw_refractory_period_enable"])

        self.set_config(
            libcaer.CAER_FILTER_DVS_HOTPIXEL_ENABLE,
            bias_obj["sw_hotpixel_enable"])

        if bias_obj["sw_hotpixel_enable"] is True:
            self.set_config(
                libcaer.CAER_FILTER_DVS_HOTPIXEL_LEARN,
                bias_obj["sw_hotpixel_learn"])
            self.set_config(
                libcaer.CAER_FILTER_DVS_HOTPIXEL_TIME,
                bias_obj["sw_hotpixel_time"])
            self.set_config(
                libcaer.CAER_FILTER_DVS_HOTPIXEL_COUNT,
                bias_obj["sw_hotpixel_count"])

    def get_bias(self):
        """Export configuration."""
        bias_obj = {}

        bias_obj["sw_background_activity_two_levels"] = self.get_config(
            libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_TWO_LEVELS)
        bias_obj["sw_background_activity_support_min"] = self.get_config(
            libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_SUPPORT_MIN)
        bias_obj["sw_background_activity_support_max"] = self.get_config(
            libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_SUPPORT_MAX)
        bias_obj["sw_background_activity_time"] = self.get_config(
            libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_TIME)
        bias_obj["sw_background_activity_enable"] = self.get_config(
            libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_ENABLE)

        bias_obj["sw_refractory_period_time"] = self.get_config(
            libcaer.CAER_FILTER_DVS_REFRACTORY_PERIOD_TIME)
        bias_obj["sw_refractory_period_enable"] = self.get_config(
            libcaer.CAER_FILTER_DVS_REFRACTORY_PERIOD_ENABLE)

        bias_obj["sw_hotpixel_enable"] = self.get_config(
            libcaer.CAER_FILTER_DVS_HOTPIXEL_ENABLE)

        bias_obj["sw_hotpixel_learn"] = self.get_config(
            libcaer.CAER_FILTER_DVS_HOTPIXEL_LEARN)
        if bias_obj["sw_hotpixel_enable"] is True:
            bias_obj["sw_hotpixel_time"] = self.get_config(
                libcaer.CAER_FILTER_DVS_HOTPIXEL_TIME)
            bias_obj["sw_hotpixel_count"] = self.get_config(
                libcaer.CAER_FILTER_DVS_HOTPIXEL_COUNT)

        return bias_obj

    def set_config(self, param_addr, param):
        """Set configuration.

        Parameters
        ----------
        param_addr : uint8
            a configuration parameter address, see defines CAER_FILTER_DVS_*.
        param : uint64
            a configuration parameter value integer.

        Returns
        -------
        flag : bool
            True if operation successful, false otherwise.
        """
        if self.handle is not None:
            set_sucess = libcaer.caerFilterDVSNoiseConfigSet(
                noiseFilter=self.handle,
                paramAddr=param_addr, param=param)
            return set_sucess
        else:
            return False

    def get_config(self, param_addr):
        """Get configuration.

        Parameters
        ----------
        param_addr : uint8
            a configuration parameter address, see defines CAER_FILTER_DVS_*.

        Returns
        -------
        param : uint64
            the value of the configuration.
        """
        if self.handle is not None:
            return libcaer.caerFilterDVSNoiseConfigGet(
                self.handle, param_addr)
        else:
            return None
