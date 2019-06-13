"""DVS128.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from builtins import range
import numpy as np

from pyaer import libcaer
from pyaer.device import USBDevice
from pyaer.filters import DVSNoise
from pyaer import utils


class DVS128(USBDevice):
    """DVS128.

    # Arguments
        device_id: `int`<br/>
            a unique ID to identify the device from others.
            Will be used as the source for EventPackets being
            generate from its data.<br/>
            `default is 1`
        bus_number_restrict: `int`<br/>
            restrict the search for viable devices to only this USB
            bus number.<br/>
            `default is 0`
        dev_address_restrict: `int`<br/>
            restrict the search for viable devices to only this USB
            device address.<br/>
            `default is 0`
        serial_number: `str`<br/>
            restrict the search for viable devices to only devices which do
            possess the given Serial Number in their USB
            SerialNumber descriptor.<br/>
            `default is ""`
        noise_filter: `bool`<br/>
            if enable noise filter,<br/>
            `default is False`.
    """
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number="",
                 noise_filter=False):
        """DVS128."""
        super(DVS128, self).__init__()
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        # get camera information
        self.obtain_device_info(self.handle)

        # noise filter
        self.filter_noise = noise_filter
        if noise_filter is True:
            self.noise_filter = DVSNoise(self.dvs_size_X, self.dvs_size_Y)
        else:
            self.noise_filter = None

    def set_noise_filter(self, noise_filter):
        """Set noise filter.

        # Arguments
            noise_filter: `filters.DVSNoise`<br/>
                A valid `DVSNoise` object. This filter implements
                software-level background activity filter.
        """
        if noise_filter is not None:
            self.noise_filter = noise_filter

    def enable_noise_filter(self):
        """Enalbe DVS noise filter.

        This function enables the DVS noise filter.
        Note that this function will initialize a `DVSNoise` filter
        if there is None.
        """
        if self.filter_noise is False:
            self.filter_noise = True

        if self.noise_filter is None:
            self.noise_filter = DVSNoise(self.dvs_size_X, self.dvs_size_Y)

    def disable_noise_filter(self):
        """Disable noise filter.

        This method disable the noise filter. Note that this function
        doesn't destroy the existed noise filter. It simply switches off
        the function.
        """
        if self.filter_noise is True:
            self.filter_noise = False

    def obtain_device_info(self, handle):
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

        # Arguments
            handle: `caerDeviceHandle`<br/>
                a valid device handle that can be used with the other
                `libcaer` functions, or `None` on error.
        """
        if handle is not None:
            info = libcaer.caerDVS128InfoGet(handle)

            # port all info data field out
            self.device_id = info.deviceID
            self.device_serial_number = info.deviceSerialNumber
            self.device_usb_bus_number = info.deviceUSBBusNumber
            self.device_usb_device_address = info.deviceUSBDeviceAddress
            self.device_string = info.deviceString
            self.firmware_version = info.firmwareVersion
            self.device_is_master = info.deviceIsMaster
            self.dvs_size_X = info.dvsSizeX
            self.dvs_size_Y = info.dvsSizeY

    def open(self,
             device_id=1,
             bus_number_restrict=0,
             dev_address_restrict=0,
             serial_number=""):
        """Open device.


        # Arguments
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
        super(DVS128, self).open(
            libcaer.CAER_DEVICE_DVS128, device_id,
            bus_number_restrict, dev_address_restrict,
            serial_number)

    def set_bias_from_json(self, file_path, verbose=False):
        """Set bias from loading JSON configuration file.

        # Arguments
            file_path: `str`<br/>
                absolute path of the JSON bias file.
            verbose: `bool`<br/>
                optional debugging message.
        """
        bias_obj = utils.load_dvs_bias(file_path, verbose)
        self.set_bias(bias_obj)

    def set_bias(self, bias_obj):
        """Set bias from bias dictionary.

        # Arguments
            bias_obj: `dict`<br/>
                dictionary that contains DVS128 biases.

        # Returns
            flag: `bool`<br/>
                True if set successful, False otherwise.
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
        # setting for noise filter
        if self.filter_noise is True:
            self.noise_filter.set_bias(bias_obj["noise_filter_configs"])

    def get_bias(self):
        """Get bias settings.

        # Returns
            bias_obj: `dict`<br/>
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

        # get noise filter configs
        if self.noise_filter is not None:
            bias_obj["noise_filter_configs"] = self.noise_filter.get_bias()

        return bias_obj

    def save_bias_to_json(self, file_path):
        """Save bias to JSON.

        # Arguments
            file_path: `str`<br/>
                the absolute path to the destiation.

        # Returns
            flag: `bool`<br/>
                returns True if success in writing, False otherwise.
        """
        bias_obj = self.get_bias()
        return utils.write_json(file_path, bias_obj)

    def start_data_stream(self, send_default_config=True):
        """Start streaming data.

        # Arguments
            send_default_config: `bool`<br/>
                send default config to the device before starting
                the data streaming.<br/>
                `default is True`
        """
        if send_default_config is True:
            self.send_default_config()
        self.data_start()
        self.set_data_exchange_blocking()

    def get_polarity_event(self, packet_header, noise_filter=False):
        """Get a packet of polarity event.

        # Arguments
            packet_header: `caerEventPacketHeader`<br/>
                the header that represents a event packet
            noise_filter: `bool`<br/>
                the background activity filter is applied if True.

        # Returns
            events: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (N, 4) where N
                is the number of events in the event packet.
                Each row in the array represents a single polarity event.
                The first number is the timestamp.
                The second number is the X position of the event.
                The third number is the Y position of the event.
                The fourth number represents the polarity of the event
                (positive or negative).<br/>
                If the `noise_filter` option is set to `True`,
                this array has an additional column at the end.
                The last column represents the validity of the corresponding
                event. Filtered events will be marked as 0.
            num_events: `int`<br/>
                number of the polarity events available in the packet.

        """
        num_events, polarity = self.get_event_packet(
            packet_header, libcaer.POLARITY_EVENT)

        if noise_filter is True:
            polarity = self.noise_filter.apply(polarity)

            events = libcaer.get_filtered_polarity_event(
                polarity, num_events*5).reshape(num_events, 5)
        else:
            events = libcaer.get_polarity_event(
                polarity, num_events*4).reshape(num_events, 4)

        return events, num_events

    def get_event(self, mode="events"):
        """Get event.

        # Returns
            pol_events: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (N, 4) where N
                is the number of events in the event packet.
                Each row in the array represents a single polarity event.
                The first number is the timestamp.
                The second number is the X position of the event.
                The third number is the Y position of the event.
                The fourth number represents the polarity of the event
                (positive or negative).<br/>
                If the `noise_filter` option is set to `True`,
                this array has an additional column at the end.
                The last column represents the validity of the corresponding
                event. Filtered events will be marked as 0.
            num_pol_events: `int`<br/>
                number of the polarity events available in the packet.
            special_events: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (N, 2) where N
                is the number of events in the event packet.
                Each row in the array represents a single special event.
                The first value is the timestamp of the event.
                The second value is the special event data.
            num_special_events: `int`<br/>
                number of the special events in the packet.
        """
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
                    if mode == "events":
                        events, num_events = self.get_polarity_event(
                            packet_header, self.filter_noise)
                        pol_events = np.hstack((pol_events, events)) \
                            if pol_events is not None else events
                    elif mode == "events_hist":
                        hist, num_events = self.get_polarity_hist(
                            packet_header, device_type="DVS128")
                        pol_events = hist if pol_events is None \
                            else pol_events+hist

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
