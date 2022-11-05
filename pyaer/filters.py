"""Implementation of software filters in libcaer.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from typing import Any
from typing import List
from typing import Tuple

from pyaer import libcaer
from pyaer import utils
from pyaer.dtypes import BiasObjectType


class DVSNoise:
    """Software DVS background activity filter.

    # Args:
        size_x: maximum X axis resolution.
        size_y: maximum Y axis resolution.
    """

    def __init__(self, size_x: int, size_y: int) -> None:
        """DVS Noise."""
        self.size_x = size_x
        self.size_y = size_y
        self.handle = None

        self.initialize()

        if self.handle is None:
            raise ValueError(
                "Software background activity filter" "initialization failed."
            )

        self.configs_list: List[Tuple[int, str]] = [
            (
                libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_TWO_LEVELS,
                "sw_background_activity_two_levels",
            ),
            (
                libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_CHECK_POLARITY,
                "sw_background_activity_check_polarity",
            ),
            (
                libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_SUPPORT_MIN,
                "sw_background_activity_support_min",
            ),
            (
                libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_SUPPORT_MAX,
                "sw_background_activity_support_max",
            ),
            (
                libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_TIME,
                "sw_background_activity_time",
            ),
            (
                libcaer.CAER_FILTER_DVS_BACKGROUND_ACTIVITY_ENABLE,
                "sw_background_activity_enable",
            ),
            (
                libcaer.CAER_FILTER_DVS_REFRACTORY_PERIOD_TIME,
                "sw_refractory_period_time",
            ),
            (
                libcaer.CAER_FILTER_DVS_REFRACTORY_PERIOD_ENABLE,
                "sw_refractory_period_enable",
            ),
        ]

    def initialize(self) -> None:
        """Initializes."""
        if self.handle is None:
            self.handle = libcaer.caerFilterDVSNoiseInitialize(
                sizeX=self.size_x, sizeY=self.size_y
            )

    def destroy(self) -> None:
        """Destroys DVS noise filter to free up memory."""
        libcaer.caerFilterDVSNoiseDestroy(self.handle)

    def set_bias_from_json(self, file_path: str) -> None:
        """Sets bias from loading JSON configuration file.

        # Args:
            file_path: absolute path of the JSON bias file.
            verbose: print verbosely if True.
        """
        bias_obj = utils.load_json(file_path)
        if bias_obj is not None:
            self.set_bias(bias_obj)

    def set_bias(self, bias_obj: BiasObjectType) -> None:
        """Configures filter.

        # Args:
            bias_obj: A dictionary that contains the configuration of the filter.
        """
        for parameter_address, bias_name in self.configs_list:
            self.set_config(parameter_address, bias_obj[bias_name])

        self.set_config(
            libcaer.CAER_FILTER_DVS_HOTPIXEL_ENABLE, bias_obj["sw_hotpixel_enable"]
        )

        if bias_obj["sw_hotpixel_enable"] is True:
            self.set_config(
                libcaer.CAER_FILTER_DVS_HOTPIXEL_LEARN, bias_obj["sw_hotpixel_learn"]
            )
            #  self.set_config(
            #      libcaer.CAER_FILTER_DVS_HOTPIXEL_TIME,
            #      bias_obj["sw_hotpixel_time"])
            #  self.set_config(
            #      libcaer.CAER_FILTER_DVS_HOTPIXEL_COUNT,
            #      bias_obj["sw_hotpixel_count"])

    def get_bias(self) -> BiasObjectType:
        """Exports configuration.

        # Returns:
            bias_obj: A dictionary that contains the configuration of the filter.
        """
        bias_obj: BiasObjectType = {}

        for parameter_address, bias_name in self.configs_list:
            bias_obj[bias_name] = self.get_config(parameter_address)

        bias_obj["sw_hotpixel_enable"] = bool(
            self.get_config(libcaer.CAER_FILTER_DVS_HOTPIXEL_ENABLE)
        )

        bias_obj["sw_hotpixel_learn"] = bool(
            self.get_config(libcaer.CAER_FILTER_DVS_HOTPIXEL_LEARN)
        )
        if bias_obj["sw_hotpixel_enable"] is True:
            bias_obj["sw_hotpixel_time"] = self.get_config(
                libcaer.CAER_FILTER_DVS_HOTPIXEL_TIME
            )
            bias_obj["sw_hotpixel_count"] = self.get_config(
                libcaer.CAER_FILTER_DVS_HOTPIXEL_COUNT
            )

        return bias_obj

    def save_bias_to_json(self, file_path: str) -> bool:
        """Saves filter configuration to JSON.

        # Args:
            file_path: the absolute path to the destiation.

        # Returns:
            flag: returns True if success in writing, False otherwise.
        """
        bias_obj = self.get_bias()
        return utils.write_json(file_path, bias_obj)

    def set_config(self, param_addr: int, param: Any) -> bool:
        """Sets configuration.

        # Args:
            param_addr: a configuration parameter address, see defines
                `CAER_FILTER_DVS_*`.
            param: a configuration parameter value integer.

        # Returns:
            True if operation successful, false otherwise.
        """
        if self.handle is not None:
            set_sucess = libcaer.caerFilterDVSNoiseConfigSet(
                noiseFilter=self.handle, paramAddr=param_addr, param=param
            )
            return set_sucess
        else:
            return False

    def get_config(self, param_addr: int) -> Any:
        """Gets configuration.

        # Args:
            param_addr: a configuration parameter address, see defines
                `CAER_FILTER_DVS_*`.

        # Returns:
            The value of the configuration.
        """
        if self.handle is not None:
            return libcaer.caerFilterDVSNoiseConfigGet(self.handle, param_addr)
        else:
            return None

    def apply(self, event_packet: Any) -> Any:
        """Apply the filter to a event_packet.

        # Args:
            event_packet: `caerEventPacket`<br/>
                the event packet to filter.

        # Returns:
            The filtered event packet.
        """
        return libcaer.apply_dvs_noise_filter(self.handle, event_packet)
