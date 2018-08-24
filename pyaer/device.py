"""Generic Device.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
import abc
from pyaer import libcaer


class USBDevice(object):
    """Base class for all USB devices."""
    def __init__(self):
        """Device."""
        self.handle = None

        # functions for get events number and packet functions
        self.get_event_number_funcs = {
            libcaer.POLARITY_EVENT:
                libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.SPECIAL_EVENT:
                libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.IMU6_EVENT:
                libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.SPIKE_EVENT:
                libcaer.caerEventPacketHeaderGetEventNumber
            }
        self.get_event_packet_funcs = {
            libcaer.POLARITY_EVENT:
                libcaer.caerPolarityEventPacketFromPacketHeader,
            libcaer.SPECIAL_EVENT:
                libcaer.caerSpecialEventPacketFromPacketHeader,
            libcaer.FRAME_EVENT:
                libcaer.caerFrameEventPacketFromPacketHeader,
            libcaer.IMU6_EVENT:
                libcaer.caerIMU6EventPacketFromPacketHeader,
            libcaer.SPIKE_EVENT:
                libcaer.caerSpikeEventPacketFromPacketHeader
            }

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

        # Arguments
            device_type: `int`<br/>
                Device type:<br/>
                `libcaer.CAER_DEVICE_DVS128`,
                `libcaer.CAER_DEVICE_EDVS`,
                `libcaer.CAER_DEVICE_DAVIS`,
                `libcaer.CAER_DEVICE_DAVIS_FX2`,
                `libcaer.CAER_DEVICE_DAVIS_FX3`,
                `libcaer.CAER_DEVICE_DAVIS_RPI`,
                `libcaer.CAER_DEVICE_DYNAPSE`.
            device_id: `int`<br/>
                a unique ID to identify the device from others.
                Will be used as the source for EventPackets being
                generate from its data.<br/>
                `default is 1`.
            bus_number_restrict: `int`<br/>
                restrict the search for viable devices to only this USB
                bus number.<br/>
                `default is 0`.
            dev_address_restrict: `int`<br/>
                restrict the search for viable devices to only this USB
                device address.<br/>
                `default is 0`.
            serial_number: `str`<br/>
                restrict the search for viable devices to only devices which do
                possess the given Serial Number in their USB
                SerialNumber descriptor.<br/>
                `default is ""`
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

    def get_event_packet(self, packet_header, packet_type):
        """Get event packet from packet header."""
        num_events = self.get_event_number_funcs[packet_type](
            packet_header) if packet_type in self.get_event_number_funcs \
            else None

        event_packet = self.get_event_packet_funcs[packet_type](
            packet_header) if packet_type in self.get_event_packet_funcs \
            else None

        return num_events, event_packet

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
        num_events, polarity = self.get_event_packet(
            packet_header, libcaer.POLARITY_EVENT)

        # TODO: to implement a noise filtering process
        # or reimplement this function into specific classes

        events = libcaer.get_polarity_event(
            polarity, num_events*4).reshape(num_events, 4)

        return events, num_events

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
        num_events, special = self.get_event_packet(
            packet_header, libcaer.SPECIAL_EVENT)

        events = libcaer.get_special_event(
            special, num_events*2).reshape(num_events, 2)

        return events, num_events

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
        _, frame = self.get_event_packet(packet_header, libcaer.FRAME_EVENT)
        first_event = libcaer.caerFrameEventPacketGetEventConst(frame, 0)
        frame_ts = libcaer.caerFrameEventGetTimestamp(first_event)
        Y_range = libcaer.caerFrameEventGetLengthY(first_event)
        X_range = libcaer.caerFrameEventGetLengthX(first_event)

        frame_mat = libcaer.get_frame_event(
            first_event, Y_range*X_range).reshape(Y_range, X_range)

        return frame_mat, frame_ts

    def get_imu6_event(self, packet_header):
        """Get IMU5 event.

        Parameters
        ----------
        packet_header : caerEventPacketHeader
            the header that represents a event packet
        """
        num_events, imu = self.get_event_packet(
            packet_header, libcaer.IMU6_EVENT)

        events = libcaer.get_imu6_event(
            imu, num_events*8).reshape(num_events, 8)

        return events, num_events

    def get_spike_event(self, packet_header):
        """Get Spike Event.

        Parameters
        ----------
        packet_header : caerEventPacketHeader
            the header that represents a event packet
        """
        num_events, spike = self.get_event_packet(
            packet_header, self.SPIKE_EVENT)

        events = libcaer.get_spike_event(
            spike, num_events*4).reshape(num_events, 4)

        return events, num_events


class SerialDevice(object):
    """Base class for serial devices."""
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
             serial_port_name="/dev/ttyUSB0",
             serial_baud_rate=libcaer.CAER_HOST_CONFIG_SERIAL_BAUD_RATE_12M):
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
        serial_port_name : str
            name of the serial port device to open.
        serial_baud_rate : uint32_t
            baud-rate for serial port communication.
        """
        self.handle = libcaer.caerDeviceOpenSerial(
            device_id, device_type, serial_port_name,
            serial_baud_rate)
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
        polarity = libcaer.caerPolarityEventPacketFromPacketHeader(
            packet_header)

        events = libcaer.get_polarity_event(
            polarity, num_events*4).reshape(num_events, 4)

        return events, num_events
