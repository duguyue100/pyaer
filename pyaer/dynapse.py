"""DYNAPE.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
import numpy as np
from pyaer import libcaer
from pyaer.device import USBDevice


class DYNAPE(USBDevice):
    """Class defines DYNAPE."""
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number=""):
        """DYNAPE.

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
        super(DYNAPE, self).__init__()
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        # get camera info
        self.obtain_device_info(self.handle)

    def obtain_device_info(self, handle):
        """Obtain DYNAPE info."""
        if handle is not None:
            info = libcaer.caerDynapseInfoGet(handle)

            # port all info data fields out
            self.device_id = info.deviceID
            self.device_serial_number = info.deviceSerialNumber
            self.deivce_usb_bus_number = info.deivceUSBBusNumber
            self.device_usb_device_address = info.deviceUSBDeviceAddress
            self.device_string = info.deviceString
            self.logic_version = info.logicVersion
            self.device_is_master = info.deviceIsMaster
            self.logic_clock = info.logicClock
            self.chip_id = info.chipID
            self.aer_has_statistics = info.aerHasStatistics
            self.mux_has_statistics = info.muxHasStatistics

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
        super(DYNAPE, self).open(
            libcaer.CAER_DEVICE_DYNAPE, device_id,
            bus_number_restrict, dev_address_restrict,
            serial_number)

    def get_event(self):
        """Get Event.

        Maybe not so efficient.
        """
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None:
            num_spike_events = 0
            spike_neuron_id = None
            spike_core_id = None
            spike_chip_id = None
            spike_ts = None

            for packet_id in range(packet_number):
                packet_header, packet_type = self.get_packet_header(
                    packet_container, packet_id)
                if packet_type == libcaer.SPIKE_EVENT:
                    ts, neuron_id, core_id, chip_id, num_events = \
                        self.get_spike_event(packet_header)

                    spike_neuron_id = np.hstack(
                        (spike_neuron_id, neuron_id)) \
                        if spike_neuron_id is not None else neuron_id
                    spike_core_id = np.hstack((spike_core_id, core_id)) \
                        if spike_core_id is not None else core_id
                    spike_chip_id = np.hstack((spike_chip_id, chip_id)) \
                        if spike_chip_id is not None else chip_id
                    spike_ts = np.hstack((spike_ts, ts)) \
                        if spike_ts is not None else ts
                    num_spike_events += num_events
        return (spike_ts, spike_neuron_id, spike_core_id, spike_chip_id,
                num_spike_events)
