"""DYNAP-SE Test Example.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

from pyaer.dynapse import DYNAPSE

device = DYNAPSE()

print ("Device ID:", device.device_id)
if device.device_is_master:
    print ("Device is master.")
else:
    print ("Device is slave.")
print ("Device Serial Number:", device.device_serial_number)
print ("Device String:", device.device_string)
print ("Device USB bus Number:", device.device_usb_bus_number)
print ("Device USB device address:", device.device_usb_device_address)
print ("Logic Version:", device.logic_version)
print ("Logic Clock:", device.logic_clock)
print ("Chip ID:", device.chip_id)
print ("AER has statistics:", device.aer_has_statistics)
print ("MUX has statistics:", device.mux_has_statistics)

device.send_default_config()
device.start_data_stream()

neuron_1 = device.core_xy_to_neuron_id(0, 3, 4)
neuron_2 = device.core_xy_to_neuron_id(0, 5, 7)

print ("Core 0, Column 3, Row 4:", neuron_1)
print ("Core 0, Column 5, Row 7:", neuron_2)

while True:
    try:
        (spike_ts, spike_neuron_id, spike_core_id, spike_chip_id,
         num_spike_events) = \
            device.get_event()

        num_event_1 = (spike_neuron_id == neuron_1).sum()
        num_event_2 = (spike_neuron_id == neuron_2).sum()

        print ("Number of events from neuron 1: %d, neuron 2: %d" %
               (num_event_1, num_event_2))
    except KeyboardInterrupt:
        break

# connect neuron 1 to neuron 2
device.write_cam(neuron_1, neuron_2, 5,
                 device.DYNAPSE_CONFIG_CAMTYPE_F_EXC)

# send spiker to neuron 1
device.write_poisson_spikerate(neuron_1, 2000)

while True:
    try:
        (spike_ts, spike_neuron_id, spike_core_id, spike_chip_id,
         num_spike_events) = \
            device.get_event()

        num_event_1 = (spike_neuron_id == neuron_1).sum()
        num_event_2 = (spike_neuron_id == neuron_2).sum()

        print ("Number of events from neuron %d: %d, neuron %d: %d" %
               (neuron_1, num_event_1, neuron_2, num_event_2))
    except KeyboardInterrupt:
        device.shutdown()
        break
