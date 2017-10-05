"""DVS128 Test.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function
from pyaer.dvs128 import DVS128

device = DVS128()

print ("Device ID:", device.device_id)
if device.device_is_master:
    print ("Device is master.")
else:
    print ("Device is slave.")
print ("Device Serial Number:", device.device_serial_number)
print ("Device String:", device.device_string)
print ("Device USB bus Number:", device.device_usb_bus_number)
print ("Device USB device address:", device.device_usb_device_address)
print ("Device size X:", device.dvs_size_X)
print ("Device size Y:", device.dvs_size_Y)
print ("Logic Version:", device.logic_version)

packet_container, packet_number = device.get_packet_container()

print (type(packet_container))
print (packet_number)

#  while True:
#      (pol_ts, pol_xy, pol_pol, num_pol_event,
#       special_ts, special_event_data, num_special_event) = \
#          device.get_event()
#
#      print ("Number of events:", num_pol_event, "Number of special events:",
#             num_special_event)

#  device.close()
