"""Generic Device.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Union
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING

import numpy as np

from pyaer import libcaer
from pyaer.dtypes import DeviceType
from pyaer.dtypes import EventType
from pyaer.dtypes import ModuleAddressType
from pyaer.dtypes import ParameterAddressType
from pyaer.dtypes import BiasObjectType
from pyaer.utils import load_json
from pyaer.utils import write_json

if TYPE_CHECKING:
    from pyaer.filters import DVSNoise


class Device(object):
    """Generic device."""

    def __init__(self):
        self.handle = None

        self.filter_noise = False
        self.noise_filter: Optional["DVSNoise"] = None

        self.configs_list: List[
            Tuple[str, ModuleAddressType, ParameterAddressType]
        ] = []

        # Functions for get events number and packet functions
        self.get_event_number_funcs: Dict[EventType, Callable] = {
            libcaer.POLARITY_EVENT: libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.SPECIAL_EVENT: libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.IMU6_EVENT: libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.IMU9_EVENT: libcaer.caerEventPacketHeaderGetEventNumber,
            libcaer.SPIKE_EVENT: libcaer.caerEventPacketHeaderGetEventNumber,
        }
        self.get_event_packet_funcs: Dict[EventType, Callable] = {
            libcaer.POLARITY_EVENT: libcaer.caerPolarityEventPacketFromPacketHeader,
            libcaer.SPECIAL_EVENT: libcaer.caerSpecialEventPacketFromPacketHeader,
            libcaer.FRAME_EVENT: libcaer.caerFrameEventPacketFromPacketHeader,
            libcaer.IMU6_EVENT: libcaer.caerIMU6EventPacketFromPacketHeader,
            libcaer.IMU9_EVENT: libcaer.caerIMU9EventPacketFromPacketHeader,
            libcaer.SPIKE_EVENT: libcaer.caerSpikeEventPacketFromPacketHeader,
        }

    @abstractmethod
    def obtain_device_info(self, handle: Any) -> None:
        """Obtains device handle.

        This abstract method should be implemented in all derived classes. This method
        collects the general information about the device such as the width and height
        of the camera or the serial number of the device.

        # Args:
            handle: a valid device handle that can be used with the other `libcaer`
                functions, or `None` on error.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_event(self) -> None:
        """Gets Event.

        This abstract method should be implemented in all derived classes. This method
        returns a packet of events according to the type of the sensor.
        """
        raise NotImplementedError()

    @abstractmethod
    def open(self) -> None:
        """Opens a device.

        The acutal implementation depends on the subclass.
        """
        raise NotImplementedError()

    def close(self):
        """Closes USB device.

        This method closes an opened device if the respective handle is not None.
        """
        if self.handle is not None:
            libcaer.caerDeviceClose(self.handle)

    def data_start(self) -> bool:
        """Starts data transmission.

        # Returns:     `True` if the data transmission is initialized successfully.
        Otherwise `False`.
        """
        # TODO figure out the parameter meaning
        if self.handle is not None:
            data_start_success = libcaer.caerDeviceDataStart(
                self.handle, None, None, None, None, None
            )
            return data_start_success
        else:
            return False

    def data_stop(self) -> None:
        """Stops data transmission.

        This method stops the data transmission only. Note that this method does not
        destroy the respective device `handle`.
        """
        libcaer.caerDeviceDataStop(self.handle)

    def shutdown(self) -> None:
        """Shuts down device.

        This method is a combination of `data_stop` and `close`. This is a preferred way
        of shutting down a device.
        """
        self.data_stop()
        self.close()

    def send_default_config(self) -> bool:
        """Sends default configuration.

        Each type of devices has a set of default configurations (e.g. bias) that are
        pre-defined in the `libcaer` library. Note that the default configuration might
        not be suitable for your needs.

        # Returns:
            `True` if the default config is set successfully, `False` otherwise.
        """
        if self.handle is not None:
            return libcaer.caerDeviceSendDefaultConfig(self.handle)
        else:
            return False

    def set_config(
        self, mod_addr: int, param_addr: int, param: Union[int, bool]
    ) -> bool:
        """Sets configuration.

        The main function of setting configurations (e.g., bias).

        # Args:
            mod_addr: a module address, used to specify which configuration module one
                wants to update. Negative addresses are used for host-side
                configuration, while positive addresses (including zero) are used for
                device-side configuration.
            param_addr: a parameter address, to select a specific parameter to update
                from this particular configuration module. Only positive numbers
                (including zero) are allowed.
            param: a configuration parameter's new value.

        # Returns:
            `True` if the config is set successfully, `False` otherwise.
        """
        if self.handle is not None:
            return libcaer.caerDeviceConfigSet(self.handle, mod_addr, param_addr, param)
        else:
            return False

    def set_max_container_packet_size(self, max_packet_size: int = 0) -> bool:
        """Sets max container packet size.

        # Args:
            max_packet_size: Set the maximum number of events any of a packet
                container's packets may hold before it's made available to the user.
                Set to zero to disable. The default is `0`.
        """
        return self.set_config(
            libcaer.CAER_HOST_CONFIG_PACKETS,
            libcaer.CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_PACKET_SIZE,
            max_packet_size,
        )

    def set_max_container_interval(self, max_packet_interval: int = 10000) -> bool:
        """Sets max packet interval.

        # Args:
            max_packet_interval: Set the time interval between subsequent packet
                containers. Must be at least 1 microsecond. The value is in
                microseconds, and is checked across all types of events contained in
                the EventPacketContainer. The default is `10000` (10ms or 100 packets/s)
        """
        return self.set_config(
            libcaer.CAER_HOST_CONFIG_PACKETS,
            libcaer.CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_INTERVAL,
            max_packet_interval,
        )

    def set_data_exchange_blocking(self, exchange_blocking: bool = True) -> bool:
        """Sets data exchange blocking.

        # Arg:
            exchange_blocking: Whether to start all the data producer modules on the
                device (DVS, APS, Mux, ...) automatically when starting the data
                transfer thread with `caerDeviceDataStart()` or not. If disabled, be
                aware you will have to start the right modules manually, which can be
                useful if you need precise control over which ones are running at any
                time. The default is `True`.
        """
        return self.set_config(
            libcaer.CAER_HOST_CONFIG_DATAEXCHANGE,
            libcaer.CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING,
            exchange_blocking,
        )

    def start_data_stream(
        self,
        send_default_config: bool = True,
        max_packet_size: Optional[int] = None,
        max_packet_interval: Optional[int] = None,
    ) -> None:
        """Starts streaming data.

        # Arguments
            send_default_config: Send default config to the device before starting
                the data streaming. `default is True`
            max_packet_size: Set the maximum number of events any of a packet
                container's packets may hold before it's made available to the user.
                Set to zero to disable. The default is `None` (use default setting: 0).
            max_packet_interval: Set the time interval between subsequent packet
                containers. Must be at least 1 microsecond. The value is in
                microseconds, and is checked across all types of events contained in the
                EventPacketContainer. The default is `None` (use default setting: 10ms)
        """
        if send_default_config:
            self.send_default_config()

        if max_packet_size is not None:
            self.set_max_container_packet_size(max_packet_size)
        if max_packet_interval is not None:
            self.set_max_container_interval(max_packet_interval)

        self.data_start()
        self.set_data_exchange_blocking()

    def get_config(self, mod_addr: int, param_addr: int) -> Optional[Union[int, bool]]:
        """Gets Configuration.

        # Args:
            mod_addr: a module address, used to specify which configuration module one
                wants to update. Negative addresses are used for host-side
                configuration, while positive addresses (including zero) are used for
                device-side configuration.
            param_addr: a parameter address, to select a specific parameter to update
                from this particular configuration module. Only positive numbers
                (including zero) are allowed.

        # Returns:
            A configuration parameter's new value. Returns None if the handle is not
                valid.
        """
        if self.handle is not None:
            return libcaer.caerDeviceConfigGet(self.handle, mod_addr, param_addr)
        else:
            return None

    def get_packet_container(self) -> Tuple[Optional[Any], Optional[int]]:
        """Gets event packet container.

        # Returns:     A tuple of ``(packet_container, num_event_packets)``.
        """
        packet_container = libcaer.caerDeviceDataGet(self.handle)
        if packet_container is not None:
            packet_number = libcaer.caerEventPacketContainerGetEventPacketsNumber(
                packet_container
            )
            return packet_container, packet_number
        else:
            return None, None

    def get_packet_header(
        self, packet_container: Any, idx: int
    ) -> Tuple[Optional[Any], Optional[Any]]:
        """Gets a single packet header.

        # Args:
            packet_container: the event packet container
            idx: the index of the packet header

        # Returns
            A tuple of ``(packet_header, packet_type)``.
        """
        packet_header = libcaer.caerEventPacketContainerGetEventPacket(
            packet_container, idx
        )
        if packet_header is not None:
            packet_type = libcaer.caerEventPacketHeaderGetEventType(packet_header)
            return packet_header, packet_type
        else:
            return None, None

    def get_event_packet(
        self, packet_header: Any, packet_type: EventType
    ) -> Tuple[int, Any]:
        """Gets event packet from packet header.

        # Arguments
            packet_header: the header that represents a event packet.
            packet_type: the type of the event packet, can be one of the following:
                - `libcaer.POLARITY_EVENT`,
                - `libcaer.SPECIAL_EVENT`,
                - `libcaer.FRAME_EVENT`,
                - `libcaer.IMU6_EVENT`,
                - `libcaer.SPIKE_EVENT`

        # Returns
            A tuple of ``(num_events, event_packet)``.
        """
        num_events = (
            self.get_event_number_funcs[packet_type](packet_header)
            if packet_type in self.get_event_number_funcs
            else None
        )

        event_packet = (
            self.get_event_packet_funcs[packet_type](packet_header)
            if packet_type in self.get_event_packet_funcs
            else None
        )

        return num_events, event_packet

    def set_bias(self, bias_obj: BiasObjectType) -> None:
        """Sets bias from bias dictionary.

        # Args:
            bias_obj: Dictionary that contains biases.

        # Returns
            True if set successful, False otherwise.
        """
        for bias_name, module_address, parameter_address in self.configs_list:
            self.set_config(module_address, parameter_address, bias_obj[bias_name])

        # setting for noise filter
        if self.noise_filter is not None and self.filter_noise is True:
            self.noise_filter.set_bias(bias_obj["noise_filter_configs"])

    def get_bias(self) -> BiasObjectType:
        """Gets bias settings.

        # Returns     Dictionary that contains DVS128 current bias settings.
        """
        bias_obj: BiasObjectType = {}

        for bias_name, module_address, parameter_address in self.configs_list:
            bias_obj[bias_name] = self.get_config(module_address, parameter_address)

        # get noise filter configs
        if self.noise_filter is not None:
            bias_obj["noise_filter_configs"] = self.noise_filter.get_bias()

        return bias_obj

    def set_bias_from_json(self, file_path: str) -> None:
        """Set bias from loading JSON configuration file.

        # Args:
            file_path: absolute path of the JSON bias file.
        """
        bias_obj = load_json(file_path)
        self.set_bias(bias_obj)

    def save_bias_to_json(self, file_path: str) -> bool:
        """Save bias to JSON.

        # Args:
            file_path: the absolute path to the destiation.

        # Returns
            returns True if success in writing, False otherwise.
        """
        bias_obj = self.get_bias()
        return write_json(file_path, bias_obj)

    def get_polarity_event(self, packet_header: Any) -> Tuple[np.ndarray, int]:
        """Gets a packet of polarity event.

        # Args:
            packet_header: the header that represents a event packet
            noise_filter: the background activity filter is applied if True.
        """
        num_events, polarity = self.get_event_packet(
            packet_header, libcaer.POLARITY_EVENT
        )

        if self.filter_noise is True and self.noise_filter is not None:
            polarity = self.noise_filter.apply(polarity)

            events = libcaer.get_filtered_polarity_event(
                polarity, num_events * 5
            ).reshape(num_events, 5)
        else:
            events = libcaer.get_polarity_event(polarity, num_events * 4).reshape(
                num_events, 4
            )

        return events, num_events

    def get_special_event(self, packet_header: Any) -> Tuple[np.ndarray, int]:
        """Get a packet of special event.

        # Arguments
            packet_header: the header that represents a event packet.
        """
        num_events, special = self.get_event_packet(
            packet_header, libcaer.SPECIAL_EVENT
        )

        events = libcaer.get_special_event(special, num_events * 2).reshape(
            num_events, 2
        )

        return events, num_events


class USBDevice(Device):
    """Base class for all USB devices.

    This class is the base of DVS128, DAVIS240, DAVIS346 and DYNAPSE.
    """

    def __init__(self):
        super().__init__()

    def open(  # type: ignore
        self,
        device_type: DeviceType,
        device_id: int = 1,
        bus_number_restrict: int = 0,
        dev_address_restrict: int = 0,
        serial_number: str = "",
    ) -> None:
        """Open an USB deivce.

        # Args:
            device_type:
                - `libcaer.CAER_DEVICE_DVS128`,
                - `libcaer.CAER_DEVICE_DAVIS`,
                - `libcaer.CAER_DEVICE_DAVIS_FX2`,
                - `libcaer.CAER_DEVICE_DAVIS_FX3`,
                - `libcaer.CAER_DEVICE_DAVIS_RPI`,
                - `libcaer.CAER_DEVICE_DYNAPSE`.
            device_id: An unique ID to identify the device from others. Will be used as
                the source for EventPackets being generate from its data.
                `default is 1`.
            bus_number_restrict: restrict the search for viable devices to only this USB
                bus number. `default is 0`.
            dev_address_restrict: restrict the search for viable devices to only this
                USB device address. `default is 0`.
            serial_number: restrict the search for viable devices to only devices which
                do possess the given Serial Number in their USB SerialNumber descriptor.
                `default is ""`
        """
        self.handle = libcaer.caerDeviceOpen(
            device_id,
            device_type,
            bus_number_restrict,
            dev_address_restrict,
            serial_number,
        )
        if self.handle is None:
            raise ValueError("The device is failed to open.")

    def get_polarity_hist(self, packet_header, device_type=None):
        """Get the positive and negative histogram for a packet."""
        num_events, polarity = self.get_event_packet(
            packet_header, libcaer.POLARITY_EVENT
        )

        if device_type == libcaer.DAVIS_CHIP_DAVIS240C:
            hist = libcaer.get_polarity_event_histogram_240(polarity, num_events)
        elif device_type == libcaer.DAVIS_CHIP_DAVIS346B:
            hist = libcaer.get_polarity_event_histogram_346(polarity, num_events)
        elif device_type == "DVS128":
            hist = libcaer.get_polarity_event_histogram_128(polarity, num_events)
        elif device_type == libcaer.DVXPLORER_CHIP_ID:
            hist = libcaer.get_polarity_event_histogram_dvxplorer(polarity, num_events)
        elif device_type == libcaer.DVXPLORER_LITE_CHIP_ID:
            hist = libcaer.get_polarity_event_histogram_dvxplorer_lite(
                polarity, num_events
            )
        else:
            return None, 0

        return hist, num_events

    def get_frame_event(
        self, packet_header, device_type=None, aps_filter_type=libcaer.MONO
    ):
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
            frame_mat = (
                libcaer.get_frame_event_346(first_event)
                if aps_filter_type == libcaer.MONO
                else libcaer.get_rgb_frame_event_346(first_event)
            )
        else:
            Y_range = libcaer.caerFrameEventGetLengthY(first_event)
            X_range = libcaer.caerFrameEventGetLengthX(first_event)
            frame_mat = (
                libcaer.get_frame_event(first_event, Y_range * X_range).reshape(
                    Y_range, X_range
                )
                if aps_filter_type == libcaer.MONO
                else libcaer.get_frame_event(
                    first_event, Y_range * X_range * 3
                ).reshape(Y_range, X_range, 3)
            )

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
        num_events, imu = self.get_event_packet(packet_header, libcaer.IMU6_EVENT)

        events = libcaer.get_imu6_event(imu, num_events * 8).reshape(num_events, 8)

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
        num_events, imu = self.get_event_packet(packet_header, libcaer.IMU9_EVENT)

        events = libcaer.get_imu9_event(imu, num_events * 11).reshape(num_events, 11)

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
        num_events, spike = self.get_event_packet(packet_header, libcaer.SPIKE_EVENT)

        events = libcaer.get_spike_event(spike, num_events * 4).reshape(num_events, 4)

        return events, num_events


class SerialDevice(Device):
    """Base class for serial devices.

    The base class for devices that use the serial port. eDVS is the only current
    supported device in this family.
    """

    def __init__(self):
        super().__init__()

    def open(  # type: ignore
        self,
        device_type: DeviceType,
        device_id: int = 1,
        serial_port_name: str = "/dev/ttyUSB0",
        serial_baud_rate: int = libcaer.CAER_HOST_CONFIG_SERIAL_BAUD_RATE_12M,
    ) -> None:
        """Open a serial deivce.

        # Args:
            device_type: `libcaer.CAER_DEVICE_EDVS`,
            device_id: a unique ID to identify the device from others. Will be used as
                the source for EventPackets being generate from its data.
                `default is 1`.
            serial_port_name: name of the serial port device to open.
                `default is /dev/ttyUSB0`
            serial_baud_rate: baud-rate for serial port communication.
                `default is 12M`
        """
        self.handle = libcaer.caerDeviceOpenSerial(
            device_id, device_type, serial_port_name, serial_baud_rate
        )
        if self.handle is None:
            raise ValueError("The device is failed to open.")

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
        num_events, polarity = self.get_event_packet(
            packet_header, libcaer.POLARITY_EVENT
        )

        events = libcaer.get_polarity_event(polarity, num_events * 4).reshape(
            num_events, 4
        )

        return events, num_events
