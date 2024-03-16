from __future__ import annotations

from typing import Any

import numpy as np

from pyaer import libcaer
from pyaer.device import USBDevice
from pyaer.filters import DVSNoise


class DVS128(USBDevice):
    """DVS128.

    Args:
        device_id: a unique ID to identify the device from others. Will be used as the
            source for EventPackets being generate from its data. `default is 1`
        bus_number_restrict: restrict the search for viable devices to only this USB
            bus number. `default is 0`
        dev_address_restrict: restrict the search for viable devices to only this USB
            device address. `default is 0`
        serial_number: restrict the search for viable devices to only devices which do
            possess the given Serial Number in their USB SerialNumber descriptor.
            `default is ""`
        filter_noise: if enable noise filter, `default is False`.
    """

    def __init__(
        self,
        device_id: int = 1,
        bus_number_restrict: int = 0,
        dev_address_restrict: int = 0,
        serial_number: str = "",
        filter_noise: bool = False,
    ) -> None:
        super().__init__()
        # Opens device.
        self.open(
            libcaer.CAER_DEVICE_DVS128,
            device_id,
            bus_number_restrict,
            dev_address_restrict,
            serial_number,
        )
        # Gets camera information.
        self.obtain_device_info(self.handle)

        # Sets noise filter
        self.filter_noise = filter_noise
        self.noise_filter = (
            DVSNoise(self.dvs_size_X, self.dvs_size_Y) if filter_noise else None
        )

        # Bias configuration list
        self.configs_list = [
            ("cas", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_CAS),
            ("injGnd", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_INJGND),
            ("reqPd", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_REQPD),
            ("puX", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_PUX),
            ("diffOff", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_DIFFOFF),
            ("req", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_REQ),
            ("refr", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_REFR),
            ("puY", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_PUY),
            ("diffOn", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_DIFFON),
            ("diff", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_DIFF),
            ("foll", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_FOLL),
            ("Pr", libcaer.DVS128_CONFIG_BIAS, libcaer.DVS128_CONFIG_BIAS_PR),
        ]

    def obtain_device_info(self, handle: Any) -> None:
        """Obtain DVS128 info.

        This function collects the following information from the device:

        - Deveice ID
        - If the device is a master camera
        - Device string
        - Device USB bus number
        - Device USB device address
        - Camera width
        - Camera height
        - Logic version

        Args:
            handle: `caerDeviceHandle`<br/>
                a valid device handle that can be used with the other
                `libcaer` functions, or `None` on error.
        """
        if handle is not None:
            info = libcaer.caerDVS128InfoGet(handle)

            # Ports all info data field out
            self.device_id = info.deviceID
            self.device_serial_number = info.deviceSerialNumber
            self.device_usb_bus_number = info.deviceUSBBusNumber
            self.device_usb_device_address = info.deviceUSBDeviceAddress
            self.device_string = info.deviceString
            self.firmware_version = info.firmwareVersion
            self.device_is_master = info.deviceIsMaster
            self.dvs_size_X = info.dvsSizeX
            self.dvs_size_Y = info.dvsSizeY

    def get_event(  # type: ignore
        self, mode: str = "events"
    ) -> tuple[np.ndarray, int, np.ndarray, int] | None:
        """Get event.

        Returns:
            pol_events: a 2-D array of shape (N, 4) where N is the number of events in
                the event packet. Each row in the array represents a single polarity
                event. The first number is the timestamp. The second number is the X
                position of the event. The third number is the Y position of the event.
                The fourth number represents the polarity of the event (positive or
                negative). If the `noise_filter` option is set to `True`, this array
                has an additional column at the end. The last column represents the
                validity of the corresponding event. Filtered events are marked as 0.
            num_pol_events: number of the polarity events available in the packet.
            special_events: a 2-D array that has the shape of (N, 2) where N is the
                number of events in the event packet. Each row in the array represents
                a single special event. The first value is the timestamp of the event.
                The second value is the special event data.
            num_special_events: number of the special events in the packet.
        """
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None and packet_number is not None:
            num_pol_event = 0
            num_special_event = 0
            pol_events = (
                np.zeros((0, int(4 + self.filter_noise)), dtype=np.uint64)
                if mode == "events"
                else np.zeros((128, 128, 2), dtype=np.uint64)
            )
            special_events = np.zeros((0, 2), dtype=np.uint64)
            for packet_id in range(packet_number):
                packet_header, packet_type = self.get_packet_header(
                    packet_container, packet_id
                )
                if packet_type == libcaer.POLARITY_EVENT:
                    if mode == "events":
                        events, num_events = self.get_polarity_event(packet_header)
                        pol_events = np.hstack((pol_events, events))
                    elif mode == "events_hist":
                        hist, num_events = self.get_polarity_hist(
                            packet_header, device_type="DVS128"
                        )
                        pol_events += hist

                    num_pol_event += num_events
                elif packet_type == libcaer.SPECIAL_EVENT:
                    events, num_events = self.get_special_event(packet_header)
                    special_events = np.hstack((special_events, events))
                    num_special_event += num_events
            libcaer.caerEventPacketContainerFree(packet_container)

            return (pol_events, num_pol_event, special_events, num_special_event)
        else:
            return None
