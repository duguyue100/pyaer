"""DVS128.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from builtins import range
import numpy as np

from pyaer import libcaer
from pyaer.device import USBDevice
from pyaer import utils


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

    def set_bias_from_json(self, file_path, verbose=False):
        """Set bias from loading JSON configuration file.

        # Parameters
        file_path : string
            absolute path of the JSON bias file.
        """
        bias_obj = utils.load_dvs_bias(file_path, verbose)
        self.set_bias(bias_obj)

    def set_bias(self, bias_obj):
        """Set bias from bias dictionary.

        # Parameters
        bias_obj : dict
            dictionary that contains DVS128 biases.

        # Returns
        flag : bool
            True if set successful, False otherwise.
            TODO: make this flag check possible
        """
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_CAS,
                        bias_obj["cas"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_INJGND,
                        bias_obj["injGnd"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_REQPD,
                        bias_obj["reqPd"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_PUX,
                        bias_obj["puX"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_DIFFOFF,
                        bias_obj["diffOff"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_REQ,
                        bias_obj["req"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_REFR,
                        bias_obj["refr"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_PUY,
                        bias_obj["puY"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_DIFFON,
                        bias_obj["diffOn"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_DIFF,
                        bias_obj["diff"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_FOLL,
                        bias_obj["foll"])
        self.set_config(libcaer.DVS128_CONFIG_BIAS,
                        libcaer.DVS128_CONFIG_BIAS_PR,
                        bias_obj["Pr"])

    def get_bias(self):
        """Get bias settings.

        # Returns
        bias_obj : dict
            dictionary that contains DVS128 current bias settings.
        """
        bias_obj = {}
        bias_obj["cas"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_CAS)
        bias_obj["injGnd"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_INJGND)
        bias_obj["reqPd"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_REQPD)
        bias_obj["puX"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_PUX)
        bias_obj["diffOff"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_DIFFOFF)
        bias_obj["req"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_REQ)
        bias_obj["refr"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_REFR)
        bias_obj["puY"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_PUY)
        bias_obj["diffOn"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_DIFFON)
        bias_obj["diff"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_DIFF)
        bias_obj["foll"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_FOLL)
        bias_obj["Pr"] = self.get_config(
            libcaer.DVS128_CONFIG_BIAS,
            libcaer.DVS128_CONFIG_BIAS_PR)

        return bias_obj

    def save_bias_to_json(self, file_path):
        """Save bias to JSON."""
        bias_obj = self.get_bias()
        return utils.write_json(file_path, bias_obj)

    def start_data_stream(self, send_default_config=True):
        """Start streaming data."""
        if send_default_config is True:
            self.send_default_config()
        self.data_start()
        self.set_data_exchange_blocking()

    def get_event(self):
        """Get event."""
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None:
            num_pol_event = 0
            num_special_event = 0
            pol_events = None
            special_events = None
            for packet_id in range(packet_number):
                packet_header, packet_type = self.get_packet_header(
                    packet_container, packet_id)
                if packet_type == libcaer.POLARITY_EVENT:
                    events, num_events = self.get_polarity_event(
                        packet_header)
                    pol_events = np.hstack((pol_events, events)) \
                        if pol_events is not None else events
                    num_pol_event += num_events
                elif packet_type == libcaer.SPECIAL_EVENT:
                    events, num_events = self.get_special_event(
                        packet_header)
                    special_events = np.hstack((special_events, events)) \
                        if special_events is not None else events
                    num_special_event += num_events
            libcaer.caerEventPacketContainerFree(packet_container)

            return (pol_events, num_pol_event, special_events,
                    num_special_event)
        else:
            return None
