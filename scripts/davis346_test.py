"""DAVIS346 test example.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

import cv2

from pyaer.davis import DAVIS

device = DAVIS()

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


flag = device.send_default_config()
if flag:
    print ("Default bias set")
else:
    print ("Default bias set error")
device.start_data_stream()


def get_event(device):
    data = device.get_event()

    return data


while True:
    try:
        data = get_event(device)
        if data is not None:
            (pol_ts, pol_xy, pol_pol, num_pol_event,
             special_ts, special_event_data, num_special_event,
             frames_ts, frames, imu_ts, imu_acc, imu_gyro, imu_temp,
             num_imu_event) = data
            if frames.shape[0] != 0:
                cv2.imshow("frame", frames[0])

            print ("Number of events:", num_pol_event, "Number of Frames:",
                   frames.shape)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            pass

    except KeyboardInterrupt:
        device.shutdown()
        break
