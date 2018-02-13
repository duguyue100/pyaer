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

device.set_bias_from_json("./scripts/configs/dynapse_config.json")
print (device.get_bias())


print ("Device shutting down...")
device.shutdown()

#  while True:
#      try:
#          (events, num_spike_events) = \
#              device.get_event()
#
#          print ("Number of events from DYNAPSE : %d" %
#                 (num_spike_events))
#      except KeyboardInterrupt:
#          print ("Device shutting down...")
#          device.shutdown()
#          break
