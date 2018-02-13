"""DYNAPSE.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from builtins import range
import time
import numpy as np
from pyaer import libcaer
from pyaer import utils
from pyaer.device import USBDevice


class DYNAPSE(USBDevice):
    """Class defines DYNAPSE."""
    def __init__(self,
                 device_id=1,
                 bus_number_restrict=0,
                 dev_address_restrict=0,
                 serial_number=""):
        """DYNAPSE.

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
        super(DYNAPSE, self).__init__()
        # open device
        self.open(device_id, bus_number_restrict,
                  dev_address_restrict, serial_number)
        # get camera info
        self.obtain_device_info(self.handle)

        # jump directions
        self.DYNAPSE_CONFIG_SRAM_DIRECTION_X_EAST = \
            libcaer.DYNAPSE_CONFIG_SRAM_DIRECTION_X_EAST
        self.DYNAPSE_CONFIG_SRAM_DIRECTION_X_WEST = \
            libcaer.DYNAPSE_CONFIG_SRAM_DIRECTION_X_WEST
        self.DYNAPSE_CONFIG_SRAM_DIRECTION_Y_NORTH = \
            libcaer.DYNAPSE_CONFIG_SRAM_DIRECTION_Y_NORTH
        self.DYNAPSE_CONFIG_SRAM_DIRECTION_Y_SOUTH = \
            libcaer.DYNAPSE_CONFIG_SRAM_DIRECTION_Y_SOUTH

        # synaptic weights
        self.DYNAPSE_CONFIG_CAMTYPE_F_EXC = \
            libcaer.DYNAPSE_CONFIG_CAMTYPE_F_EXC
        self.DYNAPSE_CONFIG_CAMTYPE_S_EXC = \
            libcaer.DYNAPSE_CONFIG_CAMTYPE_S_EXC
        self.DYNAPSE_CONFIG_CAMTYPE_F_INH = \
            libcaer.DYNAPSE_CONFIG_CAMTYPE_F_INH
        self.DYNAPSE_CONFIG_CAMTYPE_S_INH = \
            libcaer.DYNAPSE_CONFIG_CAMTYPE_S_INH

    def obtain_device_info(self, handle):
        """Obtain DYNAPSE info."""
        if handle is not None:
            info = libcaer.caerDynapseInfoGet(handle)

            # port all info data fields out
            self.device_id = info.deviceID
            self.device_serial_number = info.deviceSerialNumber
            self.device_usb_bus_number = info.deviceUSBBusNumber
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
        super(DYNAPSE, self).open(
            libcaer.CAER_DEVICE_DYNAPSE, device_id,
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
        # DYNAPSE_CONFIG_MUX
        self.set_config(libcaer.DYNAPSE_CONFIG_MUX,
                        libcaer.DYNAPSE_CONFIG_MUX_TIMESTAMP_RESET,
                        bias_obj["mux_timestamp_reset"])
        self.set_config(libcaer.DYNAPSE_CONFIG_MUX,
                        libcaer.DYNAPSE_CONFIG_MUX_FORCE_CHIP_BIAS_ENABLE,
                        bias_obj["mux_force_chip_bias_enable"])
        self.set_config(libcaer.DYNAPSE_CONFIG_MUX,
                        libcaer.DYNAPSE_CONFIG_MUX_DROP_AER_ON_TRANSFER_STALL,
                        bias_obj["mux_drop_aer_on_transfer_stall"])

        # DYNAPSE_CONFIG_AER
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_ACK_DELAY,
                        bias_obj["aer_ack_delay"])
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_ACK_EXTENSION,
                        bias_obj["aer_ack_extension"])
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_WAIT_ON_TRANSFER_STALL,
                        bias_obj["aer_wait_on_transfer_stall"])
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_EXTERNAL_AER_CONTROL,
                        bias_obj["aer_external_aer_control"])

        # DYNAPSE_CONFIG_CHIP
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_REQ_DELAY,
                        bias_obj["chip_req_delay"])
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_REQ_EXTENSION,
                        bias_obj["chip_req_extension"])

        self.set_config(libcaer.DYNAPSE_CONFIG_USB,
                        libcaer.DYNAPSE_CONFIG_USB_EARLY_PACKET_DELAY,
                        bias_obj["usb_early_packet_delay"])

        # Turn on chip and AER communication for configuration.
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_RUN,
                        True)
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_RUN,
                        True)

        # Set silent biases (not activity)
        # TODO

        # Clear all SRAM
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U0)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM_EMPTY, 0, 0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U1)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM_EMPTY, 0, 0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U2)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM_EMPTY, 0, 0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U3)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM_EMPTY, 0, 0)

        # Set low power biases (some activity)
        # TODO

        # Setup SRAM for USB monitoring of spike events
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U0)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U0,
                        0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U1)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U1,
                        0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U2)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U2,
                        0)
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_ID,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U3)
        self.set_config(libcaer.DYNAPSE_CONFIG_DEFAULT_SRAM,
                        libcaer.DYNAPSE_CONFIG_DYNAPSE_U3,
                        0)

        # Turn off chip/AER once done
        self.set_config(libcaer.DYNAPSE_CONFIG_CHIP,
                        libcaer.DYNAPSE_CONFIG_CHIP_RUN,
                        False)
        self.set_config(libcaer.DYNAPSE_CONFIG_AER,
                        libcaer.DYNAPSE_CONFIG_AER_RUN,
                        False)

        # Essential: wait for chip to be stable
        time.sleep(1)

    def start_data_stream(self):
        """Start streaming data."""
        self.data_start()
        self.set_data_exchange_blocking()

    def core_xy_to_neuron_id(self, core_id, column_x, row_y):
        """Map core ID and column/row address.
        to the correct chip global neuron address.

        # Parameters
        core_id : uint8
            the chip's core ID, range [0,3].
        column_x : uint8
            the neuron's column address, range [0,15].
        row_y : uint8
            the neuron's row address, range [0,15].

        # Returns
        neuron_id : uint16
            chip global neuron address
        """
        return libcaer.caerDynapseCoreXYToNeuronId(
            coreId=core_id,
            columnX=column_x,
            rowY=row_y)

    def core_id_to_neuron_id(self, core_id, neuron_id_core):
        """Map core ID and per-core neuron address.
        to the correct chip global neuron address.

        # Parameters
        core_id : uint8
            the chip's core ID, range [0,3].
        neuron_id_core : uint8
            the neuron's address within this core, range [0,255].

        # Returns
        neuron_id : uint16
            chip global neuron address.
        """
        return libcaer.caerDynapseCoreAddrToNeuronId(
            coreId=core_id,
            neuronAddrCore=neuron_id_core)

    def write_poisson_spikerate(self, neuron_id, rate):
        """Specifies the poisson spike generator's spike rate.

        # Parameters
        neuron_id : uint16
            The target neuron of the poisson spike train, range [0,1023].
        rate : float
            The rate in Hz of the spike train, this will be quantized to the
            nearest supported level, range [0, 4300].

        # Returns
        flag : bool
            True if success, False otherwise
        """
        return libcaer.caerDynapseWritePoissonSpikeRate(
            self.handle, neuronAddr=neuron_id, rateHz=rate)

    def write_sram_N(self, neuron_id, sram_id, virtual_core_id, sx,
                     dx, sy, dy, destination_core):
        """Write one of the 4 SRAMs of a single neuron.

        Writing the SRAM means writing the destination
        address of where the spikes will be routed to.
        This works on the on-chip SRAM!

        # Parameters
        neuron_id : uint16
            the neuron to program, range [0,1023]
        sram_id : uint8
            SRAM address, range [0, 3]
        virtual_core_id : utin8
            fake source core ID, set it to this value
            instead of the actual source core ID, range [0,3].
        sx : bool
            X direction, can be one of:
            [DYNAPSE_CONFIG_SRAM_DIRECTION_X_EAST,
             DYNAPSE_CONFIG_SRAM_DIRECTION_X_WEST].
        dx : uint8
            X delta, number of chips to jumps before
            reaching destination, range is [0, 3]
        sy : bool
            Y direction, can be one of:
            [DYNAPSE_CONFIG_SRAM_DIRECTION_Y_NORTH,
             DYNAPSE_CONFIG_SRAM_DIRECTION_Y_SOUTH].
        dy : uint8
            number of chips to jumps before reaching destination,
            range is [0, 3]
        destination_core : uint8
            spike destination core, uses one-hot coding for the 4 cores
            [C3,C2,C1,C0] -> [0,0,0,0] (0 decimal) no core,
            [1,1,1,1] (15 decimal) all cores

        # Returns
        flag : bool
            True if success, False otherwise
        """
        return libcaer.caerDynapseWriteSramN(
            handle=self.handle,
            neuronAddr=neuron_id,
            sramId=sram_id,
            virtualCoreId=virtual_core_id,
            sx=sx, dx=dx, sy=sy, dy=dy,
            destinationCore=destination_core)

    def write_cam(self, input_neuron_id, neuron_id, cam_id, synapse_type):
        """Write a single CAM.

        To specify which spikes are allowed as input into a neuron.

        # Parameters
        input_neuron_id : uint16
            the neuron address that should be let in as input to this neuron,
            range [0,1023].
        neuron_id : uint16
            the neuron address whose CAM should be programmed, range [0,1023].
        cam_id : uint8
            CAM address (synapse), each neuron has 64, range [0,63].
        synapse_type : uint8
            one of the four possible synaptic weights:
            [DYNAPSE_CONFIG_CAMTYPE_F_EXC,
             DYNAPSE_CONFIG_CAMTYPE_S_EXC,
             DYNAPSE_CONFIG_CAMTYPE_F_INH,
             DYNAPSE_CONFIG_CAMTYPE_S_INH].

        # Returns
        flag : bool
            True if success, False otherwise
        """
        return libcaer.caerDynapseWriteCam(
            handle=self.handle,
            inputNeuronAddr=input_neuron_id,
            neuronAddr=neuron_id,
            camId=cam_id,
            synapseType=synapse_type)

    def get_event(self):
        """Get Event.

        Maybe not so efficient.
        """
        packet_container, packet_number = self.get_packet_container()
        if packet_container is not None:
            num_spike_events = 0
            spike_events = None

            for packet_id in range(packet_number):
                packet_header, packet_type = self.get_packet_header(
                    packet_container, packet_id)
                if packet_type == libcaer.SPIKE_EVENT:
                    events, num_events = self.get_spike_event(packet_header)
                    spike_events = np.hstack((spike_events, events)) \
                        if spike_events is not None else events
                    num_spike_events += num_events
            libcaer.caerEventPacketContainerFree(packet_container)
        return (spike_events, num_spike_events)
