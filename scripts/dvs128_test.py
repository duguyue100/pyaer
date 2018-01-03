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

# load new config
device.set_bias_from_json("./scripts/configs/dvs128_config.json")
print (device.get_bias())

device.start_data_stream()


def get_event(device):
    (pol_ts, pol_xy, pol_pol, num_pol_event,
     special_ts, special_event_data, num_special_event) = \
        device.get_event()
    return (pol_ts, pol_xy, pol_pol, num_pol_event,
            special_ts, special_event_data, num_special_event)


while True:
    try:
        (pol_ts, pol_xy, pol_pol, num_pol_event,
         special_ts, special_event_data, num_special_event) = \
            get_event(device)

        if num_pol_event != 0:
            img = np.zeros((128, 128), dtype=np.float)
            for event_id in range(num_pol_event):
                if pol_pol[event_id] and \
                        img[pol_xy[1, event_id], pol_xy[0, event_id]] < 3:
                    img[pol_xy[1, event_id], pol_xy[0, event_id]] += 1
                elif pol_pol[event_id] is False and \
                        img[pol_xy[1, event_id], pol_xy[0, event_id]] > -3:
                    img[pol_xy[1, event_id], pol_xy[0, event_id]] -= 1
            img = (img+3.)/6.
            cv2.imshow("image", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        print ("Number of events:", num_pol_event, "Number of special events:",
               num_special_event)
    except KeyboardInterrupt:
            device.shutdown()
            break
