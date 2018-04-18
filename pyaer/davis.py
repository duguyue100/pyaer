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

        # coarse fine setting functions
        self.cf_set = {"n_type": libcaer.cf_n_type_set,
                       "p_type": libcaer.cf_p_type_set,
                       "n_cas_type": libcaer.cf_n_type_cas_set,
                       "n_off_type": libcaer.cf_n_type_off_set,
                       "p_off_type": libcaer.cf_p_type_off_set,
                       "vdac": libcaer.vdac_set}

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
        bias_obj = utils.load_davis_bias(file_path, verbose)
        self.set_bias(bias_obj)

    def set_cf_bias(self, param_addr, param, coarse, fine, mode):
        """Setting coarse fine bias.

        # Parameter
        param_addr : parameter address
            such as libcaer.DAVIS_CONFIG_BIAS
        param : parameter
            such as libcaer.DAVIS240_CONFIG_BIAS_ONBN
        coarse : int
            coarae value
        fine : int
            fine value
        mode : setting mode
            n_type, p_type, n_cas_type, n_off_type, p_off_type, vdac
        """
        return self.set_config(
            param_addr, param,
            self.cf_set[mode](coarse, fine))

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
        # output soruces settings
        self.set_config(libcaer.DAVIS_CONFIG_APS,
                        libcaer.DAVIS_CONFIG_APS_RUN,
                        bias_obj["aps_enabled"])
        self.set_config(libcaer.DAVIS_CONFIG_DVS,
                        libcaer.DAVIS_CONFIG_DVS_RUN,
                        bias_obj["dvs_enabled"])
        self.set_config(libcaer.DAVIS_CONFIG_IMU,
                        libcaer.DAVIS_CONFIG_IMU_RUN,
                        bias_obj["imu_enabled"])

        # global settings for APS
        self.set_config(libcaer.DAVIS_CONFIG_APS,
                        libcaer.DAVIS_CONFIG_APS_EXPOSURE,
                        bias_obj["exposure"])
        self.set_config(libcaer.DAVIS_CONFIG_APS,
                        libcaer.DAVIS_CONFIG_APS_AUTOEXPOSURE,
                        bias_obj["autoexposure"])
        self.set_config(libcaer.DAVIS_CONFIG_APS,
                        libcaer.DAVIS_CONFIG_APS_FRAME_DELAY,
                        bias_obj["frame_delay"])

        # global setting of DAVIS
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
            # APSOverflowLevel
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_APSOVERFLOWLEVEL,
                27, 6, "vdac")

            # APSCas
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_APSCAS,
                21, 6, "vdac")

            # ADC_RefHigh_volt
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_ADCREFHIGH,
                bias_obj["ADC_RefHigh_volt"],
                bias_obj["ADC_RefHigh_curr"], "vdac")

            # ADC_RefLow_volt
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_ADCREFLOW,
                bias_obj["ADC_RefLow_volt"],
                bias_obj["ADC_RefLow_curr"], "vdac")

            # ADCTestVoltage
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_ADCTESTVOLTAGE,
                21, 7, "vdac")

            # CF biases
            # LocalBufBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_LOCALBUFBN,
                bias_obj["LocalBufBn_coarse"],
                bias_obj["LocalBufBn_fine"],
                "n_type")

            # PadFollBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_PADFOLLBN,
                bias_obj["PadFollBn_coarse"],
                bias_obj["PadFollBn_fine"],
                "n_type")

            # DiffBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_DIFFBN,
                bias_obj["DiffBn_coarse"],
                bias_obj["DiffBn_fine"],
                "n_type")

            # ONBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_ONBN,
                bias_obj["ONBn_coarse"],
                bias_obj["ONBn_fine"],
                "n_type")

            # OFFBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_OFFBN,
                bias_obj["OFFBn_coarse"],
                bias_obj["OFFBn_fine"],
                "n_type")

            # PixInvBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_PIXINVBN,
                bias_obj["PixInvBn_coarse"],
                bias_obj["PixInvBn_fine"],
                "n_type")

            # PrBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_PRBP,
                bias_obj["PrBp_coarse"],
                bias_obj["PrBp_fine"],
                "p_type")

            # PrSFBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_PRSFBP,
                bias_obj["PrSFBp_coarse"],
                bias_obj["PrSFBp_fine"],
                "p_type")

            # RefrBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_REFRBP,
                bias_obj["RefrBp_coarse"],
                bias_obj["RefrBp_fine"],
                "p_type")

            # ReadoutBufBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_READOUTBUFBP,
                bias_obj["ReadoutBufBp_coarse"],
                bias_obj["ReadoutBufBp_fine"],
                "p_type")

            # APSROSFBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_APSROSFBN,
                bias_obj["APSROSFBn_coarse"],
                bias_obj["APSROSFBn_fine"],
                "n_type")

            # ADCCompBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_ADCCOMPBP,
                bias_obj["ADCCompBp_coarse"],
                bias_obj["ADCCompBp_fine"],
                "p_type")

            # COLSELLowBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_COLSELLOWBN,
                bias_obj["COLSELLowBn_coarse"],
                bias_obj["COLSELLowBn_fine"],
                "n_type")

            # DACBufBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_DACBUFBP,
                bias_obj["DACBufBp_coarse"],
                bias_obj["DACBufBp_fine"],
                "p_type")

            # LcolTimeoutBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_LCOLTIMEOUTBN,
                bias_obj["LcolTimeoutBn_coarse"],
                bias_obj["LcolTimeoutBn_fine"],
                "n_type")

            # AEPdBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_AEPDBN,
                bias_obj["AEPdBn_coarse"],
                bias_obj["AEPdBn_fine"],
                "n_type")

            # AEPuXBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_AEPUXBP,
                bias_obj["AEPuXBp_coarse"],
                bias_obj["AEPuXBp_fine"],
                "p_type")

            # AEPuYBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_AEPUYBP,
                bias_obj["AEPuYBp_coarse"],
                bias_obj["AEPuYBp_fine"],
                "p_type")

            # IFRefrBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_IFREFRBN,
                bias_obj["IFRefrBn_coarse"],
                bias_obj["IFRefrBn_fine"],
                "n_type")

            # IFThrBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_IFTHRBN,
                bias_obj["IFThrBn_coarse"],
                bias_obj["IFThrBn_fine"],
                "n_type")

            # BiasBuffer
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS346_CONFIG_BIAS_BIASBUFFER,
                bias_obj["BiasBuffer_coarse"],
                bias_obj["BiasBuffer_fine"],
                "n_type")

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
            # DiffBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_DIFFBN,
                bias_obj["DiffBn_coarse"],
                bias_obj["DiffBn_fine"],
                "n_type")

            # ONBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_ONBN,
                bias_obj["ONBn_coarse"],
                bias_obj["ONBn_fine"],
                "n_type")

            # OFFBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_OFFBN,
                bias_obj["OFFBn_coarse"],
                bias_obj["OFFBn_fine"],
                "n_type")

            # APSCasEPC
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_APSCASEPC,
                bias_obj["APSCasEPC_coarse"],
                bias_obj["APSCasEPC_fine"],
                "n_cas_type")

            # DiffCasBNC
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_DIFFCASBNC,
                bias_obj["DiffCasBNC_coarse"],
                bias_obj["DiffCasBNC_fine"],
                "n_cas_type")

            # APSROSFBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_APSROSFBN,
                bias_obj["APSROSFBn_coarse"],
                bias_obj["APSROSFBn_fine"],
                "n_type")

            # LocalBufBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_LOCALBUFBN,
                bias_obj["LocalBufBn_coarse"],
                bias_obj["LocalBufBn_fine"],
                "n_type")

            # PixInvBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_PIXINVBN,
                bias_obj["PixInvBn_coarse"],
                bias_obj["PixInvBn_fine"],
                "n_type")

            # PrBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_PRBP,
                bias_obj["PrBp_coarse"],
                bias_obj["PrBp_fine"],
                "p_type")

            # PrSFBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_PRSFBP,
                bias_obj["PrSFBp_coarse"],
                bias_obj["PrSFBp_fine"],
                "p_type")

            # RefrBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_REFRBP,
                bias_obj["RefrBp_coarse"],
                bias_obj["RefrBp_fine"],
                "p_type")

            # AEPdBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_AEPDBN,
                bias_obj["AEPdBn_coarse"],
                bias_obj["AEPdBn_fine"],
                "n_type")

            # LcolTimeoutBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_LCOLTIMEOUTBN,
                bias_obj["LcolTimeoutBn_coarse"],
                bias_obj["LcolTimeoutBn_fine"],
                "n_type")

            # AEPuXBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_AEPUXBP,
                bias_obj["AEPuXBp_coarse"],
                bias_obj["AEPuXBp_fine"],
                "p_type")

            # AEPuYBp
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_AEPUYBP,
                bias_obj["AEPuYBp_coarse"],
                bias_obj["AEPuYBp_fine"],
                "p_type")

            # IFThrBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_IFTHRBN,
                bias_obj["IFThrBn_coarse"],
                bias_obj["IFThrBn_fine"],
                "n_type")

            # IFRefrBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_IFREFRBN,
                bias_obj["IFRefrBn_coarse"],
                bias_obj["IFRefrBn_fine"],
                "n_type")

            # PadFollBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_PADFOLLBN,
                bias_obj["PadFollBn_coarse"],
                bias_obj["PadFollBn_fine"],
                "n_type")

            # APSOverflowLevelBn
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_APSOVERFLOWLEVELBN,
                bias_obj["APSOverflowLevelBn_coarse"],
                bias_obj["APSOverflowLevelBn_fine"],
                "n_type")

            # BiasBuffer
            self.set_cf_bias(
                libcaer.DAVIS_CONFIG_BIAS,
                libcaer.DAVIS240_CONFIG_BIAS_BIASBUFFER,
                bias_obj["BiasBuffer_coarse"],
                bias_obj["BiasBuffer_fine"],
                "n_type")

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

    def get_bias(self):
        """Get bias settings.

        # Returns
        bias_obj : dict
            dictionary that contains DVS128 current bias settings.
        """
        bias_obj = {}
        # output sources
        bias_obj["aps_enabled"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_RUN)
        bias_obj["dvs_enabled"] = self.get_config(
            libcaer.DAVIS_CONFIG_DVS,
            libcaer.DAVIS_CONFIG_DVS_RUN)
        bias_obj["imu_enabled"] = self.get_config(
            libcaer.DAVIS_CONFIG_IMU,
            libcaer.DAVIS_CONFIG_IMU_RUN)

        # global settings for APS
        bias_obj["exposure"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_EXPOSURE)
        bias_obj["autoexposure"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_AUTOEXPOSURE)
        bias_obj["frame_delay"] = self.get_config(
            libcaer.DAVIS_CONFIG_APS,
            libcaer.DAVIS_CONFIG_APS_FRAME_DELAY)

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

            # CF biases
            # LocalBufBn
            bias_obj["LocalBufBn_coarse"], bias_obj["LocalBufBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_LOCALBUFBN)

            # PadFollBn
            bias_obj["PadFollBn_coarse"], bias_obj["PadFollBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_PADFOLLBN)

            # DiffBn
            bias_obj["DiffBn_coarse"], bias_obj["DiffBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_DIFFBN)

            # ONBn
            bias_obj["ONBn_coarse"], bias_obj["ONBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_ONBN)

            # OFFBn
            bias_obj["OFFBn_coarse"], bias_obj["OFFBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_OFFBN)

            # PixInvBn
            bias_obj["PixInvBn_coarse"], bias_obj["PixInvBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_PIXINVBN)

            # PrBp
            bias_obj["PrBp_coarse"], bias_obj["PrBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_PRBP)

            # PrSFBp
            bias_obj["PrSFBp_coarse"], bias_obj["PrSFPb_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_PRSFBP)

            # RefrBp
            bias_obj["RefrBp_coarse"], bias_obj["RefrBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_REFRBP)

            # ReadoutBufBp
            bias_obj["ReadoutBufBp_coarse"], bias_obj["ReadoutBufBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_READOUTBUFBP)

            # APSROSFBn
            bias_obj["APSROSFBn_coarse"], bias_obj["APSROSFBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_APSROSFBN)

            # ADCCompBp
            bias_obj["ADCCompBp_coarse"], bias_obj["ADCCompBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_ADCCOMPBP)

            # COLSELLowBn
            bias_obj["COLSELLowBn_coarse"], bias_obj["COLSELLowBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_COLSELLOWBN)

            # DACBufBp
            bias_obj["DACBufBp_coarse"], bias_obj["DACBufBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_DACBUFBP)

            # LcolTimeoutBn
            (bias_obj["LcolTimeoutBn_coarse"],
             bias_obj["LcolTimeoutBn_fine"]) = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_LCOLTIMEOUTBN)

            # AEPdBn
            bias_obj["AEPdBn_coarse"], bias_obj["AEPdBn_fien"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_AEPDBN)

            # AEPuXBp
            bias_obj["AEPuXBp_coarse"], bias_obj["AEPuXBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_AEPUXBP)

            # AEPuYBp
            bias_obj["AEPuYBp_coarse"], bias_obj["AEPuYBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_AEPUYBP)

            # IFRefrBn
            bias_obj["IFRefrBn_coarse"], bias_obj["IFRefrBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_IFREFRBN)

            # IFThrBn
            bias_obj["IFThrBn_coarse"], bias_obj["IFThrBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_IFTHRBN)

            # BiasBuffer
            bias_obj["BiasBuffer_coarse"], bias_obj["BiasBuffer_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS346_CONFIG_BIAS_BIASBUFFER)

            if self.dvs_has_background_activity_filter:
                bias_obj["background_activity_filter_enabled"] = \
                    self.get_config(
                        libcaer.DAVIS_CONFIG_DVS,
                        libcaer.DAVIS_CONFIG_DVS_FILTER_BACKGROUND_ACTIVITY)
                bias_obj["background_activity_filter_time"] = self.get_config(
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
            # DiffBn
            bias_obj["DiffBn_coarse"], bias_obj["DiffBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_DIFFBN)

            # ONBn
            bias_obj["ONBn_coarse"], bias_obj["ONBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_ONBN)

            # OFFBn
            bias_obj["OFFBn_coarse"], bias_obj["OFFBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_OFFBN)

            # APSCasEPC
            bias_obj["APSCasEPC_coarse"], bias_obj["APSCasEPC_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_APSCASEPC)

            # DiffCasBNC
            bias_obj["DiffCasBNC_coarse"], bias_obj["DiffCasBNC_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_DIFFCASBNC)

            # APSROSFBn
            bias_obj["APSROSFBn_coarse"], bias_obj["APSROSFBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_APSROSFBN)

            # LocalBufBn
            bias_obj["LocalBufBn_coarse"], bias_obj["LocalBufBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_LOCALBUFBN)

            # PixInvBn
            bias_obj["PixInvBn_coarse"], bias_obj["PixInvBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_PIXINVBN)

            # PrBp
            bias_obj["PrBp_coarse"], bias_obj["PrBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_PRBP)

            # PrSFBp
            bias_obj["PrSFBp_coarse"], bias_obj["PrSFPb_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_PRSFBP)

            # RefrBp
            bias_obj["RefrBp_coarse"], bias_obj["RefrBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_REFRBP)

            # AEPdBn
            bias_obj["AEPdBn_coarse"], bias_obj["AEPdBn_fien"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_AEPDBN)

            # LcolTimeoutBn
            (bias_obj["LcolTimeoutBn_coarse"],
             bias_obj["LcolTimeoutBn_fine"]) = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_LCOLTIMEOUTBN)

            # AEPuXBp
            bias_obj["AEPuXBp_coarse"], bias_obj["AEPuXBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_AEPUXBP)

            # AEPuYBp
            bias_obj["AEPuYBp_coarse"], bias_obj["AEPuYBp_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_AEPUYBP)

            # IFThrBn
            bias_obj["IFThrBn_coarse"], bias_obj["IFThrBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_IFTHRBN)

            # IFRefrBn
            bias_obj["IFRefrBn_coarse"], bias_obj["IFRefrBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_IFREFRBN)

            # PadFollBn
            bias_obj["PadFollBn_coarse"], bias_obj["PadFollBn_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_PADFOLLBN)

            # APSOverflowLevelBn
            (bias_obj["APSOverflowLevelBn_coarse"],
             bias_obj["APSOverflowLevelBn_fine"]) = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_APSOVERFLOWLEVELBN)

            # BiasBuffer
            bias_obj["BiasBuffer_coarse"], bias_obj["BiasBuffer_fine"] = \
                self.get_cf_bias(
                    libcaer.DAVIS_CONFIG_BIAS,
                    libcaer.DAVIS240_CONFIG_BIAS_BIASBUFFER)

        return bias_obj

    def save_bias_to_json(self, file_path):
        """Save bias to JSON."""
        bias_obj = self.get_bias()
        return utils.write_json(file_path, bias_obj)

    def start_data_stream(self, send_default_config=True):
        """Start streaming data."""
        if send_default_config is True:
            self.send_default_config()
        self.data_start()
        self.set_data_exchange_blocking()

    def get_event(self):
        """Get Event."""
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None:
            num_pol_event = 0
            num_special_event = 0
            num_imu_event = 0
            pol_events = None
            special_events = None
            frames = []
            frames_ts = []
            imu_events = None
            for packet_id in range(packet_number):
                packet_header, packet_type = self.get_packet_header(
                    packet_container, packet_id)
                if packet_type == libcaer.POLARITY_EVENT:
                    events, num_events = self.get_polarity_event(
                        packet_header)
                    pol_events = np.hstack((pol_events, events)) \
                        if pol_events is not None else events
                    num_pol_event += num_events
                elif packet_type == libcaer.SPECIAL_EVENT:
                    events, num_events = self.get_special_event(
                        packet_header)
                    special_events = np.hstack((special_events, events)) \
                        if special_events is not None else events
                    num_special_event += num_events
                elif packet_type == libcaer.FRAME_EVENT:
                    frame_mat, frame_ts = self.get_frame_event(
                        packet_header)
                    frames.append(frame_mat)
                    frames_ts.append(frame_ts)
                elif packet_type == libcaer.IMU6_EVENT:
                    events, num_events = self.get_imu6_event(
                        packet_header)
                    imu_events = np.hstack((imu_events, events)) \
                        if imu_events is not None else events
                    num_imu_event += num_events

            # post processing with frames
            frames = np.array(frames, dtype=np.uint8)
            frames_ts = np.array(frames_ts, dtype=np.uint64)

            libcaer.caerEventPacketContainerFree(packet_container)

            return (pol_events, num_pol_event,
                    special_events, num_special_event,
                    frames_ts, frames, imu_events,
                    num_imu_event)
        else:
            return None


class DAVISFX2(DAVIS):
    """DAVIS FX2."""
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number=""):
        """DAVIS FX2.

        TODO: there may be more features to write

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
        super(DAVISFX2, self).__init__()
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        # get camera information
        self.obtain_device_info(self.handle)

    def open(self,
             device_id=1,
             bus_number_restrict=0,
             dev_address_restrict=0,
             serial_number=""):
        """Open DAVIS FX2 device.

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
        USBDevice.open(libcaer.CAER_DEVICE_DAVIS_FX2, device_id,
                       bus_number_restrict, dev_address_restrict,
                       serial_number)


class DAVISFX3(DAVIS):
    """DAVIS FX3."""
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number=""):
        """DAVIS FX3.

        TODO: there may be more features to write

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
        super(DAVISFX3, self).__init__()
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        # get camera information
        self.obtain_device_info(self.handle)

    def open(self,
             device_id=1,
             bus_number_restrict=0,
             dev_address_restrict=0,
             serial_number=""):
        """Open DAVIS FX3 device.

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
        USBDevice.open(libcaer.CAER_DEVICE_DAVIS_FX3, device_id,
                       bus_number_restrict, dev_address_restrict,
                       serial_number)


class DAVISRPI(DAVIS):
    """DAVIS RPI."""
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number=""):
        """DAVIS RPI.

        TODO: there may be more features to write

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
        super(DAVISRPI, self).__init__()
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        # get camera information
        self.obtain_device_info(self.handle)

    def open(self,
             device_id=1,
             bus_number_restrict=0,
             dev_address_restrict=0,
             serial_number=""):
        """Open DAVIS RPI device.

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
        USBDevice.open(libcaer.CAER_DEVICE_DAVIS_RPI, device_id,
                       bus_number_restrict, dev_address_restrict,
                       serial_number)
