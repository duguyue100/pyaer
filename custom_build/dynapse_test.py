"""DYNAP-SE Test Example.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

from pyaer.dynapse import DYNAPSE
from pyaer import utils

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

device.start_data_stream()

bias_obj = utils.load_dynapse_bias("./scripts/configs/dynapse_config.json")

# set bias from json file
scope = {
    0: [0, 1, 2, 3],
    }

device.set_bias_from_json("./scripts/configs/dynapse_config.json",
                          clear_sram=False, setup_sram=False,
                          fpga_bias=True, scope=scope)
# print FPGA biases
print (device.get_fpga_bias())

# set biases for a single chip
device.set_chip_bias(bias_obj, chip_id=1)

while True:
    try:
        events = device.get_event()

        if events is not None:
            print ("Number of events from DYNAPSE : %d" %
                   (events[1]))
    except KeyboardInterrupt:
        print ("Device shutting down...")
        device.shutdown()
        break
