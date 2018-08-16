"""DAVIS346 test example.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

import cv2
import numpy as np

from pyaer import libcaer
from pyaer.davis import DAVIS

device = DAVIS(noise_filter=True)

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
print ("Background Activity Filter:",
       device.dvs_has_background_activity_filter)

device.start_data_stream()
# setting bias after data stream started
device.set_bias_from_json("./scripts/configs/davis346_config.json")

clip_value = 3
histrange = [(0, v) for v in (260, 346)]


def get_event(device):
    data = device.get_event()

    return data


num_packet_before_disable = 1000

while True:
    try:
        data = get_event(device)
        if data is not None:
            (pol_events, num_pol_event,
             special_events, num_special_event,
             frames_ts, frames, imu_events,
             num_imu_event) = data
            if frames.shape[0] != 0:
                cv2.imshow("frame", frames[0])

            print ("Number of events:", num_pol_event, "Number of Frames:",
                   frames.shape, "Exposure:",
                   device.get_config(
                       libcaer.DAVIS_CONFIG_APS,
                       libcaer.DAVIS_CONFIG_APS_EXPOSURE),
                   "Autoexposure:", device.get_config(
                       libcaer.DAVIS_CONFIG_APS,
                       libcaer.DAVIS_CONFIG_APS_AUTOEXPOSURE))

            if num_pol_event != 0:
                if num_packet_before_disable > 0:
                    print (pol_events[:, 4].sum())
                    pol_events = pol_events[pol_events[:, 4] == 1]
                    num_packet_before_disable -= 1
                else:
                    device.disable_noise_filter()
                    print ("Noise filter disabled")
                pol_on = (pol_events[:, 3] == 1)
                pol_off = np.logical_not(pol_on)
                img_on, _, _ = np.histogram2d(
                        pol_events[pol_on, 2], pol_events[pol_on, 1],
                        bins=(260, 346), range=histrange)
                img_off, _, _ = np.histogram2d(
                        pol_events[pol_off, 2], pol_events[pol_off, 1],
                        bins=(260, 346), range=histrange)
                if clip_value is not None:
                    integrated_img = np.clip(
                        (img_on-img_off), -clip_value, clip_value)
                else:
                    integrated_img = (img_on-img_off)
                img = integrated_img+clip_value

                cv2.imshow("image", img/float(clip_value*2))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            pass

    except KeyboardInterrupt:
        device.shutdown()
        break
