"""DAVIS Camera.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from builtins import range
import numpy as np
from pyaer import libcaer
from pyaer.device import USBDevice
from pyaer import utils


class DAVIS(USBDevice):
    """Class for managing single DAVIS device."""
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number=""):
        """DAVIS.

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
        super(DAVIS, self).__init__()
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        # get camera information
        self.obtain_device_info(self.handle)

    def obtain_device_info(self, handle):
        """Obtain DAVIS info."""
        info = libcaer.caerDavisInfoGet(handle)

        self.device_id = info.deviceID
        self.device_serial_number = info.deviceSerialNumber
        self.device_usb_bus_number = info.deviceUSBBusNumber
        self.device_usb_device_address = info.deviceUSBDeviceAddress
        self.device_string = info.deviceString
        self.logic_version = info.logicVersion
        self.device_is_master = info.deviceIsMaster
        self.logic_clock = info.logicClock
        self.adc_clock = info.adcClock
        self.chip_id = info.chipID
        self.dvs_size_X = info.dvsSizeX
        self.dvs_size_Y = info.dvsSizeY
        self.dvs_has_pixel_filter = info.dvsHasPixelFilter
        self.dvs_has_background_activity_filter = \
            info.dvsHasBackgroundActivityFilter
        self.dvs_has_test_event_generator = info.dvsHasTestEventGenerator
        self.aps_size_X = info.apsSizeX
        self.aps_size_Y = info.apsSizeY
        self.aps_color_filter = info.apsColorFilter
        self.aps_has_global_shutter = info.apsHasGlobalShutter
        self.aps_has_quad_ROI = info.apsHasQuadROI
        self.aps_has_external_ADC = info.apsHasExternalADC
        self.aps_has_internal_ADC = info.apsHasInternalADC
        self.ext_input_has_generator = info.extInputHasGenerator
        self.ext_input_has_extra_detectors = \
            info.extInputHasExtraDetectors
        self.dvs_has_ROI_filter = info.dvsHasROIFilter
        self.dvs_has_statistics = info.dvsHasStatistics
        self.mux_has_statistics = info.muxHasStatistics
        # auto-exposure
        self.min_exposure = 10
        self.max_exposure = 25000
        self.proportion_to_cut = 0.25

    def open(self,
             device_id=1,
             bus_number_restrict=0,
             dev_address_restrict=0,
             serial_number=""):
        """Open DAVIS device.

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
        super(DAVIS, self).open(
            libcaer.CAER_DEVICE_DAVIS, device_id,
            bus_number_restrict, dev_address_restrict,
            serial_number)

    def set_bias_from_json(self, file_path, verbose=False):
        """Set bias from loading JSON configuration file.

        # Parameters
        file_path : string
            absolute path of the JSON bias file.
        """
        bias_obj = utils.load_dvs_bias(file_path, verbose)
        self.set_bias(bias_obj)

    def set_bias(self, bias_obj):
        """Set bias from bias dictionary.

        # Parameters
        bias_obj : dict
            dictionary that contains DVS128 biases.

        # Returns
        flag : bool
            True if set successful, False otherwise.
            TODO: make this flag check possible
        """
        # global setting of DAVIS
        self.set_config(libcaer.DAVIS_CONFIG_APS,
                        libcaer.DAVIS_CONFIG_APS_EXPOSURE,
                        bias_obj["exposure"])
        self.set_config(libcaer.DAVIS_CONFIG_APS,
                        libcaer.DAVIS_CONFIG_APS_FRAME_DELAY,
                        bias_obj["frame_delay"])
        self.set_config(libcaer.DAVIS_CONFIG_APS,
                        libcaer.DAVIS_CONFIG_APS_RUN,
                        bias_obj["aps_enabled"])
        self.set_config(libcaer.DAVIS_CONFIG_DVS,
                        libcaer.DAVIS_CONFIG_DVS_RUN,
                        bias_obj["dvs_enabled"])
        self.set_config(libcaer.DAVIS_CONFIG_IMU,
                        libcaer.DAVIS_CONFIG_IMU_RUN,
                        bias_obj["imu_enabled"])
        # IMU settings of DAVIS
        if 0 <= bias_obj["imu_gyro_scale"] <= 3:
            self.set_config(libcaer.DAVIS_CONFIG_IMU,
                            libcaer.DAVIS_CONFIG_IMU_GYRO_FULL_SCALE,
                            bias_obj["imu_gyro_scale"])

        if 0 <= bias_obj["imu_acc_scale"] <= 3:
            self.set_config(libcaer.DAVIS_CONFIG_IMU,
                            libcaer.DAVIS_CONFIG_IMU_ACCEL_FULL_SCALE,
                            bias_obj["imu_acc_scale"])

        if 0 <= bias_obj["imu_low_pass_filter"] <= 6:
            self.set_config(
                libcaer.DAVIS_CONFIG_IMU,
                libcaer.DAVIS_CONFIG_IMU_DIGITAL_LOW_PASS_FILTER,
                bias_obj["imu_low_pass_filter"])
            if bias_obj["imu_low_pass_filter"] == 0:
                self.set_config(
                    libcaer.DAVIS_CONFIG_IMU,
                    libcaer.DAVIS_CONFIG_IMU_SAMPLE_RATE_DIVIDER,
                    7)
            else:
                self.set_config(
                    libcaer.DAVIS_CONFIG_IMU,
                    libcaer.DAVIS_CONFIG_IMU_SAMPLE_RATE_DIVIDER,
                    0)

        if self.chip_id == libcaer.DAVIS_CHIP_DAVIS346B:
            # VDAC
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_APSOVERFLOWLEVEL,
                libcaer.vdac_set(27, 6))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_APSCAS,
                libcaer.vdac_set(21, 6))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_ADCREFHIGH,
                libcaer.vdac_set(
                    bias_obj["ADC_RefHigh_volt"],
                    bias_obj["ADC_RefHigh_current"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_ADCREFLOW,
                libcaer.vdac_set(
                    bias_obj["ADC_RefLow_volt"],
                    bias_obj["ADC_RefLow_current"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_ADCTESTVOLTAGE,
                libcaer.vdac_set(21, 7))
            # CF biases
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_LOCALBUFBN,
                libcaer.cf_n_type_set(5, 164))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_PADFOLLBN,
                libcaer.cf_n_type_set(7, 215))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_DIFFBN,
                libcaer.cf_n_type_set(
                    bias_obj["DiffBn_coarse"],
                    bias_obj["DiffBn_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_ONBN,
                libcaer.cf_n_type_set(
                    bias_obj["ONBn_coarse"],
                    bias_obj["ONBn_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_OFFBN,
                libcaer.cf_n_type_set(
                    bias_obj["OFFBn_coarse"],
                    bias_obj["OFFBn_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_PIXINVBN,
                libcaer.cf_n_type_set(5, 129))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_PRBP,
                libcaer.cf_p_type_set(
                    bias_obj["PrBp_coarse"],
                    bias_obj["PrBp_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_PRSFBP,
                libcaer.cf_p_type_set(
                    bias_obj["PrSFBp_coarse"],
                    bias_obj["PrSFBp_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_REFRBP,
                libcaer.cf_p_type_set(
                    bias_obj["RefrBp_coarse"],
                    bias_obj["RefrBp_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_READOUTBUFBP,
                libcaer.cf_p_type_set(6, 20))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_APSROSFBN,
                libcaer.cf_n_type_set(6, 219))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_ADCCOMPBP,
                libcaer.cf_p_type_set(5, 20))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_COLSELLOWBN,
                libcaer.cf_n_type_set(0, 1))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_DACBUFBP,
                libcaer.cf_p_type_set(6, 60))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_LCOLTIMEOUTBN,
                libcaer.cf_n_type_set(5, 49))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_AEPDBN,
                libcaer.cf_n_type_set(6, 91))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_AEPUXBP,
                libcaer.cf_p_type_set(4, 80))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_AEPUYBP,
                libcaer.cf_p_type_set(7, 152))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_IFREFRBN,
                libcaer.cf_n_type_set(5, 255))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_IFTHRBN,
                libcaer.cf_n_type_set(5, 255))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_BIASBUFFER,
                libcaer.cf_n_type_set(5, 254))
            # Special Biases
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_SSP,
                libcaer.shiftsource_set(1, 33, libcaer.SHIFTED_SOURCE))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_SSN,
                libcaer.shiftsource_set(1, 33, libcaer.SHIFTED_SOURCE))

            if self.dvs_has_background_activity_filter:
                self.set_config(
                    libcaer.DAVIS_CONFIG_DVS,
                    libcaer.DAVIS_CONFIG_DVS_FILTER_BACKGROUND_ACTIVITY,
                    bias_obj["background_activity_filter_enabled"])
                self.set_config(
                    libcaer.DAVIS_CONFIG_DVS,
                    libcaer.DAVIS_CONFIG_DVS_FILTER_BACKGROUND_ACTIVITY_TIME,
                    bias_obj["background_activity_filter_time"])
                self.set_config(
                    libcaer.DAVIS_CONFIG_DVS,
                    libcaer.DAVIS_CONFIG_DVS_FILTER_REFRACTORY_PERIOD,
                    bias_obj["refractory_period_enabled"])
                self.set_config(
                    libcaer.DAVIS_CONFIG_DVS,
                    libcaer.DAVIS_CONFIG_DVS_FILTER_REFRACTORY_PERIOD_TIME,
                    bias_obj["refractory_period_time"])

        elif self.chip_id == libcaer.DAVIS_CHIP_DAVIS240C:
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_PRBP,
                libcaer.cf_p_type_set(
                    bias_obj["PrBp_coarse"],
                    bias_obj["PrBp_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_PRSFBP,
                libcaer.cf_p_type_set(
                    bias_obj["PrSFBp_coarse"],
                    bias_obj["PrSFBp_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_DIFFBN,
                libcaer.cf_n_type_set(
                    bias_obj["DiffBn_coarse"],
                    bias_obj["DiffBn_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_ONBN,
                libcaer.cf_n_type_set(
                    bias_obj["ONBn_coarse"],
                    bias_obj["ONBn_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_OFFBN,
                libcaer.cf_n_type_set(
                    bias_obj["OFFBn_coarse"],
                    bias_obj["OFFBn_fine"]))
            self.set_config(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_REFRBP,
                libcaer.cf_p_type_set(
                    bias_obj["RefrBp_coarse"],
                    bias_obj["RefrBp_fine"]))

    def get_bias(self):
        """Get bias settings.

        # Returns
        bias_obj : dict
            dictionary that contains DVS128 current bias settings.
        """
        bias_obj = {}
        # global setting of DAVIS
        bias_obj["exposure"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_EXPOSURE)
        bias_obj["frame_delay"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_FRAME_DELAY)
        bias_obj["aps_enabled"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_RUN)
        bias_obj["dvs_enabled"] = self.get_config(
            libcaer.DAVIS_CONFIG_DVS,
            libcaer.DAVIS_CONFIG_DVS_RUN)
        bias_obj["imu_enabled"] = self.get_config(
            libcaer.DAVIS_CONFIG_IMU,
            libcaer.DAVIS_CONFIG_IMU_RUN)
        # IMU settings of DAVIS
        bias_obj["imu_gyro_scale"] = self.get_config(
            libcaer.DAVIS_CONFIG_IMU,
            libcaer.DAVIS_CONFIG_IMU_GYRO_FULL_SCALE)
        bias_obj["imu_acc_scale"] = self.get_config(
            libcaer.DAVIS_CONFIG_IMU,
            libcaer.DAVIS_CONFIG_IMU_ACCEL_FULL_SCALE)
        bias_obj["imu_low_pass_filter"] = self.get_config(
            libcaer.DAVIS_CONFIG_IMU,
            libcaer.DAVIS_CONFIG_IMU_DIGITAL_LOW_PASS_FILTER)

        if self.chip_id == libcaer.DAVIS_CHIP_DAVIS346B:
            # VDAC
            adc_ref_high = libcaer.caerBiasVDACParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_ADCREFHIGH))
            bias_obj["ADC_RefHigh_volt"] = adc_ref_high.voltageValue
            bias_obj["ADC_RefHigh_current"] = adc_ref_high.currentValue

            adc_ref_low = libcaer.caerBiasVDACParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_ADCREFLOW))
            bias_obj["ADC_RefLow_volt"] = adc_ref_low.voltageValue
            bias_obj["ADC_RefLow_current"] = adc_ref_low.currentValue

            prbp_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_PRBP))
            bias_obj["PrBp_coarse"] = prbp_cf.coarseValue
            bias_obj["PrBp_fine"] = prbp_cf.fineValue

            prsfbp_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_PRSFBP))
            bias_obj["PrSFBp_coarse"] = prsfbp_cf.coarseValue
            bias_obj["PrSFPb_fine"] = prsfbp_cf.fineValue

            diffbn_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_DIFFBN))
            bias_obj["DiffBn_coarse"] = diffbn_cf.coarseValue
            bias_obj["DiffBn_fine"] = diffbn_cf.fineValue

            onbn_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_ONBN))
            bias_obj["ONBn_coarse"] = onbn_cf.coarseValue
            bias_obj["ONBn_fine"] = onbn_cf.fineValue

            offbn_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_OFFBN))
            bias_obj["OFFBn_coarse"] = offbn_cf.coarseValue
            bias_obj["OFFBn_fine"] = offbn_cf.fineValue

            refrbp_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_REFRBP))
            bias_obj["RefrBp_coarse"] = refrbp_cf.coarseValue
            bias_obj["RefrBp_fine"] = refrbp_cf.fineValue

            if self.dvs_has_background_activity_filter:
                bias_obj["background_activity_filter_enabled"] = \
                    self.get_config(
                        libcaer.DAVIS_CONFIG_DVS,
                        libcaer.DAVIS_CONFIG_DVS_FILTER_BACKGROUND_ACTIVITY)
                bias_obj["background_activity_filter_time"] = self.set_config(
                    libcaer.DAVIS_CONFIG_DVS,
                    libcaer.DAVIS_CONFIG_DVS_FILTER_BACKGROUND_ACTIVITY_TIME)

                bias_obj["refractory_period_enabled"] = \
                    self.get_config(
                        libcaer.DAVIS_CONFIG_DVS,
                        libcaer.DAVIS_CONFIG_DVS_FILTER_REFRACTORY_PERIOD)
                bias_obj["refractory_period_time"] = \
                    self.get_config(
                        libcaer.DAVIS_CONFIG_DVS,
                        libcaer.DAVIS_CONFIG_DVS_FILTER_REFRACTORY_PERIOD_TIME)

        elif self.chip_id == libcaer.DAVIS_CHIP_DAVIS240C:
            prbp_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_PRBP))
            bias_obj["PrBp_coarse"] = prbp_cf.coarseValue
            bias_obj["PrBp_fine"] = prbp_cf.fineValue

            prsfbp_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_PRSFBP))
            bias_obj["PrSFBp_coarse"] = prsfbp_cf.coarseValue
            bias_obj["PrSFPb_fine"] = prsfbp_cf.fineValue

            diffbn_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_DIFFBN))
            bias_obj["DiffBn_coarse"] = diffbn_cf.coarseValue
            bias_obj["DiffBn_fine"] = diffbn_cf.fineValue

            onbn_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_ONBN))
            bias_obj["ONBn_coarse"] = onbn_cf.coarseValue
            bias_obj["ONBn_fine"] = onbn_cf.fineValue

            offbn_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_OFFBN))
            bias_obj["OFFBn_coarse"] = offbn_cf.coarseValue
            bias_obj["OFFBn_fine"] = offbn_cf.fineValue

            refrbp_cf = libcaer.caerBiasCoarseFineParse(
                self.get_config(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_REFRBP))
            bias_obj["RefrBp_coarse"] = refrbp_cf.coarseValue
            bias_obj["RefrBp_fine"] = refrbp_cf.fineValue
        return bias_obj

    def get_aps_bias(self):
        """Get APS biases."""
        aps_bias_obj = {}
        aps_bias_obj["column_settle"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_COLUMN_SETTLE)
        aps_bias_obj["exposure"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_EXPOSURE)
        aps_bias_obj["frame_delay"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_FRAME_DELAY)
        aps_bias_obj["global_shutter"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_GLOBAL_SHUTTER)
        aps_bias_obj["null_settle"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_NULL_SETTLE)
        aps_bias_obj["reset_read"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_RESET_READ)
        aps_bias_obj["reset_settle"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_RESET_SETTLE)
        aps_bias_obj["aps_enabled"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_RUN)
        aps_bias_obj["wait_on_tranfer_stall"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_WAIT_ON_TRANSFER_STALL)
        aps_bias_obj["autoexposure_enabled"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_AUTOEXPOSURE)

        return aps_bias_obj

    def save_bias_to_json(self, file_path):
        """Save bias to JSON."""
        bias_obj = self.get_bias()
        return utils.write_json(file_path, bias_obj)

    def start_data_stream(self):
        """Start streaming data."""
        self.data_start()
        self.set_data_exchange_blocking()

    def compute_new_exposure(self, frame, current_exposure,
                             desired_intensity,
                             autoexposure_gain):
        """Compute new exposure if auto-exposure is enabled.

        # Parameters
        frame : numpy.ndarray
            the input frame
        current_exposure : int
            current exposure value
        desired_intensity : float
            desired intensity value
        autoexposure_gain : float
            autoexposure gain

        # Returns
        new_exposure : int
            new exposure value
        """
        current_intensity = utils.trim_mean(frame, self.proportion_to_cut)

        err = desired_intensity-current_intensity
        delta_exposure = current_exposure*autoexposure_gain/1000.*err
        new_exposure = int(current_exposure+delta_exposure+0.5)

        return utils.clip(new_exposure, self.min_exposure, self.max_exposure)

    def get_event(self):
        """Get Event.

        Maybe not so efficient.
        """
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None:
            num_pol_event = 0
            num_special_event = 0
            num_imu_event = 0
            pol_ts = None
            pol_xy = None
            pol_pol = None
            special_ts = None
            special_event_data = None
            frames = []
            frames_ts = []
            imu_acc = None
            imu_gyro = None
            imu_ts = None
            imu_temp = None
            for packet_id in range(packet_number):
                packet_header, packet_type = self.get_packet_header(
                    packet_container, packet_id)
                if packet_type == libcaer.POLARITY_EVENT:
                    ts, xy, pol, num_events = self.get_polarity_event(
                        packet_header)
                    pol_ts = np.hstack((pol_ts, ts)) \
                        if pol_ts is not None else ts
                    pol_xy = np.hstack((pol_xy, xy)) \
                        if pol_xy is not None else xy
                    pol_pol = np.hstack((pol_pol, pol)) \
                        if pol_pol is not None else pol
                    num_pol_event += num_events
                elif packet_type == libcaer.SPECIAL_EVENT:
                    ts, event_data, num_events = self.get_special_event(
                        packet_header)
                    special_ts = np.hstack((special_ts, ts)) \
                        if special_ts is not None else special_ts
                    special_event_data = np.hstack(
                        (special_event_data, event_data)) \
                        if special_event_data is not None \
                        else special_event_data
                    num_special_event += num_events
                elif packet_type == libcaer.FRAME_EVENT:
                    frame_mat, frame_ts = self.get_frame_event(
                        packet_header)
                    frames.append(frame_mat)
                    frames_ts.append(frame_ts)
                elif packet_type == libcaer.IMU6_EVENT:
                    ts, acc, gyro, temp, num_events = self.get_imu6_event(
                        packet_header)
                    imu_acc = np.hstack((imu_acc, acc)) \
                        if imu_acc is not None else acc
                    imu_gyro = np.hstack((imu_gyro, gyro)) \
                        if imu_gyro is not None else gyro
                    imu_ts = np.hstack((imu_ts, ts)) \
                        if imu_ts is not None else ts
                    imu_temp = np.hstack((imu_temp, temp)) \
                        if imu_temp is not None else temp
                    num_imu_event += num_events

            # post processing with frames
            frames = np.array(frames, dtype=np.uint16)
            frames_ts = np.array(frames_ts, dtype=np.uint64)

            return (pol_ts, pol_xy, pol_pol, num_pol_event,
                    special_ts, special_event_data, num_special_event,
                    frames_ts, frames, imu_ts, imu_acc, imu_gyro, imu_temp,
                    num_imu_event)
        else:
            return None
