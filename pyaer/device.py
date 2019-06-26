"""Generic Device.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
import abc
import cv2
import numpy as np
from pyaer import libcaer


class USBDevice(object):
    """Base class for all USB devices.

    This class is the base of DVS128, DAVIS240, DAVIS346 and DYNAPSE.
    """
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
            libcaer.IMU9_EVENT:
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
            libcaer.IMU9_EVENT:
                libcaer.caerIMU9EventPacketFromPacketHeader,
            libcaer.SPIKE_EVENT:
                libcaer.caerSpikeEventPacketFromPacketHeader
            }

    @abc.abstractmethod
    def obtain_device_info(self, handle):
        """Obtain device handle.

        This abstract method should be implemented in all derived classes.
        This method collects the general information about the USB device
        such as the width and height of the camera or the serial number
        of the device.

        # Arguments
            handle: `caerDeviceHandle`<br/>
                a valid device handle that can be used with the other
                `libcaer` functions, or `None` on error.
        """
        return

    @abc.abstractmethod
    def get_event(self):
        """Get Event.

        This abstract method should be implemented in all derived classes.
        This method returns a packet of events according to the type of
        the sensor.
        """
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
        """Close USB device.

        This method closes an opened USB device if the respective
        handle is not None.
        """
        if self.handle is not None:
            libcaer.caerDeviceClose(self.handle)

    def shutdown(self):
        """Shutdown device.

        This method is a combination of `data_stop` and `close`.
        This is a preferred way of shutting down a device.
        """
        self.data_stop()
        self.close()

    def data_start(self):
        """Start data transmission.

        # Returns
            flag: `bool`<br/>
                Return `True` if the data transmission is
                initialized successfully. Otherwise `False`.
        """
        # TODO figure out the parameter meaning
        if self.handle is not None:
            data_start_success = libcaer.caerDeviceDataStart(
                self.handle, None, None, None, None, None)
            return data_start_success
        else:
            return False

    def data_stop(self):
        """Stop data transmission.

        This method stops the data transmission only.
        Note that this method does not destroy the respective
        device `handle`.
        """
        libcaer.caerDeviceDataStop(self.handle)

    def send_default_config(self):
        """Send default configuration.

        Each type of devices has a set of default configurations (e.g. bias)
        that are pre-defined in the `libcaer` library.
        Note that the default configuration might not be suitable for your
        needs.

        # Returns
            flag: `bool`<br/>
                return `True` if the default config is set successfully,
                `False` otherwise.
        """
        if self.handle is not None:
            send_success = libcaer.caerDeviceSendDefaultConfig(self.handle)
            return send_success
        else:
            return False

    def set_data_exchange_blocking(self, exchange_blocking=True):
        """Set data exchange blocking.

        # Arguments
            exchange_blocking: `bool`<br/>
                whether to start all the data producer modules on the device
                (DVS, APS, Mux, ...) automatically when starting the
                data transfer thread with `caerDeviceDataStart()` or not.
                If disabled, be aware you will have to start the right modules
                manually, which can be useful if you need precise control
                over which ones are running at any time.<br/>
                The default is `True`.
        """
        return self.set_config(
            libcaer.CAER_HOST_CONFIG_DATAEXCHANGE,
            libcaer.CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING,
            exchange_blocking)

    def set_config(self, mod_addr, param_addr, param):
        """Set configuration.

        The main function of setting configurations (e.g., bias).

        # Arguments
            mod_addr: `int`<br/>
                a module address, used to specify which configuration module
                one wants to update. Negative addresses are used for host-side
                configuration, while positive addresses (including zero) are
                used for device-side configuration.
            param_addr: `int`<br/>
                a parameter address, to select a specific parameter to update
                from this particular configuration module.
                Only positive numbers
                (including zero) are allowed.
            param: `int` or `bool`<br/>
                a configuration parameter's new value.

        # Returns
            flag: `bool`<br/>
                returns `True` if the config is set successfully,
                `False` otherwise.
        """
        if self.handle is not None:
            set_success = libcaer.caerDeviceConfigSet(
                self.handle, mod_addr, param_addr, param)
            return set_success
        else:
            return False

    def get_config(self, mod_addr, param_addr):
        """Get Configuration.

        # Arguments
            mod_addr: `int`<br/>
                a module address, used to specify which configuration module
                one wants to update. Negative addresses are used for host-side
                configuration, while positive addresses (including zero) are
                used for device-side configuration.
            param_addr: `int`<br/>
                a parameter address, to select a specific parameter to update
                from this particular configuration module.
                Only positive numbers
                (including zero) are allowed.

        # Returns
            param: `int` or `bool`<br/>
                a configuration parameter's new value. Returns None
                if the handle is not valid.
        """
        if self.handle is not None:
            return libcaer.caerDeviceConfigGet(
                self.handle, mod_addr, param_addr)
        else:
            return None

    def get_packet_container(self):
        """Get event packet container.

        # Returns
            packet_container: `caerEventPacketContainer`<br/>
                a container that consists of event packets.
            packet_number: `int`<br/>
                number of event packet in the container.
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

        # Arguments
            packet_container: `caerEventPacketContainer`<br/>
                the event packet container
            idx: `int`<br/>
                the index of the packet header

        # Returns
            packet_header: `caerEventPacketHeader`<br/>
                the header that represents a event packet
            packet_type: `caerEventPacketType`<br/>
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
        """Get event packet from packet header.

        # Arguments
            packet_header: `caerEventPacketHeader`<br/>
                the header that represents a event packet.
            packet_type: `caerEventPacketType`<br/>
                the type of the event packet, can be one of the following:
                `libcaer.POLARITY_EVENT`,
                `libcaer.SPECIAL_EVENT`,
                `libcaer.FRAME_EVENT`,
                `libcaer.IMU6_EVENT`,
                `libcaer.SPIKE_EVENT`

        # Returns
            num_events: `int`<br/>
                number of events, return None if there is no events.
            event_packet: `caerEventPacket`<br/>
                a packet of events that are ready to be read.
        """
        num_events = self.get_event_number_funcs[packet_type](
            packet_header) if packet_type in self.get_event_number_funcs \
            else None

        event_packet = self.get_event_packet_funcs[packet_type](
            packet_header) if packet_type in self.get_event_packet_funcs \
            else None

        return num_events, event_packet

    def get_polarity_event(self, packet_header):
        """Get a packet of polarity event.

        # Arguments
            packet_header: `caerEventPacketHeader`<br/>
                the header that represents a event packet

        # Returns
            events: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (N, 4) where N
                is the number of events in the event packet.
                Each row in the array represents a single polarity event.
                The first number is the timestamp.
                The second number is the X position of the event.
                The third number is the Y position of the event.
                The fourth number represents the polarity of the event
                (positive or negative).
            num_events: `int`<br/>
                number of the polarity events available in the packet.
        """
        num_events, polarity = self.get_event_packet(
            packet_header, libcaer.POLARITY_EVENT)

        # TODO: to implement a noise filtering process
        # or reimplement this function into specific classes

        events = libcaer.get_polarity_event(
            polarity, num_events*4).reshape(num_events, 4)

        return events, num_events

    def get_polarity_hist(self, packet_header, device_type=None):
        """Get the positive and negative histogram for a packet."""
        num_events, polarity = self.get_event_packet(
            packet_header, libcaer.POLARITY_EVENT)

        if device_type == libcaer.DAVIS_CHIP_DAVIS240C:
            hist = libcaer.get_polarity_event_histogram_240(
                polarity, num_events)
        elif device_type == libcaer.DAVIS_CHIP_DAVIS346B:
            hist = libcaer.get_polarity_event_histogram_346(
                polarity, num_events)
        elif device_type == "DVS128":
            hist = libcaer.get_polarity_event_histogram_128(
                polarity, num_events)
        else:
            return None, 0

        return hist, num_events

    def get_counter_neuron_event(self, packet_header, device_type=None):
        """Get the positive and negative histogram for a packet."""
        num_events, polarity = self.get_event_packet(
            packet_header, libcaer.POLARITY_EVENT)

        if device_type == libcaer.DAVIS_CHIP_DAVIS240C:
            hist = libcaer.get_counter_neuron_frame_240(
                polarity, num_events)
        elif device_type == libcaer.DAVIS_CHIP_DAVIS346B:
            hist = libcaer.get_polarity_event_histogram_346(
                polarity, num_events)
        elif device_type == "DVS128":
            hist = libcaer.get_polarity_event_histogram_128(
                polarity, num_events)
        else:
            return None, 0

        return hist, num_events

    def get_special_event(self, packet_header):
        """Get a packet of special event.

        # Arguments
            packet_header: `caerEventPacketHeader`<br/>
                the header that represents a event packet

        # Returns
            events: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (N, 2) where N
                is the number of events in the event packet.
                Each row in the array represents a single special event.
                The first value is the timestamp of the event.
                The second value is the special event data.
            num_events: `int`<br/>
                number of the special events in the packet.
        """
        num_events, special = self.get_event_packet(
            packet_header, libcaer.SPECIAL_EVENT)

        events = libcaer.get_special_event(
            special, num_events*2).reshape(num_events, 2)

        return events, num_events

    def get_frame_event(self, packet_header, device_type=None,
                        aps_filter_type=libcaer.MONO):
        """Get a packet of frame event.

        # Arguments
            packet_header: `caerEventPacketHeader`<br/>
                the header that represents a event packet

        # Returns
            frame_mat: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (height, width).
                The height and width of the APS frame is determined by
                the specific DAVIS device (e.g., DAVIS240 will have
                a 180x240 APS frame.
                For DAVIS346Red that has RGB outputs, the output array
                has the shape of (height, width, 3)
            frame_ts: `int`<br/>
                the APS frame timestamp.
        """
        _, frame = self.get_event_packet(packet_header, libcaer.FRAME_EVENT)
        first_event = libcaer.caerFrameEventPacketGetEventConst(frame, 0)
        frame_ts = libcaer.caerFrameEventGetTimestamp64(first_event, frame)

        if device_type == libcaer.DAVIS_CHIP_DAVIS240C:
            frame_mat = libcaer.get_frame_event_240(first_event)
        elif device_type == libcaer.DAVIS_CHIP_DAVIS346B:
            frame_mat = libcaer.get_frame_event_346(first_event) \
                if aps_filter_type == libcaer.MONO else \
                libcaer.get_rgb_frame_event_346(first_event)
        else:
            Y_range = libcaer.caerFrameEventGetLengthY(first_event)
            X_range = libcaer.caerFrameEventGetLengthX(first_event)
            frame_mat = libcaer.get_frame_event(
                first_event, Y_range*X_range).reshape(Y_range, X_range) \
                if aps_filter_type == libcaer.MONO else \
                libcaer.get_frame_event(
                    first_event, Y_range*X_range*3).reshape(
                        Y_range, X_range, 3)

        return frame_mat, frame_ts

    def get_imu6_event(self, packet_header):
        """Get IMU6 event.

        # Arguments
            packet_header: `caerEventPacketHeader`
                the header that represents a event packet

        # Returns
            events: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (N, 8) where N
                is the number of IMU6 events in the packet.
                Each row of the array consists a single IMU6 event.
                The first value is the timestamp of the event.
                The next three values are accelerations on the X, Y, and Z
                axes. The next three values are angular velocity
                on the X, Y and Z axes.
                The last value is the temperature in Celsius scale.
            num_events: `int`<br/>
                number of the IMU6 events.
        """
        num_events, imu = self.get_event_packet(
            packet_header, libcaer.IMU6_EVENT)

        events = libcaer.get_imu6_event(
            imu, num_events*8).reshape(num_events, 8)

        return events, num_events

    def get_imu9_event(self, packet_header):
        """Get IMU9 event.

        # Arguments
            packet_header: `caerEventPacketHeader`
                the header that represents a event packet

        # Returns
            events: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (N, 11) where N
                is the number of IMU9 events in the packet.
                Each row of the array consists a single IMU9 event.
                The first value is the timestamp of the event.
                The next three values are accelerations on the X, Y, and Z
                axes. The next three values are angular velocity
                on the X, Y and Z axes. The next three values are
                X, Y, Z axis compass heading.
                The last value is the temperature in Celsius scale.
            num_events: `int`<br/>
                number of the IMU9 events.
        """
        num_events, imu = self.get_event_packet(
            packet_header, libcaer.IMU9_EVENT)

        events = libcaer.get_imu9_event(
            imu, num_events*11).reshape(num_events, 11)

        return events, num_events

    def get_spike_event(self, packet_header):
        """Get Spike Event.

        # Arguments
            packet_header: `caerEventPacketHeader`
                the header that represents a event packet

        # Returns
            events: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (N, 4) where N
                is the number of spike events in the packet.
                Each row of the array has a single spike event.
                The first value is the timestamp of the event.
                The second value is the neuron ID.
                The third value is the chip ID.
                The last value is the source core ID.
            num_events: `int`<br/>
                the number of the spike events.
        """
        num_events, spike = self.get_event_packet(
            packet_header, self.SPIKE_EVENT)

        events = libcaer.get_spike_event(
            spike, num_events*4).reshape(num_events, 4)

        return events, num_events


class SerialDevice(object):
    """Base class for serial devices.

    The base class for devices that use the serial port.
    eDVS is the only current supported device in this family.
    """
    def __init__(self):
        """Device."""
        self.handle = None

    @abc.abstractmethod
    def obtain_device_info(self, handle):
        """Obtain device handle.

        This abstract method should be implemented in all derived classes.
        This method collects the general information about the USB device
        such as the width and height of the camera or the serial number
        of the device.

        # Arguments
            handle: `caerDeviceHandle`<br/>
                a valid device handle that can be used with the other
                `libcaer` functions, or `None` on error.
        """
        return

    @abc.abstractmethod
    def get_event(self):
        """Get Event.

        This abstract method should be implemented in all derived classes.
        This method returns a packet of events according to the type of
        the sensor.
        """
        return

    def open(self,
             device_type,
             device_id=1,
             serial_port_name="/dev/ttyUSB0",
             serial_baud_rate=libcaer.CAER_HOST_CONFIG_SERIAL_BAUD_RATE_12M):
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
            serial_port_name: `str`<br/>
                name of the serial port device to open.<br/>
                `default is /dev/ttyUSB0`
            serial_baud_rate: `uint32_t`
                baud-rate for serial port communication.<br/>
                `default is 12M`
        """
        self.handle = libcaer.caerDeviceOpenSerial(
            device_id, device_type, serial_port_name,
            serial_baud_rate)
        if self.handle is None:
            raise ValueError("The device is failed to open.")

    def close(self):
        """Close USB device.

        This method closes an opened USB device if the respective
        handle is not None.
        """
        if self.handle is not None:
            libcaer.caerDeviceClose(self.handle)

    def shutdown(self):
        """Shutdown device.

        This method is a combination of `data_stop` and `close`.
        This is a preferred way of shutting down a device.
        """
        self.data_stop()
        self.close()

    def data_start(self):
        """Start data transmission.

        # Returns
            flag: `bool`<br/>
                Return `True` if the data transmission is
                initialized successfully. Otherwise `False`.
        """
        # TODO figure out the parameter meaning
        if self.handle is not None:
            data_start_success = libcaer.caerDeviceDataStart(
                self.handle, None, None, None, None, None)
            return data_start_success
        else:
            return False

    def data_stop(self):
        """Stop data transmission.

        This method stops the data transmission only.
        Note that this method does not destroy the respective
        device `handle`.
        """
        libcaer.caerDeviceDataStop(self.handle)

    def send_default_config(self):
        """Send default configuration.

        Each type of devices has a set of default configurations (e.g. bias)
        that are pre-defined in the `libcaer` library.
        Note that the default configuration might not be suitable for your
        needs.

        # Returns
            flag: `bool`<br/>
                return `True` if the default config is set successfully,
                `False` otherwise.
        """
        if self.handle is not None:
            send_success = libcaer.caerDeviceSendDefaultConfig(self.handle)
            return send_success
        else:
            return False

    def set_data_exchange_blocking(self, exchange_blocking=True):
        """Set data exchange blocking.

        # Arguments
            exchange_blocking: `bool`<br/>
                whether to start all the data producer modules on the device
                (DVS, APS, Mux, ...) automatically when starting the
                data transfer thread with `caerDeviceDataStart()` or not.
                If disabled, be aware you will have to start the right modules
                manually, which can be useful if you need precise control
                over which ones are running at any time.<br/>
                The default is `True`.
        """
        return self.set_config(
            libcaer.CAER_HOST_CONFIG_DATAEXCHANGE,
            libcaer.CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING,
            exchange_blocking)

    def set_config(self, mod_addr, param_addr, param):
        """Set configuration.

        The main function of setting configurations (e.g., bias).

        # Arguments
            mod_addr: `int`<br/>
                a module address, used to specify which configuration module
                one wants to update. Negative addresses are used for host-side
                configuration, while positive addresses (including zero) are
                used for device-side configuration.
            param_addr: `int`<br/>
                a parameter address, to select a specific parameter to update
                from this particular configuration module.
                Only positive numbers
                (including zero) are allowed.
            param: `int` or `bool`<br/>
                a configuration parameter's new value.

        # Returns
            flag: `bool`<br/>
                returns `True` if the config is set successfully,
                `False` otherwise.
        """
        if self.handle is not None:
            set_success = libcaer.caerDeviceConfigSet(
                self.handle, mod_addr, param_addr, param)
            return set_success
        else:
            return False

    def get_config(self, mod_addr, param_addr):
        """Get Configuration.

        # Arguments
            mod_addr: `int`<br/>
                a module address, used to specify which configuration module
                one wants to update. Negative addresses are used for host-side
                configuration, while positive addresses (including zero) are
                used for device-side configuration.
            param_addr: `int`<br/>
                a parameter address, to select a specific parameter to update
                from this particular configuration module.
                Only positive numbers
                (including zero) are allowed.

        # Returns
            param: `int` or `bool`<br/>
                a configuration parameter's new value. Returns None
                if the handle is not valid.
        """
        if self.handle is not None:
            return libcaer.caerDeviceConfigGet(
                self.handle, mod_addr, param_addr)
        else:
            return None

    def get_packet_container(self):
        """Get event packet container.

        # Returns
            packet_container: `caerEventPacketContainer`<br/>
                a container that consists of event packets.
            packet_number: `int`<br/>
                number of event packet in the container.
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

        # Arguments
            packet_container: `caerEventPacketContainer`<br/>
                the event packet container
            idx: `int`<br/>
                the index of the packet header

        # Returns
            packet_header: `caerEventPacketHeader`<br/>
                the header that represents a event packet
            packet_type: `caerEventPacketType`<br/>
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

        # Arguments
            packet_header: `caerEventPacketHeader`<br/>
                the header that represents a event packet

        # Returns
            events: `numpy.ndarray`
                a 2-D array that has the shape of (N, 4) where N
                is the number of events in the event packet.
                Each row in the array represents a single polarity event.
                The first number is the timestamp.
                The second number is the X position of the event.
                The third number is the Y position of the event.
                The fourth number represents the polarity of the event
                (positive or negative).
            num_events: `int`
                number of the polarity events available in the packet.
        """
        num_events = libcaer.caerEventPacketHeaderGetEventNumber(
            packet_header)
        polarity = libcaer.caerPolarityEventPacketFromPacketHeader(
            packet_header)

        events = libcaer.get_polarity_event(
            polarity, num_events*4).reshape(num_events, 4)

        return events, num_events
