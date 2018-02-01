"""DVS128 Threaded Test.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

import threading
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

# global variable
clip_value = 3
histrange = [(0, v) for v in (128, 128)]


def drawing_func():
    pass


def fetching_func():
    pass


# define thread
drawer = threading.Thread(name="drawer", target=drawing_func)
fetcher = threading.Thread(name="fetcher", target=fetching_func)




def get_event(device):
    (pol_events, num_pol_event,
     special_events, num_special_event) = \
        device.get_event()
    return (pol_events, num_pol_event,
            special_events, num_special_event)


while True:
    try:
        (pol_events, num_pol_event,
         special_events, num_special_event) = get_event(device)

        if num_pol_event != 0:
            pol_on = (pol_events[:, 3] == 1)
            pol_off = np.logical_not(pol_on)
            img_on, _, _ = np.histogram2d(
                    pol_events[pol_on, 2], pol_events[pol_on, 1],
                    bins=(128, 128), range=histrange)
            img_off, _, _ = np.histogram2d(
                    pol_events[pol_off, 1], pol_events[pol_off, 0],
                    bins=(128, 128), range=histrange)
            if clip_value is not None:
                integrated_img = np.clip(
                    (img_on-img_off), -clip_value, clip_value)
            else:
                integrated_img = (img_on-img_off)
            img = integrated_img+clip_value

            cv2.imshow("image", img/float(clip_value*2))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        print ("Number of events:", num_pol_event, "Number of special events:",
               num_special_event)
    except KeyboardInterrupt:
            device.shutdown()
            break
