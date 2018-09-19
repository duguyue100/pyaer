"""DVS128 Test.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

import numpy as np
import cv2

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

device.start_data_stream()
# load new config
device.set_bias_from_json("./scripts/configs/dvs128_config.json")
print (device.get_bias())

clip_value = 3
histrange = [(0, v) for v in (128, 128)]

while True:
    try:
        (pol_events, num_pol_event,
         special_events, num_special_event) = \
            device.get_event("events_hist")
        if num_pol_event != 0:
            img = pol_events[..., 1]-pol_events[..., 0]
            img = np.clip(img, -clip_value, clip_value)
            img = img+clip_value

            cv2.imshow("image", img/float(clip_value*2))
            print ("Number of events:", num_pol_event, "Number of special events:",
                   num_special_event)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        device.shutdown()
        break
