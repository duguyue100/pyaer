"""Generic Device.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
import numpy as np
from pyaer import libcaer


class USBDevice(object):
    """Base class for all USB devices."""
    def __init__(self,
                 device_type,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number=""):
        """Device.

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
        pass

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
        if self.handle is not None:
            return libcaer.caerDeviceConfigGet(
                self.handle, mod_addr, param_addr)
        else:
            return None
