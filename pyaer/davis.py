"""DAVIS Camera.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from builtins import range
import numpy as np
from pyaer import libcaer
from pyaer.device import USBDevice


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

    def start_data_stream(self):
        """Start streaming data."""
        self.data_start()
        self.set_data_exchange_blocking()

        # ignore first packet
        #  _, _ = self.get_packet_container()

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
            frames = np.array(frames, dtype=np.uint8)
            frames_ts = np.array(frames_ts, dtype=np.uint64)

            return (pol_ts, pol_xy, pol_pol, num_pol_event,
                    special_ts, special_event_data, num_special_event,
                    frames_ts, frames, imu_ts, imu_acc, imu_gyro, imu_temp,
                    num_imu_event)
        else:
            return None
