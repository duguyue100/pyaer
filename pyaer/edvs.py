"""eDVS.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from typing import Any
from typing import Tuple

import numpy as np

from pyaer import libcaer
from pyaer.device import SerialDevice
from pyaer.filters import DVSNoise


class eDVS(SerialDevice):
    """eDVS.

    # Args:
        device_id: A unique ID to identify the device from others. Will be used as the
            source for EventPackets being generate from its data. Default is 1.
        serial_port_name: name of the serial port device to open. Default is
            "/dev/ttyUSB0".
        serial_baud_rate: Baud-rate for serial port communication. Default is 12M
        filter_noise: If True, software noise filter will be enabled.
    """

    def __init__(
        self,
        device_id: int = 1,
        serial_port_name: str = "/dev/ttyUSB0",
        serial_baud_rate: int = libcaer.CAER_HOST_CONFIG_SERIAL_BAUD_RATE_12M,
        filter_noise: bool = False,
    ) -> None:
        super().__init__()
        # Opens device
        self.open(
            libcaer.CAER_DEVICE_EDVS, device_id, serial_port_name, serial_baud_rate
        )
        # Gets camera information
        self.obtain_device_info(self.handle)

        # Sets noise filter
        self.filter_noise = filter_noise
        self.noise_filter = (
            DVSNoise(self.dvs_size_X, self.dvs_size_Y) if self.filter_noise else None
        )

        self.configs_list = [
            ("cas", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_CAS),
            ("injGnd", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_INJGND),
            ("reqPd", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_REQPD),
            ("puX", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_PUX),
            ("diffOff", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_DIFFOFF),
            ("req", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_REQ),
            ("refr", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_REFR),
            ("puY", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_PUY),
            ("diffOn", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_DIFFON),
            ("diff", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_DIFF),
            ("foll", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_FOLL),
            ("Pr", libcaer.EDVS_CONFIG_BIAS, libcaer.EDVS_CONFIG_BIAS_PR),
        ]

    def obtain_device_info(self, handle: Any) -> None:
        """Obtain eDVS info.

        This function collects the following information from the device:

        - Deveice ID
        - Device string
        - If the device is a master camera
        - Camera width
        - Camera height

        # Args:
            handle: a valid device handle that can be used with the other
                `libcaer` functions, or `None` on error.
        """
        if handle is not None:
            info = libcaer.caerEDVSInfoGet(handle)

            # port all info data field out
            self.device_id = info.deviceID
            self.device_string = info.deviceString
            self.device_is_master = info.deviceIsMaster
            self.dvs_size_X = info.dvsSizeX
            self.dvs_size_Y = info.dvsSizeY
            self.serial_port_name = info.serialPortName
            self.serial_baud_rate = info.serialBaudRate

    def get_event(self):
        """Get event.

        # Returns
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
            pol_events = np.zeros(
                (0, 4) if self.filter_noise else (0, 5), dtype=np.uint64
            )
            special_events = np.zeros((0, 2), dtype=np.uint64)
            for packet_id in range(packet_number):
                packet_header, packet_type = self.get_packet_header(
                    packet_container, packet_id
                )
                if packet_type == libcaer.POLARITY_EVENT:
                    events, num_events = self.get_polarity_event(packet_header)
                    pol_events = np.hstack((pol_events, events))
                    num_pol_event += num_events
                elif packet_type == libcaer.SPECIAL_EVENT:
                    events, num_events = self.get_special_event(packet_header)
                    special_events = np.hstack((special_events, events))
                    num_special_event += num_events
            libcaer.caerEventPacketContainerFree(packet_container)

            return (pol_events, num_pol_event, special_events, num_special_event)
        else:
            return None
