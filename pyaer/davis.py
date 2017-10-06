"""DAVIS Camera.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
import numpy as np
from pyaer import libcaer


class DAVIS(object):
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
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        if self.handle is None:
            raise ValueError("The camera is failed to open.")
        # get camera information
        self.obtain_device_info(self.handle)

    def obtain_device_info(self, handle):
        """Obtain DAVIS info."""
        info = libcaer.caerDavisInfoGet(handle)

        self.device_id = info.deviceID
        self.device_serial_number = info.deviceSerialNumber
        self.device_usb_bus_number = info.deviceUSBBusNumber
        self.device_usb_device_address = info.deviceUSBDeviceAdress
        self.device_string = info.deivce_string
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

    def send_default_config(self):
        """Send default bias configuration."""
        if self.handle is not None:
            send_success = libcaer.caerDeviceSendDefaultConfig(self.handle)
            return send_success
        else:
            return False

    def set_config(self, mod_addr, param_addr, param):
        """Set configuration."""
        if self.handle is not None:
            set_success = libcaer.caerDeviceConfigSet(
                self.handle, mod_addr, param_addr, param)
            return set_success
        else:
            return False

    def get_config(self, mod_addr, param_addr):
        """Get Configuration."""
        # TODO test configure get function
        pass

    def set_data_exchange_blocking(self):
        """Set data exchange blocking."""
        return self.set_config(
            libcaer.CAER_HOST_CONFIG_DATAEXCHANGE,
            libcaer.CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING,
            True)

    def data_start(self):
        """Start data transmission."""
        # TODO figure out the parameter meaning
        if self.handle is not None:
            data_start_success = libcaer.caerDeviceDataStart(
                self.handle, None, None, None, None, None)
            return data_start_success
        else:
            return False

    def data_stop(self):
        """Stop data transmission."""
        if self.handle is not None:
            libcaer.caerDeviceDataStop(self.handle)

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
        self.handle = libcaer.caerDeviceOpen(
            device_id, libcaer.CAER_DEVICE_DAVIS,
            bus_number_restrict, dev_address_restrict,
            serial_number)

    def close(self):
        """Close device.

        Cannot use
        """
        pass

    def shutdown(self):
        """Shutdown device."""
        self.data_stop()
        self.close()

    def get_packet_container(self):
        """Get event packet container.

        Returns
        -------
        packet_container : caerEventPacketContainer
            a container that consists of event packets
        packet_number : int
            number of event packet in the container
        """
        packet_container = libcaer.caerDeviceDataGet(self.handle)
        if packet_container is not None:
            packet_number = \
                libcaer.caerEventPacketContainerGetEventPacketsNumber(
                    packet_container)
            return packet_container, packet_number
        else:
            return None, None

    def get_packet_header(self, packet_container, idx):
        """Get a single packet header.

        Parameters
        ----------
        packet_container : caerEventPacketContainer
            the event packet container
        idx : int
            the index of the packet header

        Returns
        -------
        packet_header : caerEventPacketHeader
            the header that represents a event packet
        packet_type : caerEventPacketType
            the type of the event packet
        """
        packet_header = \
            libcaer.caerEventPacketContainerGetEventPacket(
                packet_container, idx)
        if packet_header is None:
            return (None, None)
        else:
            packet_type = libcaer.caerEventPacketHeaderGetEventType(
                packet_header)
            return packet_header, packet_type

    def get_polarity_event(self, packet_header):
        """Get a packet of polarity event.

        Parameters
        ----------
        packet_header : caerEventPacketHeader
            the header that represents a event packet

        Returns
        -------
        ts : numpy.ndarray
            list of time stamp
        xy : numpy.ndarray
            list of x, y coordinate
        pol : numpy.ndarray
            list of polarity
        """
        num_events = libcaer.caerEventPacketHeaderGetEventNumber(
            packet_header)
        ts = []
        x = []
        y = []
        pol = []
        for event_id in range(num_events):
            polarity = libcaer.caerPolarityEventPacketFromPacketHeader(
                packet_header)
            event = libcaer.caerPolarityEventPacketGetEvent(
                polarity, event_id)
            ts.append(libcaer.caerPolarityEventGetTimestamp(event))
            x.append(libcaer.caerPolarityEventGetX(event))
            y.append(libcaer.caerPolarityEventGetY(event))
            pol.append(libcaer.caerPolarityEventGetPolarity(event))

        # change to numpy array
        ts = np.array(ts, dtype=np.uint64)
        xy = np.array([x, y], dtype=np.uint8)
        pol = np.array(pol, dtype=np.bool)

        return ts, xy, pol, num_events

    def get_special_event(self, packet_header):
        """Get a packet of special event.

        Parameters
        ----------
        packet_header : caerEventPacketHeader
            the header that represents a event packet

        Returns
        -------
        ts : numpy.ndarray
            list of time stamp
        event_data : numpy.ndarray
            list of event data
        """
        num_events = libcaer.caerEventPacketHeaderGetEventNumber(
            packet_header)
        ts = []
        event_data = []
        for event_id in range(num_events):
            polarity = libcaer.caerSpecialEventPacketFromPacketHeader(
                packet_header)
            event = libcaer.caerPolarityEventPacketGetEvent(
                polarity, event_id)
            ts.append(libcaer.caerSpecialEventGetTimestamp(event))
            event_data.append(libcaer.caerSpecialEventGetData(event))

        # change to numpy array
        ts = np.array(ts, dtype=np.uint64)
        event_data = np.array(event_data, dtype=np.bool)

        return ts, event_data, num_events

    def get_frame_event(self, packet_header):
        """Get a packet of frame event.

        Parameters
        ----------
        packet_header : caerEventPacketHeader
            the header that represents a event packet

        Returns
        -------
        frame_mat : numpy.ndarray
            the frame
        frame_ts : int
            the frame timestamp
        """
        frame = libcaer.caerFrameEventPacketFromPacketHeader(
            packet_header)
        first_event = libcaer.caerFrameEventPacketGetEventConst(frame, 0)
        frame_ts = libcaer.caerFrameEventGetTimestamp(first_event)
        frame_mat = np.zeros((self.aps_size_X, self.apsSizeY), dtype=np.uint8)
        for y in range(libcaer.caerFrameEventGetLengthX(first_event)):
            for x in range(libcaer.caerFrameEventGetLengthX(first_event)):
                frame_mat[x, y] = libcaer.caerFrameEventGetPixel(
                    first_event, x, y)
        return frame_mat, frame_ts

    def get_imu6_event(self, packet_header):
        """Get IMU5 event.

        Parameters
        ----------
        packet_header : caerEventPacketHeader
            the header that represents a event packet
        """
        num_events = libcaer.caerEventPacketHeaderGetEventNumber(
            packet_header)
        imu = libcaer.caerIMU6EventPacketFromPacketHeader(packet_header)
        imu_acc = []
        imu_gyro = []
        imu_ts = []
        imu_temp = []
        for event_id in range(num_events):
            imu6 = libcaer.caerIMU6EventPacketGetEvent(imu, event_id)
            x_acc = libcaer.caerIMU6EventGetAccelX(imu6)
            y_acc = libcaer.caerIMU6EventGetAccelY(imu6)
            z_acc = libcaer.caerIMU6EventGetAccelZ(imu6)
            x_gyro = libcaer.caerIMU6EventGetGyroX(imu6)
            y_gyro = libcaer.caerIMU6EventGetGyroY(imu6)
            z_gyro = libcaer.caerIMU6EventGetGyroZ(imu6)

            imu_acc.append([x_acc, y_acc, z_acc])
            imu_gyro.append([x_gyro, y_gyro, z_gyro])
            imu_ts.append(libcaer.caerIMU6EventGetTimestamp(imu6))
            imu_temp.append(libcaer.caerIMU6EventGetTemp(imu6))

        imu_acc = np.array(imu_acc, dtype=np.float32)
        imu_gyro = np.array(imu_gyro, dtype=np.float32)
        imu_ts = np.array(imu_ts, dtype=np.uint64)
        imu_temp = np.array(imu_temp, dtype=np.float32)

        return imu_acc, imu_gyro, imu_ts, imu_temp

    def get_event(self):
        """Get Event.

        Maybe not so efficient.
        TODO fix the details
        """
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None:
            pass
        else:
            return None
