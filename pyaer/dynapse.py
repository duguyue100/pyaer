"""DYNAPSE.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from future.utils import iteritems
from builtins import range
import time
import numpy as np
from pyaer import libcaer
from pyaer import utils
from pyaer.device import USBDevice


class DYNAPSE(USBDevice):
    """DYNAPSE.

    # Arguments
        device_id: `int`<br/>
            a unique ID to identify the device from others.
            Will be used as the source for EventPackets being
            generate from its data.<br/>
            `default is 1`
        bus_number_restrict: `int`<br/>
            restrict the search for viable devices to only this USB
            bus number.<br/>
            `default is 0`
        dev_address_restrict: `int`<br/>
            restrict the search for viable devices to only this USB
            device address.<br/>
            `default is 0`
        serial_number: `str`<br/>
            restrict the search for viable devices to only devices which do
            possess the given Serial Number in their USB
            SerialNumber descriptor.<br/>
            `default is ""`
    """
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number=""):
        """DYNAPSE."""
        super(DYNAPSE, self).__init__()
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        # get camera info
        self.obtain_device_info(self.handle)

        # jump directions
        self.DYNAPSE_CONFIG_SRAM_DIRECTION_X_EAST = \
            libcaer.DYNAPSE_CONFIG_SRAM_DIRECTION_X_EAST
        self.DYNAPSE_CONFIG_SRAM_DIRECTION_X_WEST = \
            libcaer.DYNAPSE_CONFIG_SRAM_DIRECTION_X_WEST
        self.DYNAPSE_CONFIG_SRAM_DIRECTION_Y_NORTH = \
            libcaer.DYNAPSE_CONFIG_SRAM_DIRECTION_Y_NORTH
        self.DYNAPSE_CONFIG_SRAM_DIRECTION_Y_SOUTH = \
            libcaer.DYNAPSE_CONFIG_SRAM_DIRECTION_Y_SOUTH

        # synaptic weights
        self.DYNAPSE_CONFIG_CAMTYPE_F_EXC = \
            libcaer.DYNAPSE_CONFIG_CAMTYPE_F_EXC
        self.DYNAPSE_CONFIG_CAMTYPE_S_EXC = \
            libcaer.DYNAPSE_CONFIG_CAMTYPE_S_EXC
        self.DYNAPSE_CONFIG_CAMTYPE_F_INH = \
            libcaer.DYNAPSE_CONFIG_CAMTYPE_F_INH
        self.DYNAPSE_CONFIG_CAMTYPE_S_INH = \
            libcaer.DYNAPSE_CONFIG_CAMTYPE_S_INH

        # chip configurations
        self.chip_config = [libcaer.DYNAPSE_CONFIG_DYNAPSE_U0,
                            libcaer.DYNAPSE_CONFIG_DYNAPSE_U1,
                            libcaer.DYNAPSE_CONFIG_DYNAPSE_U2,
                            libcaer.DYNAPSE_CONFIG_DYNAPSE_U3]

    def obtain_device_info(self, handle):
        """Obtain DYNAPSE info.

        This function collects the following information from the device:

        - Deveice ID
        - Device serial number
        - Device USB bus number
        - Device USB device address
        - Device string
        - Logic version
        - If the device is a master camera
        - Chip ID
        - If the device has AER statistics
        - If the device has MUX statistics

        # Arguments
            handle: `caerDeviceHandle`<br/>
                a valid device handle that can be used with the other
                `libcaer` functions, or `None` on error.
        """
        if handle is not None:
            info = libcaer.caerDynapseInfoGet(handle)

            # port all info data fields out
            self.device_id = info.deviceID
            self.device_serial_number = info.deviceSerialNumber
            self.device_usb_bus_number = info.deviceUSBBusNumber
            self.device_usb_device_address = info.deviceUSBDeviceAddress
            self.device_string = info.deviceString
            self.logic_version = info.logicVersion
            self.device_is_master = info.deviceIsMaster
            self.logic_clock = info.logicClock
            self.chip_id = info.chipID
            self.aer_has_statistics = info.aerHasStatistics
            self.mux_has_statistics = info.muxHasStatistics

    def open(self,
             device_id=1,
             bus_number_restrict=0,
             dev_address_restrict=0,
             serial_number=""):
        """Open device.

        # Arguments
            device_id: `int`<br/>
                a unique ID to identify the device from others.
                Will be used as the source for EventPackets being
                generate from its data.<br/>
                `default is 1`
            bus_number_restrict: `int`<br/>
                restrict the search for viable devices to only this USB
                bus number.<br/>
                `default is 0`
            dev_address_restrict: `int`<br/>
                restrict the search for viable devices to only this USB
                device address.<br/>
                `default is 0`
            serial_number: `str`<br/>
                restrict the search for viable devices to only devices which do
                possess the given Serial Number in their USB
                SerialNumber descriptor.<br/>
                `default is ""`
        """
        super(DYNAPSE, self).open(
            libcaer.CAER_DEVICE_DYNAPSE, device_id,
            bus_number_restrict, dev_address_restrict,
            serial_number)

    def set_bias_from_json(self, file_path, fpga_bias=True, clear_sram=False,
                           setup_sram=False, scope="all", verbose=False):
        """Set bias from loading JSON configuration file.

        # Arguments
            file_path: `str`<br/>
                absolute path of the JSON bias file.
            fpga_bias: `bool`<br/>
                Set FPGA biases if True, False otherwise,<br/>
                `default is True`
            clear_sram: `bool`<br/>
                Clear SRAM if True, False otherwise,
                Default is False
            setup_sram: `bool`
                Setup SRAM if True, False otherwise,<br/>
                `default is False`
            scope: `str, dict`<br/>
                a dictionary that describe the bias setting profile,
                set everything if the argument is "all"
                Here is a basic template for scope description<br/>

                ```
                scope = {
                    0: [0, 1, 2, 3],
                    1: [0, 1, 2, 3],
                    2: [0, 1, 2, 3],
                    3: [0, 1, 2, 3],
                    }
                ```
        """
        bias_obj = utils.load_dynapse_bias(file_path, verbose)
        self.set_bias(bias_obj,
                      fpga_bias=fpga_bias,
                      clear_sram=clear_sram, setup_sram=setup_sram,
                      scope=scope)

    def clear_sram(self):
        """Clear SRAM for all chips.
        """
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U0)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM_EMPTY, 0, 0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U1)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM_EMPTY, 0, 0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U2)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM_EMPTY, 0, 0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U3)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM_EMPTY, 0, 0)

    def setup_sram(self):
        """Setup SRAM for all chips.
        """
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U0)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U0,
                        0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U1)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U1,
                        0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U2)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U2,
                        0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U3)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U3,
                        0)

    def set_chip_bias(self, bias_obj, chip_id,
                      core_ids=[0, 1, 2, 3],
                      clear_sram=False, setup_sram=False):
        """Set bias for a single chip.

        # Arguments
            bias_obj: `dict`<br/>
                a dictionary that consists of all 4 core's biases
            chip_id: `int`<br/>
                chip id is between 0-3
            core_ids: `list`<br/>
                list of core ids from 0 to 3, each element is a string,
                the default is `[0, 1, 2, 3]`<br/>
                e.g.,<br/>
                    - `[0, 3]`: set core 0 and core 3<br/>
                    - `[2]`: set core 2<br/>
                    - `[]`: do not set core level biases
            clear_sram: `bool`<br/>
                Clear SRAM if True, False otherwise,<br/>
                `default is False`
            setup_sram: bool<br/>
                Setup SRAM if True, False otherwise,<br/>
                `default is False`
        """
        # stop data stream
        self.data_stop()
        time.sleep(1)

        # Turn on chip and AER communication for configuration.
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_RUN,
                        True)
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_RUN,
                        True)

        # Clear all SRAM
        if clear_sram is True:
            self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                            libcaer.DYNAPSE_CONFIG_CHIP_ID,
                            self.chip_config[chip_id])
            self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM_EMPTY, 0, 0)

        # set chip bias
        self.set_activity_bias(bias_obj, self.chip_config[chip_id],
                               core_ids=core_ids)

        # Setup SRAM for USB monitoring of spike events
        if setup_sram is True:
            self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                            libcaer.DYNAPSE_CONFIG_CHIP_ID,
                            self.chip_config[chip_id])
            self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM,
                            self.chip_config[chip_id],
                            0)
            self.setup_sram()

        # Turn off chip/AER once done
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_RUN,
                        False)
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_RUN,
                        False)

        # Essential: wait for chip to be stable
        time.sleep(1)
        # restart data stream
        self.start_data_stream(send_default_config=False)

    def set_bias(self, bias_obj,
                 fpga_bias=True,
                 clear_sram=False, setup_sram=False,
                 scope="all"):
        """Set bias from bias dictionary.

        You don't have to turn on the clear_sram and setup_sram
        for reloading biases.

        # Arguments
            bias_obj: `dict`<br/>
                dictionary that contains DYNAPSE biases.
            fpga_bias: `bool`<br/>
                Set FPGA biases if True, False otherwise,<br/>
                `default is True`
            clear_sram: `bool`<br/>
                Clear SRAM if True, False otherwise,<br/>
                `default is False`
            setup_sram: `bool`<br/>
                Setup SRAM if True, False otherwise,<br/>
                `default is False`
            scope: `str, dict`<br/>
                a dictionary that describe the bias setting profile,
                set everything if the argument is "all"
                Here is a basic template for scope description<br/>

                ```
                scope = {
                    0: [0, 1, 2, 3],
                    1: [0, 1, 2, 3],
                    2: [0, 1, 2, 3],
                    3: [0, 1, 2, 3],
                    }
                ```

        # Returns
            flag: `bool`<br/>
                True if set successful, False otherwise.
        """
        # stop data stream
        self.data_stop()
        time.sleep(1)

        # set FPGA biases
        if fpga_bias is True:
            self.set_fpga_bias(bias_obj)

        # Turn on chip and AER communication for configuration.
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_RUN,
                        True)
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_RUN,
                        True)

        # Clear all SRAM
        if clear_sram is True:
            self.clear_sram()

        if scope == "all":
            scope = {
                0: [0, 1, 2, 3],
                1: [0, 1, 2, 3],
                2: [0, 1, 2, 3],
                3: [0, 1, 2, 3],
                }
        else:
            # make sure the chip description is a dictionary
            assert isinstance(scope, dict)

        # Set biases for some activity
        for (chip_id, core_ids) in iteritems(scope):
            self.set_activity_bias(bias_obj, self.chip_config[chip_id],
                                   core_ids=core_ids)

        # Setup SRAM for USB monitoring of spike events
        if setup_sram is True:
            self.setup_sram()

        # Turn off chip/AER once done
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_RUN,
                        False)
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_RUN,
                        False)

        # Essential: wait for chip to be stable
        time.sleep(1)
        # restart data stream
        self.start_data_stream(send_default_config=False)

    def set_fpga_bias(self, bias_obj):
        """Set FPGA biases.

        # Arguments
            bias_obj: `dict`<br/>
                dictionary that contains FPGA biases for the device.
        """
        # DYNAPSE_CONFIG_MUX
        self.set_config(libcaer.DYNAPSE_CONFIG_MUX,
                        libcaer.DYNAPSE_CONFIG_MUX_TIMESTAMP_RESET,
                        bias_obj["mux_timestamp_reset"])
        self.set_config(libcaer.DYNAPSE_CONFIG_MUX,
                        libcaer.DYNAPSE_CONFIG_MUX_FORCE_CHIP_BIAS_ENABLE,
                        bias_obj["mux_force_chip_bias_enable"])
        self.set_config(libcaer.DYNAPSE_CONFIG_MUX,
                        libcaer.DYNAPSE_CONFIG_MUX_DROP_AER_ON_TRANSFER_STALL,
                        bias_obj["mux_drop_aer_on_transfer_stall"])

        # DYNAPSE_CONFIG_AER
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_ACK_DELAY,
                        bias_obj["aer_ack_delay"])
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_ACK_EXTENSION,
                        bias_obj["aer_ack_extension"])
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_WAIT_ON_TRANSFER_STALL,
                        bias_obj["aer_wait_on_transfer_stall"])
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_EXTERNAL_AER_CONTROL,
                        bias_obj["aer_external_aer_control"])

        # DYNAPSE_CONFIG_CHIP
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_REQ_DELAY,
                        bias_obj["chip_req_delay"])
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_REQ_EXTENSION,
                        bias_obj["chip_req_extension"])

        self.set_config(libcaer.DYNAPSE_CONFIG_USB,
                        libcaer.DYNAPSE_CONFIG_USB_EARLY_PACKET_DELAY,
                        bias_obj["usb_early_packet_delay"])

    def set_activity_bias(self, bias_obj, chip_id,
                          core_ids=[0, 1, 2, 3]):
        """Set biases for each chip.

        # Arguments
            bias_obj: `dict`<br/>
                dictionary that contains activity biases for target chip.
            chip_id: `uint8_t`<br/>
                one of
                `DYNAPSE_CONFIG_DYNAPSE_U0`,
                `DYNAPSE_CONFIG_DYNAPSE_U1`,
                `DYNAPSE_CONFIG_DYNAPSE_U2`,
                `DYNAPSE_CONFIG_DYNAPSE_U3`
            core_ids: `list`<br/>
                list of core ids from 0 to 3, each element is a int,
                the default is `[0, 1, 2, 3]`<br/>
                e.g.,<br/>
                    - `[0, 3]`: set core 0 and core 3<br/>
                    - `[2]`: set core 2<br/>
                    - `[]`: do not set core level biases
        """
        assert 0 <= chip_id <= 3
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        chip_id)

        for core_id in core_ids:
            # make sure teh core id is in the range
            assert 0 <= core_id <= 3
            core_id = str(core_id)
            # IF BUF P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_BUF_P"),
                    bias_obj["c"+core_id+"_if_buf_p_coarse"],
                    bias_obj["c"+core_id+"_if_buf_p_fine"],
                    True, True, False, True))

            # IF RFR N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_RFR_N"),
                    bias_obj["c"+core_id+"_if_rfr_n_coarse"],
                    bias_obj["c"+core_id+"_if_rfr_n_fine"],
                    True, True, True, True))

            # IF NMDA N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_NMDA_N"),
                    bias_obj["c"+core_id+"_if_nmda_n_coarse"],
                    bias_obj["c"+core_id+"_if_nmda_n_fine"],
                    True, True, True, True))

            # IF DC P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_DC_P"),
                    bias_obj["c"+core_id+"_if_dc_p_coarse"],
                    bias_obj["c"+core_id+"_if_dc_p_fine"],
                    True, True, False, True))

            # IF TAU1 N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_TAU1_N"),
                    bias_obj["c"+core_id+"_if_tau1_coarse"],
                    bias_obj["c"+core_id+"_if_tau1_fine"],
                    False, True, True, True))

            # IF TAU2 N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_TAU2_N"),
                    bias_obj["c"+core_id+"_if_tau2_coarse"],
                    bias_obj["c"+core_id+"_if_tau2_fine"],
                    True, True, True, True))

            # IF THR N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_THR_N"),
                    bias_obj["c"+core_id+"_if_thr_n_coarse"],
                    bias_obj["c"+core_id+"_if_thr_n_fine"],
                    True, True, True, True))

            # IF AHW P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_AHW_P"),
                    bias_obj["c"+core_id+"_if_ahw_p_coarse"],
                    bias_obj["c"+core_id+"_if_ahw_p_fine"],
                    True, True, False, True))

            # IF AHTAU N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_AHTAU_N"),
                    bias_obj["c"+core_id+"_if_ahtau_n_coarse"],
                    bias_obj["c"+core_id+"_if_ahtau_n_fine"],
                    True, True, True, True))

            # IF AHTHR N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_AHTHR_N"),
                    bias_obj["c"+core_id+"_if_ahthr_n_coarse"],
                    bias_obj["c"+core_id+"_if_ahthr_n_fine"],
                    True, True, True, True))

            # IF CASC N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_IF_CASC_N"),
                    bias_obj["c"+core_id+"_if_casc_n_coarse"],
                    bias_obj["c"+core_id+"_if_casc_n_fine"],
                    True, True, True, True))

            # PULSE PWLK P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_PULSE_PWLK_P"),
                    bias_obj["c"+core_id+"_pulse_pwlk_p_coarse"],
                    bias_obj["c"+core_id+"_pulse_pwlk_p_fine"],
                    True, True, False, True))

            # PS WEIGHT INH S N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(
                        libcaer,
                        "DYNAPSE_CONFIG_BIAS_C"+core_id+"_PS_WEIGHT_INH_S_N"),
                    bias_obj["c"+core_id+"_ps_weight_inh_s_n_coarse"],
                    bias_obj["c"+core_id+"_ps_weight_inh_s_n_fine"],
                    True, True, True, True))

            # PS WEIGHT IN F N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(
                        libcaer,
                        "DYNAPSE_CONFIG_BIAS_C"+core_id+"_PS_WEIGHT_INH_F_N"),
                    bias_obj["c"+core_id+"_ps_weight_inh_f_n_coarse"],
                    bias_obj["c"+core_id+"_ps_weight_inh_f_n_fine"],
                    True, True, True, True))

            # PS WEIGHT EXC S N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(
                        libcaer,
                        "DYNAPSE_CONFIG_BIAS_C"+core_id+"_PS_WEIGHT_EXC_S_N"),
                    bias_obj["c"+core_id+"_ps_weight_exc_s_n_coarse"],
                    bias_obj["c"+core_id+"_ps_weight_exc_s_n_fine"],
                    True, True, True, True))

            # PS WEIGHT EXC F N
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(
                        libcaer,
                        "DYNAPSE_CONFIG_BIAS_C"+core_id+"_PS_WEIGHT_EXC_F_N"),
                    bias_obj["c"+core_id+"_ps_weight_exc_f_n_coarse"],
                    bias_obj["c"+core_id+"_ps_weight_exc_f_n_fine"],
                    True, True, True, True))

            # NPDPII TAU S P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_NPDPII_TAU_S_P"),
                    bias_obj["c"+core_id+"_npdpii_tau_s_p_coarse"],
                    bias_obj["c"+core_id+"_npdpii_tau_s_p_fine"],
                    True, True, False, True))

            # NPDPII TAU F P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_NPDPII_TAU_F_P"),
                    bias_obj["c"+core_id+"_npdpii_tau_f_p_coarse"],
                    bias_obj["c"+core_id+"_npdpii_tau_f_p_fine"],
                    True, True, False, True))

            # NPDPII THR S P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_NPDPII_THR_S_P"),
                    bias_obj["c"+core_id+"_npdpii_thr_s_p_coarse"],
                    bias_obj["c"+core_id+"_npdpii_thr_s_p_fine"],
                    True, True, False, True))

            # NPDPII THR F P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_NPDPII_THR_F_P"),
                    bias_obj["c"+core_id+"_npdpii_thr_f_p_coarse"],
                    bias_obj["c"+core_id+"_npdpii_thr_f_p_fine"],
                    True, True, False, True))

            # NPDPIE TAU S P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_NPDPIE_TAU_S_P"),
                    bias_obj["c"+core_id+"_npdpie_tau_s_p_coarse"],
                    bias_obj["c"+core_id+"_npdpie_tau_s_p_fine"],
                    True, True, False, True))

            # NPDPIE TAU F P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_NPDPIE_TAU_F_P"),
                    bias_obj["c"+core_id+"_npdpie_tau_f_p_coarse"],
                    bias_obj["c"+core_id+"_npdpie_tau_f_p_fine"],
                    True, True, False, True))

            # NPDPIE THR S P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_NPDPIE_THR_S_P"),
                    bias_obj["c"+core_id+"_npdpie_thr_s_p_coarse"],
                    bias_obj["c"+core_id+"_npdpie_thr_s_p_fine"],
                    True, True, False, True))

            # NPDPIE THR F P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_NPDPIE_THR_F_P"),
                    bias_obj["c"+core_id+"_npdpie_thr_f_p_coarse"],
                    bias_obj["c"+core_id+"_npdpie_thr_f_p_fine"],
                    True, True, False, True))

            # R2R P
            self.set_config(
                libcaer.DYNAPSE_CONFIG_CHIP,
                libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
                libcaer.set_dynapse_bias(
                    getattr(libcaer,
                            "DYNAPSE_CONFIG_BIAS_C"+core_id+"_R2R_P"),
                    bias_obj["c"+core_id+"_r2r_p_coarse"],
                    bias_obj["c"+core_id+"_r2r_p_fine"],
                    True, True, False, True))

        # biases for all the cores
        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_D_BUFFER,
                bias_obj["d_buffer_coarse"],
                bias_obj["d_buffer_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_D_SSP,
                bias_obj["d_ssp_coarse"],
                bias_obj["d_ssp_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_D_SSN,
                bias_obj["d_ssn_coarse"],
                bias_obj["d_ssn_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_U_BUFFER,
                bias_obj["u_buffer_coarse"],
                bias_obj["u_buffer_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_U_SSP,
                bias_obj["u_ssp_coarse"],
                bias_obj["u_ssp_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_U_SSN,
                bias_obj["u_ssn_coarse"],
                bias_obj["u_ssn_fine"],
                True, True, False, True))

    def get_cf_bias(self, param_addr, param):
        """Get coarse-fine bias.

        Note: biases for neurons currently cannot be recalled.

        # Arguments
            param_addr: `int`<br/>
                a parameter address, to select a specific parameter to update
                from this particular configuration module. Only positive
                numbers (including zero) are allowed.
            param: `int` or `bool`<br/>
                a configuration parameter's new value.

        # Returns
            coarse_value: `uint`<br/>
                coarse value
            fine_value: `uint`<br/>
                fine value
        """
        cf_param = libcaer.caerBiasCoarseFineParse(
            self.get_config(param_addr, param))

        return cf_param.coarseValue, cf_param.fineValue

    def get_fpga_bias(self):
        """Get bias settings from FPGA.

        # Returns
            bias_obj: `dict`
                dictionary that contains DYNAPSE current bias settings.
        """
        bias_obj = {}
        # DYNAPSE_CONFIG_MUX
        bias_obj["mux_timestamp_reset"] = self.get_config(
            libcaer.DYNAPSE_CONFIG_MUX,
            libcaer.DYNAPSE_CONFIG_MUX_TIMESTAMP_RESET)
        bias_obj["mux_force_chip_bias_enable"] = self.get_config(
            libcaer.DYNAPSE_CONFIG_MUX,
            libcaer.DYNAPSE_CONFIG_MUX_FORCE_CHIP_BIAS_ENABLE)
        bias_obj["mux_drop_aer_on_transfer_stall"] = self.get_config(
            libcaer.DYNAPSE_CONFIG_MUX,
            libcaer.DYNAPSE_CONFIG_MUX_DROP_AER_ON_TRANSFER_STALL)

        # DYNAPSE_CONFIG_AER
        bias_obj["aer_ack_delay"] = self.get_config(
            libcaer.DYNAPSE_CONFIG_AER,
            libcaer.DYNAPSE_CONFIG_AER_ACK_DELAY)
        bias_obj["aer_ack_extension"] = self.get_config(
            libcaer.DYNAPSE_CONFIG_AER,
            libcaer.DYNAPSE_CONFIG_AER_ACK_EXTENSION)
        bias_obj["aer_wait_on_transfer_stall"] = self.get_config(
            libcaer.DYNAPSE_CONFIG_AER,
            libcaer.DYNAPSE_CONFIG_AER_WAIT_ON_TRANSFER_STALL)
        bias_obj["aer_external_aer_control"] = self.get_config(
            libcaer.DYNAPSE_CONFIG_AER,
            libcaer.DYNAPSE_CONFIG_AER_EXTERNAL_AER_CONTROL)

        # DYNAPSE_CONFIG_CHIP
        bias_obj["chip_req_delay"] = self.get_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_REQ_DELAY)
        bias_obj["chip_req_extension"] = self.get_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_REQ_EXTENSION)

        bias_obj["usb_early_packet_delay"] = self.get_config(
            libcaer.DYNAPSE_CONFIG_USB,
            libcaer.DYNAPSE_CONFIG_USB_EARLY_PACKET_DELAY)

        return bias_obj

    def save_fpga_bias_to_json(self, file_path):
        """Save FPGA bias to JSON.

        Only the bias from FPGA can be retrieved.

        # Arguments
            file_path: `str`<br/>
                the absolute path to the destiation.

        # Returns
            flag: `bool`<br/>
                returns True if success in writing, False otherwise.
        """
        bias_obj = self.get_fpga_bias()
        return utils.write_json(file_path, bias_obj)

    def start_data_stream(self, send_default_config=True):
        """Start streaming data.

        # Arguments
            send_default_config: `bool`<br/>
                send default config to the device before starting
                the data streaming.<br/>
                `default is True`
        """
        if send_default_config is True:
            self.send_default_config()
        self.data_start()
        self.set_data_exchange_blocking()

    def core_xy_to_neuron_id(self, core_id, column_x, row_y):
        """Map core ID and column/row address
        to the correct chip global neuron address.

        # Arguments
            core_id: `uint8`<br/>
                the chip's core ID, range [0, 3].
            column_x: `uint8`<br/>
                the neuron's column address, range [0, 15].
            row_y: `uint8`<br/>
                the neuron's row address, range [0, 15].

        # Returns
            neuron_id: `uint16`<br/>
                chip global neuron address
        """
        return libcaer.caerDynapseCoreXYToNeuronId(
            coreId=core_id,
            columnX=column_x,
            rowY=row_y)

    def core_id_to_neuron_id(self, core_id, neuron_id_core):
        """Map core ID and per-core neuron address
        to the correct chip global neuron address.

        # Arguments
            core_id: `uint8`<br/>
                the chip's core ID, range [0, 3].
            neuron_id_core: `uint8`<br/>
                the neuron's address within this core, range [0, 255].

        # Returns
            neuron_id: `uint16`<br/>
                chip global neuron address.
        """
        return libcaer.caerDynapseCoreAddrToNeuronId(
            coreId=core_id,
            neuronAddrCore=neuron_id_core)

    def write_poisson_spikerate(self, neuron_id, rate):
        """Specifies the poisson spike generator's spike rate.

        # Arguments
            neuron_id: `uint16`<br/>
                The target neuron of the poisson spike train, range [0,1023].
            rate: `float`<br/>
                The rate in Hz of the spike train, this will be quantized
                to the nearest supported level, range [0, 4300].

        # Returns
            flag: `bool`<br/>
                True if success, False otherwise
        """
        return libcaer.caerDynapseWritePoissonSpikeRate(
            self.handle, neuronAddr=neuron_id, rateHz=rate)

    def write_sram_N(self, neuron_id, sram_id, virtual_core_id, sx,
                     dx, sy, dy, destination_core):
        """Write one of the 4 SRAMs of a single neuron.

        Writing the SRAM means writing the destination
        address of where the spikes will be routed to.
        This works on the on-chip SRAM!

        # Arguments
            neuron_id: `uint16`<br/>
                the neuron to program, range [0, 1023]
            sram_id: `uint8`<br/>
                SRAM address, range [0, 3]
            virtual_core_id: `utin8`<br/>
                fake source core ID, set it to this value
                instead of the actual source core ID, range [0, 3].
            sx: `bool`<br/>
                X direction, can be one of:
                `[DYNAPSE_CONFIG_SRAM_DIRECTION_X_EAST,
                  DYNAPSE_CONFIG_SRAM_DIRECTION_X_WEST]`.
            dx: `uint8`<br/>
                X delta, number of chips to jumps before
                reaching destination, range is [0, 3]
            sy: `bool`<br/>
                Y direction, can be one of:
                `[DYNAPSE_CONFIG_SRAM_DIRECTION_Y_NORTH,
                  DYNAPSE_CONFIG_SRAM_DIRECTION_Y_SOUTH]`.
            dy: `uint8`<br/>
                number of chips to jumps before reaching destination,
                range is [0, 3]
            destination_core: `uint8`<br/>
                spike destination core, uses one-hot coding for the 4 cores
                `[C3, C2, C1, C0] -> [0, 0, 0, 0]` (0 decimal) no core,
                `[1, 1, 1, 1]` (15 decimal) all cores

        # Returns
            flag: `bool`<br/>
                True if success, False otherwise
        """
        return libcaer.caerDynapseWriteSramN(
            handle=self.handle,
            neuronAddr=neuron_id,
            sramId=sram_id,
            virtualCoreId=virtual_core_id,
            sx=sx, dx=dx, sy=sy, dy=dy,
            destinationCore=destination_core)

    def write_cam(self, input_neuron_id, neuron_id, cam_id, synapse_type):
        """Write a single CAM.

        To specify which spikes are allowed as input into a neuron.

        # Arguments
            input_neuron_id: `uint16`<br/>
                the neuron address that should be let in as input to
                this neuron, range [0, 1023].
            neuron_id: `uint16`<br/>
                the neuron address whose CAM should be programmed,
                range [0,1023].
            cam_id: `uint8`<br/>
                CAM address (synapse), each neuron has 64, range [0,63].
            synapse_type: `uint8`<br/>
                one of the four possible synaptic weights:

                ```
                [DYNAPSE_CONFIG_CAMTYPE_F_EXC,
                 DYNAPSE_CONFIG_CAMTYPE_S_EXC,
                 DYNAPSE_CONFIG_CAMTYPE_F_INH,
                 DYNAPSE_CONFIG_CAMTYPE_S_INH].
                ```

        # Returns
            flag: `bool`<br/>
                True if success, False otherwise
        """
        return libcaer.caerDynapseWriteCam(
            handle=self.handle,
            inputNeuronAddr=input_neuron_id,
            neuronAddr=neuron_id,
            camId=cam_id,
            synapseType=synapse_type)

    def get_event(self):
        """Get Event.

        # Returns
            spike_events: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (N, 4) where N
                is the number of spike events in the packet.
                Each row of the array has a single spike event.
                The first value is the timestamp of the event.
                The second value is the neuron ID.
                The third value is the chip ID.
                The last value is the source core ID.
            num_spike_events: `int`<br/>
                the number of the spike events.
        """
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None:
            num_spike_events = 0
            spike_events = None
            for packet_id in range(packet_number):
                packet_header, packet_type = self.get_packet_header(
                    packet_container, packet_id)
                if packet_type == libcaer.SPIKE_EVENT:
                    events, num_events = self.get_spike_event(packet_header)
                    spike_events = np.hstack((spike_events, events)) \
                        if spike_events is not None else events
                    num_spike_events += num_events
            libcaer.caerEventPacketContainerFree(packet_container)
            return (spike_events, num_spike_events)
        else:
            return (None, None)
