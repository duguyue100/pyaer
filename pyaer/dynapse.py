"""DYNAPSE.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from builtins import range
import numpy as np
from pyaer import libcaer
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
