"""DYNAPSE.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from builtins import range
import time
import numpy as np
from pyaer import libcaer
from pyaer import utils
from pyaer.device import USBDevice


class DYNAPSE(USBDevice):
    """Class defines DYNAPSE."""
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number=""):
        """DYNAPSE.

        Parameters
        ----------
        device_id : int
            a unique ID to identify the device from others.
            Will be used as the source for EventPackets being
            generate from its data.
            default is 1
        bus_number_restrict : int
            restrict the search for viable devices to only this USB
            bus number.
            default is 0
        dev_address_restrict : int
            restrict the search for viable devices to only this USB
            device address.
            default is 0
        serial_number : str
            restrict the search for viable devices to only devices which do
            possess the given Serial Number in their USB
            SerialNumber descriptor.
            default is ""
        """
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

        self.bias_obj = None

    def obtain_device_info(self, handle):
        """Obtain DYNAPSE info."""
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

        Parameters
        ----------
        device_id : int
            a unique ID to identify the device from others.
            Will be used as the source for EventPackets being
            generate from its data.
            default is 1
        bus_number_restrict : int
            restrict the search for viable devices to only this USB
            bus number.
            default is 0
        dev_address_restrict : int
            restrict the search for viable devices to only this USB
            device address.
            default is 0
        serial_number : str
            restrict the search for viable devices to only devices which do
            possess the given Serial Number in their USB
            SerialNumber descriptor.
            default is ""
        """
        super(DYNAPSE, self).open(
            libcaer.CAER_DEVICE_DYNAPSE, device_id,
            bus_number_restrict, dev_address_restrict,
            serial_number)

    def set_bias_from_json(self, file_path, clear_sram=False,
                           setup_sram=False, verbose=False):
        """Set bias from loading JSON configuration file.

        # Parameters
        file_path : string
            absolute path of the JSON bias file.
        """
        bias_obj = utils.load_dvs_bias(file_path, verbose)
        self.set_bias(bias_obj, clear_sram=clear_sram, setup_sram=setup_sram)

    def set_bias(self, bias_obj, clear_sram=False, setup_sram=False):
        """Set bias from bias dictionary.

        You don't have to turn on the clear_sram and setup_sram
        for reloading biases.

        # Parameters
        bias_obj : dict
            dictionary that contains DVS128 biases.

        # Returns
        flag : bool
            True if set successful, False otherwise.
            TODO: make this flag check possible
        """
        time.sleep(1)
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

        # Set biases for some activity
        self.set_activity_bias(libcaer.DYNAPSE_CONFIG_DYNAPSE_U0,
                               bias_obj)
        self.set_activity_bias(libcaer.DYNAPSE_CONFIG_DYNAPSE_U1,
                               bias_obj)
        self.set_activity_bias(libcaer.DYNAPSE_CONFIG_DYNAPSE_U2,
                               bias_obj)
        self.set_activity_bias(libcaer.DYNAPSE_CONFIG_DYNAPSE_U3,
                               bias_obj)

        # Setup SRAM for USB monitoring of spike events
        if setup_sram is True:
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

        # Turn off chip/AER once done
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_RUN,
                        False)
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_RUN,
                        False)

        # Essential: wait for chip to be stable
        time.sleep(1)
        self.bias_obj = bias_obj

    def set_activity_bias(self, chip_id, bias_obj):
        """Set biases for each chip.

        Parameters
        ----------
        chip_id : uint8_t
            one of
            DYNAPSE_CONFIG_DYNAPSE_U0,
            DYNAPSE_CONFIG_DYNAPSE_U1,
            DYNAPSE_CONFIG_DYNAPSE_U2,
            DYNAPSE_CONFIG_DYNAPSE_U3
        bias_obj : dict
            dictionary that contains DVS128 biases.
        """
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        chip_id)

        # Core 0
        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_BUF_P,
                bias_obj["c0_if_buf_p_coarse"],
                bias_obj["c0_if_buf_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_RFR_N,
                bias_obj["c0_if_rfr_n_coarse"],
                bias_obj["c0_if_rfr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_NMDA_N,
                bias_obj["c0_if_nmda_n_coarse"],
                bias_obj["c0_if_nmda_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_DC_P,
                bias_obj["c0_if_dc_p_coarse"],
                bias_obj["c0_if_dc_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_TAU1_N,
                bias_obj["c0_if_tau1_coarse"],
                bias_obj["c0_if_tau1_fine"],
                False, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_TAU2_N,
                bias_obj["c0_if_tau2_coarse"],
                bias_obj["c0_if_tau2_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_THR_N,
                bias_obj["c0_if_thr_n_coarse"],
                bias_obj["c0_if_thr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_AHW_P,
                bias_obj["c0_if_ahw_p_coarse"],
                bias_obj["c0_if_ahw_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_AHTAU_N,
                bias_obj["c0_if_ahtau_n_coarse"],
                bias_obj["c0_if_ahtau_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_AHTHR_N,
                bias_obj["c0_if_ahthr_n_coarse"],
                bias_obj["c0_if_ahthr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_IF_CASC_N,
                bias_obj["c0_if_casc_n_coarse"],
                bias_obj["c0_if_casc_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_PULSE_PWLK_P,
                bias_obj["c0_pulse_pwlk_p_coarse"],
                bias_obj["c0_pulse_pwlk_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_PS_WEIGHT_INH_S_N,
                bias_obj["c0_ps_weight_inh_s_n_coarse"],
                bias_obj["c0_ps_weight_inh_s_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_PS_WEIGHT_INH_F_N,
                bias_obj["c0_ps_weight_inh_f_n_coarse"],
                bias_obj["c0_ps_weight_inh_f_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_PS_WEIGHT_EXC_S_N,
                bias_obj["c0_ps_weight_exc_s_n_coarse"],
                bias_obj["c0_ps_weight_exc_s_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_PS_WEIGHT_EXC_F_N,
                bias_obj["c0_ps_weight_exc_f_n_coarse"],
                bias_obj["c0_ps_weight_exc_f_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_NPDPII_TAU_S_P,
                bias_obj["c0_npdpii_tau_s_p_coarse"],
                bias_obj["c0_npdpii_tau_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_NPDPII_TAU_F_P,
                bias_obj["c0_npdpii_tau_f_p_coarse"],
                bias_obj["c0_npdpii_tau_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_NPDPII_THR_S_P,
                bias_obj["c0_npdpii_thr_s_p_coarse"],
                bias_obj["c0_npdpii_thr_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_NPDPII_THR_F_P,
                bias_obj["c0_npdpii_thr_f_p_coarse"],
                bias_obj["c0_npdpii_thr_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_NPDPIE_TAU_S_P,
                bias_obj["c0_npdpie_tau_s_p_coarse"],
                bias_obj["c0_npdpie_tau_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_NPDPIE_TAU_F_P,
                bias_obj["c0_npdpie_tau_f_p_coarse"],
                bias_obj["c0_npdpie_tau_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_NPDPIE_THR_S_P,
                bias_obj["c0_npdpie_thr_s_p_coarse"],
                bias_obj["c0_npdpie_thr_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_NPDPIE_THR_F_P,
                bias_obj["c0_npdpie_thr_f_p_coarse"],
                bias_obj["c0_npdpie_thr_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C0_R2R_P,
                bias_obj["c0_r2r_p_coarse"],
                bias_obj["c0_r2r_p_fine"],
                True, True, False, True))

        # Core 1
        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_BUF_P,
                bias_obj["c1_if_buf_p_coarse"],
                bias_obj["c1_if_buf_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_RFR_N,
                bias_obj["c1_if_rfr_n_coarse"],
                bias_obj["c1_if_rfr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_NMDA_N,
                bias_obj["c1_if_nmda_n_coarse"],
                bias_obj["c1_if_nmda_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_DC_P,
                bias_obj["c1_if_dc_p_coarse"],
                bias_obj["c1_if_dc_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_TAU1_N,
                bias_obj["c1_if_tau1_coarse"],
                bias_obj["c1_if_tau1_fine"],
                False, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_TAU2_N,
                bias_obj["c1_if_tau2_coarse"],
                bias_obj["c1_if_tau2_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_THR_N,
                bias_obj["c1_if_thr_n_coarse"],
                bias_obj["c1_if_thr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_AHW_P,
                bias_obj["c1_if_ahw_p_coarse"],
                bias_obj["c1_if_ahw_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_AHTAU_N,
                bias_obj["c1_if_ahtau_n_coarse"],
                bias_obj["c1_if_ahtau_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_AHTHR_N,
                bias_obj["c1_if_ahthr_n_coarse"],
                bias_obj["c1_if_ahthr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_IF_CASC_N,
                bias_obj["c1_if_casc_n_coarse"],
                bias_obj["c1_if_casc_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_PULSE_PWLK_P,
                bias_obj["c1_pulse_pwlk_p_coarse"],
                bias_obj["c1_pulse_pwlk_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_PS_WEIGHT_INH_S_N,
                bias_obj["c1_ps_weight_inh_s_n_coarse"],
                bias_obj["c1_ps_weight_inh_s_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_PS_WEIGHT_INH_F_N,
                bias_obj["c1_ps_weight_inh_f_n_coarse"],
                bias_obj["c1_ps_weight_inh_f_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_PS_WEIGHT_EXC_S_N,
                bias_obj["c1_ps_weight_exc_s_n_coarse"],
                bias_obj["c1_ps_weight_exc_s_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_PS_WEIGHT_EXC_F_N,
                bias_obj["c1_ps_weight_exc_f_n_coarse"],
                bias_obj["c1_ps_weight_exc_f_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_NPDPII_TAU_S_P,
                bias_obj["c1_npdpii_tau_s_p_coarse"],
                bias_obj["c1_npdpii_tau_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_NPDPII_TAU_F_P,
                bias_obj["c1_npdpii_tau_f_p_coarse"],
                bias_obj["c1_npdpii_tau_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_NPDPII_THR_S_P,
                bias_obj["c1_npdpii_thr_s_p_coarse"],
                bias_obj["c1_npdpii_thr_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_NPDPII_THR_F_P,
                bias_obj["c1_npdpii_thr_f_p_coarse"],
                bias_obj["c1_npdpii_thr_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_NPDPIE_TAU_S_P,
                bias_obj["c1_npdpie_tau_s_p_coarse"],
                bias_obj["c1_npdpie_tau_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_NPDPIE_TAU_F_P,
                bias_obj["c1_npdpie_tau_f_p_coarse"],
                bias_obj["c1_npdpie_tau_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_NPDPIE_THR_S_P,
                bias_obj["c1_npdpie_thr_s_p_coarse"],
                bias_obj["c1_npdpie_thr_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_NPDPIE_THR_F_P,
                bias_obj["c1_npdpie_thr_f_p_coarse"],
                bias_obj["c1_npdpie_thr_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C1_R2R_P,
                bias_obj["c1_r2r_p_coarse"],
                bias_obj["c1_r2r_p_fine"],
                True, True, False, True))

        # Core 2
        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_BUF_P,
                bias_obj["c2_if_buf_p_coarse"],
                bias_obj["c2_if_buf_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_RFR_N,
                bias_obj["c2_if_rfr_n_coarse"],
                bias_obj["c2_if_rfr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_NMDA_N,
                bias_obj["c2_if_nmda_n_coarse"],
                bias_obj["c2_if_nmda_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_DC_P,
                bias_obj["c2_if_dc_p_coarse"],
                bias_obj["c2_if_dc_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_TAU1_N,
                bias_obj["c2_if_tau1_coarse"],
                bias_obj["c2_if_tau1_fine"],
                False, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_TAU2_N,
                bias_obj["c2_if_tau2_coarse"],
                bias_obj["c2_if_tau2_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_THR_N,
                bias_obj["c2_if_thr_n_coarse"],
                bias_obj["c2_if_thr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_AHW_P,
                bias_obj["c2_if_ahw_p_coarse"],
                bias_obj["c2_if_ahw_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_AHTAU_N,
                bias_obj["c2_if_ahtau_n_coarse"],
                bias_obj["c2_if_ahtau_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_AHTHR_N,
                bias_obj["c2_if_ahthr_n_coarse"],
                bias_obj["c2_if_ahthr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_IF_CASC_N,
                bias_obj["c2_if_casc_n_coarse"],
                bias_obj["c2_if_casc_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_PULSE_PWLK_P,
                bias_obj["c2_pulse_pwlk_p_coarse"],
                bias_obj["c2_pulse_pwlk_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_PS_WEIGHT_INH_S_N,
                bias_obj["c2_ps_weight_inh_s_n_coarse"],
                bias_obj["c2_ps_weight_inh_s_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_PS_WEIGHT_INH_F_N,
                bias_obj["c2_ps_weight_inh_f_n_coarse"],
                bias_obj["c2_ps_weight_inh_f_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_PS_WEIGHT_EXC_S_N,
                bias_obj["c2_ps_weight_exc_s_n_coarse"],
                bias_obj["c2_ps_weight_exc_s_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_PS_WEIGHT_EXC_F_N,
                bias_obj["c2_ps_weight_exc_f_n_coarse"],
                bias_obj["c2_ps_weight_exc_f_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_NPDPII_TAU_S_P,
                bias_obj["c2_npdpii_tau_s_p_coarse"],
                bias_obj["c2_npdpii_tau_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_NPDPII_TAU_F_P,
                bias_obj["c2_npdpii_tau_f_p_coarse"],
                bias_obj["c2_npdpii_tau_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_NPDPII_THR_S_P,
                bias_obj["c2_npdpii_thr_s_p_coarse"],
                bias_obj["c2_npdpii_thr_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_NPDPII_THR_F_P,
                bias_obj["c2_npdpii_thr_f_p_coarse"],
                bias_obj["c2_npdpii_thr_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_NPDPIE_TAU_S_P,
                bias_obj["c2_npdpie_tau_s_p_coarse"],
                bias_obj["c2_npdpie_tau_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_NPDPIE_TAU_F_P,
                bias_obj["c2_npdpie_tau_f_p_coarse"],
                bias_obj["c2_npdpie_tau_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_NPDPIE_THR_S_P,
                bias_obj["c2_npdpie_thr_s_p_coarse"],
                bias_obj["c2_npdpie_thr_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_NPDPIE_THR_F_P,
                bias_obj["c2_npdpie_thr_f_p_coarse"],
                bias_obj["c2_npdpie_thr_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C2_R2R_P,
                bias_obj["c2_r2r_p_coarse"],
                bias_obj["c2_r2r_p_fine"],
                True, True, False, True))

        # Core 3
        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_BUF_P,
                bias_obj["c3_if_buf_p_coarse"],
                bias_obj["c3_if_buf_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_RFR_N,
                bias_obj["c3_if_rfr_n_coarse"],
                bias_obj["c3_if_rfr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_NMDA_N,
                bias_obj["c3_if_nmda_n_coarse"],
                bias_obj["c3_if_nmda_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_DC_P,
                bias_obj["c3_if_dc_p_coarse"],
                bias_obj["c3_if_dc_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_TAU1_N,
                bias_obj["c3_if_tau1_coarse"],
                bias_obj["c3_if_tau1_fine"],
                False, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_TAU2_N,
                bias_obj["c3_if_tau2_coarse"],
                bias_obj["c3_if_tau2_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_THR_N,
                bias_obj["c3_if_thr_n_coarse"],
                bias_obj["c3_if_thr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_AHW_P,
                bias_obj["c3_if_ahw_p_coarse"],
                bias_obj["c3_if_ahw_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_AHTAU_N,
                bias_obj["c3_if_ahtau_n_coarse"],
                bias_obj["c3_if_ahtau_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_AHTHR_N,
                bias_obj["c3_if_ahthr_n_coarse"],
                bias_obj["c3_if_ahthr_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_IF_CASC_N,
                bias_obj["c3_if_casc_n_coarse"],
                bias_obj["c3_if_casc_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_PULSE_PWLK_P,
                bias_obj["c3_pulse_pwlk_p_coarse"],
                bias_obj["c3_pulse_pwlk_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_PS_WEIGHT_INH_S_N,
                bias_obj["c3_ps_weight_inh_s_n_coarse"],
                bias_obj["c3_ps_weight_inh_s_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_PS_WEIGHT_INH_F_N,
                bias_obj["c3_ps_weight_inh_f_n_coarse"],
                bias_obj["c3_ps_weight_inh_f_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_PS_WEIGHT_EXC_S_N,
                bias_obj["c3_ps_weight_exc_s_n_coarse"],
                bias_obj["c3_ps_weight_exc_s_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_PS_WEIGHT_EXC_F_N,
                bias_obj["c3_ps_weight_exc_f_n_coarse"],
                bias_obj["c3_ps_weight_exc_f_n_fine"],
                True, True, True, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_NPDPII_TAU_S_P,
                bias_obj["c3_npdpii_tau_s_p_coarse"],
                bias_obj["c3_npdpii_tau_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_NPDPII_TAU_F_P,
                bias_obj["c3_npdpii_tau_f_p_coarse"],
                bias_obj["c3_npdpii_tau_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_NPDPII_THR_S_P,
                bias_obj["c3_npdpii_thr_s_p_coarse"],
                bias_obj["c3_npdpii_thr_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_NPDPII_THR_F_P,
                bias_obj["c3_npdpii_thr_f_p_coarse"],
                bias_obj["c3_npdpii_thr_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_NPDPIE_TAU_S_P,
                bias_obj["c3_npdpie_tau_s_p_coarse"],
                bias_obj["c3_npdpie_tau_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_NPDPIE_TAU_F_P,
                bias_obj["c3_npdpie_tau_f_p_coarse"],
                bias_obj["c3_npdpie_tau_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_NPDPIE_THR_S_P,
                bias_obj["c3_npdpie_thr_s_p_coarse"],
                bias_obj["c3_npdpie_thr_s_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_NPDPIE_THR_F_P,
                bias_obj["c3_npdpie_thr_f_p_coarse"],
                bias_obj["c3_npdpie_thr_f_p_fine"],
                True, True, False, True))

        self.set_config(
            libcaer.DYNAPSE_CONFIG_CHIP,
            libcaer.DYNAPSE_CONFIG_CHIP_CONTENT,
            libcaer.set_dynapse_bias(
                libcaer.DYNAPSE_CONFIG_BIAS_C3_R2R_P,
                bias_obj["c3_r2r_p_coarse"],
                bias_obj["c3_r2r_p_fine"],
                True, True, False, True))

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

        # Parameters
        param_addr : parameter address
            such as libcaer.DAVIS_CONFIG_BIAS
        param : parameter
            such as libcaer.DAVIS240_CONFIG_BIAS_ONBN

        Returns
        coarse_value : uint
            coarse value
        fine_value :uint
            fine value
        """
        cf_param = libcaer.caerBiasCoarseFineParse(
            self.get_config(param_addr, param))

        return cf_param.coarseValue, cf_param.fineValue

    def get_fpga_bias(self):
        """Get bias settings from FPGA.

        # Returns
        bias_obj : dict
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

    def save_bias_to_json(self, file_path):
        """Save bias to JSON."""
        if self.bias_obj is not None:
            return utils.write_json(file_path, self.bias_obj)
        else:
            return None

    def start_data_stream(self, send_default_config=True):
        """Start streaming data."""
        if send_default_config is True:
            self.send_default_config()
        self.data_start()
        self.set_data_exchange_blocking()

    def core_xy_to_neuron_id(self, core_id, column_x, row_y):
        """Map core ID and column/row address.
        to the correct chip global neuron address.

        # Parameters
        core_id : uint8
            the chip's core ID, range [0,3].
        column_x : uint8
            the neuron's column address, range [0,15].
        row_y : uint8
            the neuron's row address, range [0,15].

        # Returns
        neuron_id : uint16
            chip global neuron address
        """
        return libcaer.caerDynapseCoreXYToNeuronId(
            coreId=core_id,
            columnX=column_x,
            rowY=row_y)

    def core_id_to_neuron_id(self, core_id, neuron_id_core):
        """Map core ID and per-core neuron address.
        to the correct chip global neuron address.

        # Parameters
        core_id : uint8
            the chip's core ID, range [0,3].
        neuron_id_core : uint8
            the neuron's address within this core, range [0,255].

        # Returns
        neuron_id : uint16
            chip global neuron address.
        """
        return libcaer.caerDynapseCoreAddrToNeuronId(
            coreId=core_id,
            neuronAddrCore=neuron_id_core)

    def write_poisson_spikerate(self, neuron_id, rate):
        """Specifies the poisson spike generator's spike rate.

        # Parameters
        neuron_id : uint16
            The target neuron of the poisson spike train, range [0,1023].
        rate : float
            The rate in Hz of the spike train, this will be quantized to the
            nearest supported level, range [0, 4300].

        # Returns
        flag : bool
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

        # Parameters
        neuron_id : uint16
            the neuron to program, range [0,1023]
        sram_id : uint8
            SRAM address, range [0, 3]
        virtual_core_id : utin8
            fake source core ID, set it to this value
            instead of the actual source core ID, range [0,3].
        sx : bool
            X direction, can be one of:
            [DYNAPSE_CONFIG_SRAM_DIRECTION_X_EAST,
             DYNAPSE_CONFIG_SRAM_DIRECTION_X_WEST].
        dx : uint8
            X delta, number of chips to jumps before
            reaching destination, range is [0, 3]
        sy : bool
            Y direction, can be one of:
            [DYNAPSE_CONFIG_SRAM_DIRECTION_Y_NORTH,
             DYNAPSE_CONFIG_SRAM_DIRECTION_Y_SOUTH].
        dy : uint8
            number of chips to jumps before reaching destination,
            range is [0, 3]
        destination_core : uint8
            spike destination core, uses one-hot coding for the 4 cores
            [C3,C2,C1,C0] -> [0,0,0,0] (0 decimal) no core,
            [1,1,1,1] (15 decimal) all cores

        # Returns
        flag : bool
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

        # Parameters
        input_neuron_id : uint16
            the neuron address that should be let in as input to this neuron,
            range [0,1023].
        neuron_id : uint16
            the neuron address whose CAM should be programmed, range [0,1023].
        cam_id : uint8
            CAM address (synapse), each neuron has 64, range [0,63].
        synapse_type : uint8
            one of the four possible synaptic weights:
            [DYNAPSE_CONFIG_CAMTYPE_F_EXC,
             DYNAPSE_CONFIG_CAMTYPE_S_EXC,
             DYNAPSE_CONFIG_CAMTYPE_F_INH,
             DYNAPSE_CONFIG_CAMTYPE_S_INH].

        # Returns
        flag : bool
            True if success, False otherwise
        """
        return libcaer.caerDynapseWriteCam(
            handle=self.handle,
            inputNeuronAddr=input_neuron_id,
            neuronAddr=neuron_id,
            camId=cam_id,
            synapseType=synapse_type)

    def get_event(self):
        """Get Event."""
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
            return None
