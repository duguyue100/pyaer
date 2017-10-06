"""DVS128.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
import numpy as np
from pyaer import libcaer


class DVS128(object):
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
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        if self.handle is None:
            raise ValueError("The camera is failed to open.")
        # get camera information
        self.obtain_device_info(self.handle)

    def obtain_device_info(self, handle):
        """Obtain DVS128 info."""
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
        libcaer.caerDeviceDataStop(self.handle)

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
        self.handle = libcaer.caerDeviceOpen(
            device_id, libcaer.CAER_DEVICE_DVS128,
            bus_number_restrict, dev_address_restrict,
            serial_number)

    def close(self):
        """Close device.

        Cannot use
        """
        if self.handle is not None:
            libcaer.caerDeviceClose(self.handle)

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

    def get_event(self):
        """Get event.

        Maybe not so efficient
        """
        packet_container, packet_number = self.get_packet_container()
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
                pol_ts = np.hstack((pol_ts, ts)) if pol_ts is not None else ts
                pol_xy = np.hstack((pol_xy, xy)) if pol_xy is not None else xy
                pol_pol = np.hstack((pol_pol, pol)) if pol_pol is not None \
                    else pol
                num_pol_event += num_events
            elif packet_type == libcaer.SPECIAL_EVENT:
                ts, event_data, num_events = self.get_special_event(
                    packet_header)
                special_ts = np.hstack((special_ts, ts)) \
                    if special_ts is not None else special_ts
                special_event_data = np.hstack(
                    (special_event_data, event_data)) \
                    if special_event_data is not None else special_event_data
                num_special_event += num_events

        return (pol_ts, pol_xy, pol_pol, num_pol_event,
                special_ts, special_event_data, num_special_event)
