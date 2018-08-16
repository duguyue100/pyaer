"""Testing DVS Noise filter implementation.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import

import cv2
import numpy as np

from pyaer.dvs128 import DVS128

device = DVS128(noise_filter=True)

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

clip_value = 1
histrange = [(0, v) for v in (128, 128)]


num_packet_before_disable = 1000


def get_event(device):
    global num_packet_before_disable
    (pol_events, num_pol_event,
     special_events, num_special_event) = \
        device.get_event()
    if num_pol_event != 0:
        if num_packet_before_disable > 0:
            pol_events = pol_events[pol_events[:, 4] == 1]
            num_packet_before_disable -= 1
        else:
            device.disable_noise_filter()
            print ("Noise filter disabled")

        pol_on = (pol_events[:, 3] == 1)
        pol_off = np.logical_not(pol_on)
        img_on, _, _ = np.histogram2d(
                pol_events[pol_on, 2], pol_events[pol_on, 1],
                bins=(128, 128), range=histrange)
        img_off, _, _ = np.histogram2d(
                pol_events[pol_off, 2], pol_events[pol_off, 1],
                bins=(128, 128), range=histrange)
        if clip_value is not None:
            integrated_img = np.clip(
                (img_on-img_off), -clip_value, clip_value)
        else:
            integrated_img = (img_on-img_off)
        img = integrated_img+clip_value

        cv2.imshow("image", img/float(clip_value*2))
        print ("Number of events:", num_pol_event, "Number of special events:",
               num_special_event)
        del pol_events, num_pol_event, special_events, num_special_event

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return


while True:
    try:
        get_event(device)

    except KeyboardInterrupt:
        hot_pixels = device.noise_filter.get_hot_pixels()
        print (hot_pixels)
        print (device.noise_filter.get_bias())
        device.shutdown()
        break
