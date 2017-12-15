"""DVS128.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from builtins import range
import numpy as np
from pyaer import libcaer
from pyaer.device import USBDevice


class DVS128(USBDevice):
    """Central class for managing single DVS128 device."""
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number=""):
        """DVS128.

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
        super(DVS128, self).__init__()
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        # get camera information
        self.obtain_device_info(self.handle)

    def obtain_device_info(self, handle):
        """Obtain DVS128 info."""
        if handle is not None:
            info = libcaer.caerDVS128InfoGet(handle)

            # port all info data field out
            self.device_id = info.deviceID
            self.device_is_master = info.deviceIsMaster
            self.device_serial_number = info.deviceSerialNumber
            self.device_string = info.deviceString
            self.device_usb_bus_number = info.deviceUSBBusNumber
            self.device_usb_device_address = info.deviceUSBDeviceAddress
            self.dvs_size_X = info.dvsSizeX
            self.dvs_size_Y = info.dvsSizeY
            self.logic_version = info.logicVersion

    def open(self,
             device_id=1,
             bus_number_restrict=0,
             dev_address_restrict=0,
             serial_number=""):
        """Open device.

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
        super(DVS128, self).open(
            libcaer.CAER_DEVICE_DVS128, device_id,
            bus_number_restrict, dev_address_restrict,
            serial_number)

    def start_data_stream(self):
        """Start streaming data."""
        self.data_start()
        self.set_data_exchange_blocking()

        # ignore first packet
        _, _ = self.get_packet_container()

    def get_event(self):
        """Get event.

        Maybe not so efficient
        """
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None:
            num_pol_event = 0
            num_special_event = 0
            pol_ts = None
            pol_xy = None
            pol_pol = None
            special_ts = None
            special_event_data = None
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

            return (pol_ts, pol_xy, pol_pol, num_pol_event,
                    special_ts, special_event_data, num_special_event)
        else:
            return None
