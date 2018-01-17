"""Generic Device.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from builtins import range
import abc
import numpy as np
from pyaer import libcaer


class USBDevice(object):
    """Base class for all USB devices."""
    def __init__(self):
        """Device."""
        self.handle = None

    @abc.abstractmethod
    def obtain_device_info(self, handle):
        """Obtain device handle."""
        return

    @abc.abstractmethod
    def get_event(self):
        """Get Event."""
        return

    def open(self,
             device_type,
             device_id=1,
             bus_number_restrict=0,
             dev_address_restrict=0,
             serial_number=""):
        """Open USB deivce.

        Parameters
        ----------
        device_type : int
            Device type
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
            device_id, device_type, bus_number_restrict,
            dev_address_restrict, serial_number)
        if self.handle is None:
            raise ValueError("The device is failed to open.")

    def close(self):
        """Close USB device."""
        if self.handle is not None:
            libcaer.caerDeviceClose(self.handle)

    def shutdown(self):
        """Shutdown device."""
        self.data_stop()
        self.close()

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
        libcaer.caerDeviceDataStop(self.handle)

    def send_default_config(self):
        """Send default configuration."""
        if self.handle is not None:
            send_success = libcaer.caerDeviceSendDefaultConfig(self.handle)
            return send_success
        else:
            return False

    def set_data_exchange_blocking(self):
        """Set data exchange blocking."""
        return self.set_config(
            libcaer.CAER_HOST_CONFIG_DATAEXCHANGE,
            libcaer.CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING,
            True)

    def set_config(self, mod_addr, param_addr, param):
        """Set configuration."""
        if self.handle is not None:
            set_success = libcaer.caerDeviceConfigSet(
                self.handle, mod_addr, param_addr, param)
            return set_success
        else:
            return False

    def get_config(self, mod_addr, param_addr):
        """Get Configuration.

        (Experimental)
        """
        if self.handle is not None:
            return libcaer.caerDeviceConfigGet(
                self.handle, mod_addr, param_addr)
        else:
            return None

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

    @staticmethod
    def get_packet_header(packet_container, idx):
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

    @staticmethod
    def get_polarity_event(packet_header):
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
        ts = np.array(ts, dtype=np.int32)
        xy = np.array([x, y], dtype=np.uint8)
        pol = np.array(pol, dtype=np.bool)

        return ts, xy, pol, num_events

    @staticmethod
    def get_special_event(packet_header):
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
            event = libcaer.caerSpecialEventPacketGetEvent(
                polarity, event_id)
            ts.append(libcaer.caerSpecialEventGetTimestamp(event))
            event_data.append(libcaer.caerSpecialEventGetData(event))

        # change to numpy array
        ts = np.array(ts, dtype=np.int32)
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
        frame_mat = np.zeros((self.aps_size_Y, self.aps_size_X),
                             dtype=np.uint16)
        Y_range = libcaer.caerFrameEventGetLengthY(first_event)
        X_range = libcaer.caerFrameEventGetLengthX(first_event)
        for y in range(Y_range):
            for x in range(X_range):
                frame_mat[y, x] = libcaer.caerFrameEventGetPixel(
                    first_event, x, y)
        return frame_mat, frame_ts

    @staticmethod
    def get_imu6_event(packet_header):
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
        imu_ts = np.array(imu_ts, dtype=np.int32)
        imu_temp = np.array(imu_temp, dtype=np.float32)

        return imu_ts, imu_acc, imu_gyro, imu_temp, num_events

    @staticmethod
    def get_spike_event(packet_header):
        """Get Spike Event.

        Parameters
        ----------
        packet_header : caerEventPacketHeader
            the header that represents a event packet
        """
        num_events = libcaer.caerEventPacketHeaderGetEventNumber(
            packet_header)
        neuron_id = []
        core_id = []
        chip_id = []
        ts = []
        for event_id in range(num_events):
            spike = libcaer.caerSpikeEventPacketFromPacketHeader(
                packet_header)
            event = libcaer.caerSpikeEventPacketGetEvent(
                spike, event_id)
            neuron_id.append(libcaer.caerSpikeEventGetNeuronID(event))
            core_id.append(libcaer.caerSpikeEventGetSourceCoreID(event))
            chip_id.append(libcaer.caerSpikeEventGetChipID(event))
            ts.append(libcaer.caerSpikeEventGetTimestamp(event))

        ts = np.array(ts, dtype=np.int32)
        neuron_id = np.array(neuron_id, dtype=np.uint32)
        core_id = np.array(core_id, dtype=np.uint8)
        chip_id = np.array(chip_id, dtype=np.uint8)

        return ts, neuron_id, core_id, chip_id, num_events
