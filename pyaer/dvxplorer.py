"""DVXPLORER Camera.

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


class DVXPLORER(USBDevice):
    """DVXPLORER.

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
            if enable noise filter.<br/>
            `default is False`
    """
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number="",
                 noise_filter=False):
        """DVXPLORER."""
        super(DVXPLORER, self).__init__()
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        # get camera information
        self.obtain_device_info(self.handle)

        # simple biases arguments
        self.simple_biases = {
            "very_low": libcaer.DVX_DVS_CHIP_BIAS_SIMPLE_VERY_LOW,
            "low": libcaer.DVX_DVS_CHIP_BIAS_SIMPLE_LOW,
            "high": libcaer.DVX_DVS_CHIP_BIAS_SIMPLE_HIGH,
            "very_high": libcaer.DVX_DVS_CHIP_BIAS_SIMPLE_VERY_HIGH,
            "default": libcaer.DVX_DVS_CHIP_BIAS_SIMPLE_DEFAULT}

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
        """Obtain DVXPLORER info.

        This function collects the following information from the device:

        - Device ID
        - Device serial number
        - Device USB bus number
        - Device USB device address
        - Device string
        - Logic version
        - If the device is the master device
        - Logic clock
        - ADC clock
        - Chip ID
        - Camera DVS width
        - Camera DVS height
        - If external input has generator
        - If the device has DVS statistics
        - If the device has MUX statistics

        # Arguments
            handle: `caerDeviceHandle`<br/>
                a valid device handle that can be used with the other
                `libcaer` functions, or `None` on error.
        """
        info = libcaer.caerDVXplorerInfoGet(handle)

        self.device_id = info.deviceID
        self.device_serial_number = info.deviceSerialNumber
        self.device_usb_bus_number = info.deviceUSBBusNumber
        self.device_usb_device_address = info.deviceUSBDeviceAddress
        self.device_string = info.deviceString
        self.firmware_version = info.firmwareVersion
        self.logic_version = info.logicVersion
        self.chip_id = info.chipID
        self.device_is_master = info.deviceIsMaster
        self.mux_has_statistics = info.muxHasStatistics
        self.dvs_size_X = info.dvsSizeX
        self.dvs_size_Y = info.dvsSizeY
        self.dvs_has_statistics = info.dvsHasStatistics
        self.imu_type = info.imuType
        self.ext_input_has_generator = info.extInputHasGenerator

    def open(self,
             device_id=1,
             bus_number_restrict=0,
             dev_address_restrict=0,
             serial_number=""):
        """Open DVXPLORER device.


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
        """
        super(DVXPLORER, self).open(
            libcaer.CAER_DEVICE_DVXPLORER, device_id,
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
        bias_obj = utils.load_dvxplorer_bias(file_path, verbose)
        self.set_bias(bias_obj)

    def set_bias(self, bias_obj):
        """Set bias from bias dictionary.

        # Arguments
            bias_obj: `dict`<br/>
                dictionary that contains DVXPLORER biases.

        # Returns
            flag: `bool`<br/>
                True if set successful, False otherwise.
        """
        # DVX MUX
        self.set_config(libcaer.DVX_MUX,
                        libcaer.DVX_MUX_TIMESTAMP_RESET,
                        bias_obj["mux_timestamp_reset"])
        self.set_config(libcaer.DVX_MUX,
                        libcaer.DVX_MUX_DROP_EXTINPUT_ON_TRANSFER_STALL,
                        bias_obj["drop_extinput_on_transfer_stall"])
        self.set_config(libcaer.DVX_MUX,
                        libcaer.DVX_MUX_DROP_DVS_ON_TRANSFER_STALL,
                        bias_obj["mux_drop_dvs_on_transfer_stall"])

        # DVX EXTINPUT
        self.set_config(libcaer.DVX_EXTINPUT,
                        libcaer.DVX_EXTINPUT_DETECT_RISING_EDGES,
                        bias_obj["extinput_detect_rising_edges"])
        self.set_config(libcaer.DVX_EXTINPUT,
                        libcaer.DVX_EXTINPUT_DETECT_FALLING_EDGES,
                        bias_obj["extinput_detect_falling_edges"])
        self.set_config(libcaer.DVX_EXTINPUT,
                        libcaer.DVX_EXTINPUT_DETECT_PULSES,
                        bias_obj["extinput_detect_pulses"])
        self.set_config(libcaer.DVX_EXTINPUT,
                        libcaer.DVX_EXTINPUT_DETECT_PULSE_POLARITY,
                        bias_obj["extinput_detect_pulse_polarity"])
        self.set_config(libcaer.DVX_EXTINPUT,
                        libcaer.DVX_EXTINPUT_DETECT_PULSE_LENGTH,
                        bias_obj["extinput_detect_pulse_length"])

        # setting for noise filter
        if self.ext_input_has_generator is True:
            self.set_config(libcaer.DVX_EXTINPUT,
                            libcaer.DVX_EXTINPUT_RUN_GENERATOR,
                            bias_obj["extinput_ran_generator"])
            self.set_config(libcaer.DVX_EXTINPUT,
                            libcaer.DVX_EXTINPUT_GENERATE_PULSE_POLARITY,
                            bias_obj["extinput_generate_pulse_polarity"])
            self.set_config(libcaer.DVX_EXTINPUT,
                            libcaer.DVX_EXTINPUT_GENERATE_PULSE_INTERVAL,
                            bias_obj["extinput_generate_pulse_interval"])
            self.set_config(libcaer.DVX_EXTINPUT,
                            libcaer.DVX_EXTINPUT_GENERATE_PULSE_LENGTH,
                            bias_obj["extinput_generate_pulse_length"])
            self.set_config(
                libcaer.DVX_EXTINPUT,
                libcaer.DVX_EXTINPUT_GENERATE_INJECT_ON_RISING_EDGE,
                bias_obj["extinput_generate_inject_on_rising_edge"])
            self.set_config(
                libcaer.DVX_EXTINPUT,
                libcaer.DVX_EXTINPUT_GENERATE_INJECT_ON_FALLING_EDGE,
                bias_obj["extinput_generate_inject_on_falling_edge"])

        # DVX USB
        self.set_config(libcaer.DVX_USB,
                        libcaer.DVX_USB_EARLY_PACKET_DELAY,
                        bias_obj["usb_early_packet_delay"])

        # Set biases
        if "bias_simple" in bias_obj:
            # use system bias configuration, specify all biases otherwise
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_SIMPLE,
                            self.simple_biases[bias_obj["bias_simple"]])
        else:
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_LOG,
                            bias_obj["current_range_log"])
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_SF,
                            bias_obj["current_range_sf"])
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_ON,
                            bias_obj["current_range_on"])
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_nRST,
                            bias_obj["current_range_nrst"])
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_LOGA,
                            bias_obj["current_range_loga"])
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_LOGD,
                            bias_obj["current_range_logd"])
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_LEVEL_SF,
                            bias_obj["current_level_sf"])
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_LEVEL_nOFF,
                            bias_obj["current_level_noff"])
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_AMP,
                            bias_obj["current_amp"])
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_ON,
                            bias_obj["current_on"])
            self.set_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_OFF,
                            bias_obj["current_off"])

    def get_bias(self):
        """Get bias settings.

        # Returns
            bias_obj: `dict`<br/>
                dictionary that contains DVXPLORER current bias settings.
        """
        bias_obj = {}

        # DVX MUX
        bias_obj["mux_timestamp_reset"] = \
            self.get_config(libcaer.DVX_MUX, libcaer.DVX_MUX_TIMESTAMP_RESET)
        bias_obj["drop_extinput_on_transfer_stall"] = \
            self.get_config(libcaer.DVX_MUX,
                            libcaer.DVX_MUX_DROP_EXTINPUT_ON_TRANSFER_STALL)
        bias_obj["mux_drop_dvs_on_transfer_stall"] = \
            self.get_config(libcaer.DVX_MUX,
                            libcaer.DVX_MUX_DROP_DVS_ON_TRANSFER_STALL)

        # DVX IMU
        bias_obj["imu_accel_data_rate"] = \
            self.get_config(libcaer.DVX_IMU, libcaer.DVX_IMU_ACCEL_DATA_RATE)
        bias_obj["imu_accel_filter"] = \
            self.get_config(libcaer.DVX_IMU, libcaer.DVX_IMU_ACCEL_FILTER)
        bias_obj["imu_accel_range"] = \
            self.get_config(libcaer.DVX_IMU, libcaer.DVX_IMU_ACCEL_RANGE)
        bias_obj["imu_gyro_data_rate"] = \
            self.get_config(libcaer.DVX_IMU, libcaer.DVX_IMU_GYRO_DATA_RATE)
        bias_obj["imu_gyro_filter"] = \
            self.get_config(libcaer.DVX_IMU, libcaer.DVX_IMU_GYRO_FILTER)
        bias_obj["imu_gyro_range"] = \
            self.get_config(libcaer.DVX_IMU, libcaer.DVX_IMU_GYRO_RANGE)

        # DVX EXTINPUT
        bias_obj["extinput_detect_rising_edges"] = \
            self.get_config(libcaer.DVX_EXTINPUT,
                            libcaer.DVX_EXTINPUT_DETECT_RISING_EDGES)
        bias_obj["extinput_detect_falling_edges"] = \
            self.get_config(libcaer.DVX_EXTINPUT,
                            libcaer.DVX_EXTINPUT_DETECT_FALLING_EDGES)
        bias_obj["extinput_detect_pulses"] = \
            self.get_config(libcaer.DVX_EXTINPUT,
                            libcaer.DVX_EXTINPUT_DETECT_PULSES)
        bias_obj["extinput_detect_pulse_polarity"] = \
            self.get_config(libcaer.DVX_EXTINPUT,
                            libcaer.DVX_EXTINPUT_DETECT_PULSE_POLARITY)
        bias_obj["extinput_detect_pulse_length"] = \
            self.get_config(libcaer.DVX_EXTINPUT,
                            libcaer.DVX_EXTINPUT_DETECT_PULSE_LENGTH)

        # setting for noise filter
        if self.ext_input_has_generator is True:
            bias_obj["extinput_ran_generator"] = \
                self.get_config(libcaer.DVX_EXTINPUT,
                                libcaer.DVX_EXTINPUT_RUN_GENERATOR)
            bias_obj["extinput_generate_pulse_polarity"] = \
                self.get_config(libcaer.DVX_EXTINPUT,
                                libcaer.DVX_EXTINPUT_GENERATE_PULSE_POLARITY)
            bias_obj["extinput_generate_pulse_interval"] = \
                self.get_config(libcaer.DVX_EXTINPUT,
                                libcaer.DVX_EXTINPUT_GENERATE_PULSE_INTERVAL)
            bias_obj["extinput_generate_pulse_length"] = \
                self.get_config(libcaer.DVX_EXTINPUT,
                                libcaer.DVX_EXTINPUT_GENERATE_PULSE_LENGTH)
            bias_obj["extinput_generate_inject_on_rising_edge"] = \
                self.get_config(
                    libcaer.DVX_EXTINPUT,
                    libcaer.DVX_EXTINPUT_GENERATE_INJECT_ON_RISING_EDGE)
            bias_obj["extinput_generate_inject_on_falling_edge"] = \
                self.get_config(
                    libcaer.DVX_EXTINPUT,
                    libcaer.DVX_EXTINPUT_GENERATE_INJECT_ON_FALLING_EDGE)

        # DVX USB
        bias_obj["usb_early_packet_delay"] = \
            self.get_config(libcaer.DVX_USB,
                            libcaer.DVX_USB_EARLY_PACKET_DELAY)

        # Set biases
        bias_obj["current_range_log"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_LOG)
        bias_obj["current_range_sf"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_SF)
        bias_obj["current_range_on"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_ON)
        bias_obj["current_range_nrst"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_nRST)
        bias_obj["current_range_loga"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_LOGA)
        bias_obj["current_range_logd"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_RANGE_LOGD)
        bias_obj["current_level_sf"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_LEVEL_SF)
        bias_obj["current_level_noff"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_LEVEL_nOFF)
        bias_obj["current_amp"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_AMP)
        bias_obj["current_on"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_ON)
        bias_obj["current_off"] = \
            self.get_config(libcaer.DVX_DVS_CHIP_BIAS,
                            libcaer.DVX_DVS_CHIP_BIAS_CURRENT_OFF)

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

    def start_data_stream(self, send_default_config=True,
                          max_packet_size=None,
                          max_packet_interval=None):
        """Start streaming data.

        # Arguments
            send_default_config: `bool`<br/>
                send default config to the device before starting
                the data streaming.<br/>
                `default is True`
            max_packet_size: `int`<br/>
                set the maximum number of events any of a packet container's
                packets may hold before it's made available to the user.
                Set to zero to disable.<br/>
                The default is `None` (use default setting: 0).
            max_packet_interval: `int`<br/>
                set the time interval between subsequent packet containers.
                Must be at least 1 microsecond.
                The value is in microseconds, and is checked across all
                types of events contained in the EventPacketContainer.<br/>
                The default is `None` (use default setting: 10ms)
        """
        if send_default_config is True:
            self.send_default_config()

        if max_packet_size is not None:
            self.set_max_container_packet_size(max_packet_size)
        if max_packet_interval is not None:
            self.set_max_container_interval(max_packet_interval)

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
        """Get Event.

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
            imu_events: `numpy.ndarray`<br/>
                a 2-D array that has the shape of (N, 8) where N
                is the number of IMU6 events in the packet.
                Each row of the array consists a single IMU6 event.
                The first value is the timestamp of the event.
                The next three values are accelerations on the X, Y, and Z
                axes. The next three values are angular velocity
                on the X, Y and Z axes.
                The last value is the temperature in Celsius scale.
            num_imu_events: `int`<br/>
                number of the IMU6 events.
        """
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None:
            num_pol_event = 0
            num_special_event = 0
            num_imu_event = 0
            pol_events = None
            special_events = None
            imu_events = None
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
                        hist, num_events = \
                            self.get_polarity_hist(
                                packet_header, device_type=self.chip_id)
                        pol_events = hist if pol_events is None else \
                            pol_events+hist
                    elif mode == "counter_neuron":
                        hist, num_events = \
                            self.get_counter_neuron_event(
                                packet_header, device_type=self.chip_id)
                        pol_events = hist if pol_events is None else \
                            pol_events+hist
                    num_pol_event += num_events
                elif packet_type == libcaer.SPECIAL_EVENT:
                    events, num_events = self.get_special_event(
                        packet_header)
                    special_events = np.hstack((special_events, events)) \
                        if special_events is not None else events
                    num_special_event += num_events
                elif packet_type == libcaer.IMU6_EVENT:
                    events, num_events = self.get_imu6_event(
                        packet_header)
                    imu_events = np.hstack((imu_events, events)) \
                        if imu_events is not None else events
                    num_imu_event += num_events

            libcaer.caerEventPacketContainerFree(packet_container)

            return (pol_events, num_pol_event,
                    special_events, num_special_event,
                    imu_events, num_imu_event)
        else:
            return None
