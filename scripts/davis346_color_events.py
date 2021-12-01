"""DAVIS346 test example.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

import cv2
import numpy as np

from pyaer import libcaer
from pyaer.davis import DAVIS

device = DAVIS(noise_filter=False, color_filter=True)

print("Device ID:", device.device_id)
if device.device_is_master:
    print("Device is master.")
else:
    print("Device is slave.")
print("Device Serial Number:", device.device_serial_number)
print("Device String:", device.device_string)
print("Device USB bus Number:", device.device_usb_bus_number)
print("Device USB device address:", device.device_usb_device_address)
print("Device size X:", device.dvs_size_X)
print("Device size Y:", device.dvs_size_Y)
print("Logic Version:", device.logic_version)
print("Background Activity Filter:",
      device.dvs_has_background_activity_filter)
print("Color Filter", device.aps_color_filter, type(device.aps_color_filter))
print(device.aps_color_filter == 1)

device.start_data_stream()
# setting bias after data stream started
device.set_bias_from_json("./scripts/configs/davis346_config.json")

clip_value = 1
histrange = [(0, v) for v in (260, 346)]


def get_event(device):
    data = device.get_event()

    return data


empty_img = np.zeros((260, 346, 3), dtype=np.float)


while True:
    try:
        data = get_event(device)
        if data is not None:
            (pol_events, num_pol_event,
             special_events, num_special_event,
             frames_ts, frames, imu_events,
             num_imu_event) = data
            if frames.shape[0] != 0:
                frame = cv2.cvtColor(frames[0], cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, dsize=(692, 520),
                                   interpolation=cv2.INTER_LINEAR)
                cv2.imshow("frame", frame)

            if pol_events is not None:
                print("Number of events:", pol_events.shape,
                      "Number of Frames:",
                      frames.shape, "Exposure:",
                      device.get_config(
                          libcaer.DAVIS_CONFIG_APS,
                          libcaer.DAVIS_CONFIG_APS_EXPOSURE),
                      "Autoexposure:", device.get_config(
                          libcaer.DAVIS_CONFIG_APS,
                          libcaer.DAVIS_CONFIG_APS_AUTOEXPOSURE),
                      "Color:", pol_events[0, 4])

            if num_pol_event != 0:
                # extract color events
                pol_g_1 = (pol_events[:, 4] == 1)  # lower left green
                pol_b = (pol_events[:, 4] == 2)  # lower right blue
                pol_r = (pol_events[:, 4] == 3)  # upper left red
                pol_g_2 = (pol_events[:, 4] == 4)  # upper right green

                g_1, _, _ = np.histogram2d(
                    pol_events[pol_g_1, 2], pol_events[pol_g_1, 1],
                    bins=(260, 346), range=histrange)
                b, _, _ = np.histogram2d(
                    pol_events[pol_b, 2], pol_events[pol_b, 1],
                    bins=(260, 346), range=histrange)
                r, _, _ = np.histogram2d(
                    pol_events[pol_r, 2], pol_events[pol_r, 1],
                    bins=(260, 346), range=histrange)
                g_2, _, _ = np.histogram2d(
                    pol_events[pol_g_2, 2], pol_events[pol_g_2, 1],
                    bins=(260, 346), range=histrange)

                g_1 = np.clip(g_1, None, clip_value)/float(clip_value)
                b = np.clip(b, None, clip_value)/float(clip_value)
                r = np.clip(r, None, clip_value)/float(clip_value)
                g_2 = np.clip(g_2, None, clip_value)/float(clip_value)

                ig_1 = np.zeros((260, 346, 3), dtype=np.float)
                ib = np.zeros((260, 346, 3), dtype=np.float)
                ir = np.zeros((260, 346, 3), dtype=np.float)
                ig_2 = np.zeros((260, 346, 3), dtype=np.float)

                #  ig_1[..., 0], ig_1[..., 2] = g_1, g_1
                #  ib[..., 1], ib[..., 2] = b, b
                #  ir[..., 0], ir[..., 1] = r, r
                #  ig_2[..., 0], ig_2[..., 2] = g_2, g_2

                ig_1[..., 1] = g_1
                ib[..., 0] = b
                ir[..., 2] = r
                ig_2[..., 1] = g_2

                img = np.vstack((
                    np.hstack((ir, ig_2)),
                    np.hstack((ig_1, ib))))

                cv2.imshow("image", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            pass

    except KeyboardInterrupt:
        device.shutdown()
        break
