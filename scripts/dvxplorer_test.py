"""DVXplorer Test.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""

from __future__ import absolute_import
from __future__ import print_function

import cv2
import numpy as np

from pyaer.dvxplorer import DVXPLORER


device = DVXPLORER()

print("Device ID:", device.device_id)
print("Device Serial Number:", device.device_serial_number)
print("Device USB bus Number:", device.device_usb_bus_number)
print("Device USB device address:", device.device_usb_device_address)
print("Device String:", device.device_string)
print("Device Firmware Version:", device.firmware_version)
print("Logic Version:", device.logic_version)
print("Device Chip ID:", device.chip_id)
if device.device_is_master:
    print("Device is master.")
else:
    print("Device is slave.")
print("MUX has statistics:", device.mux_has_statistics)
print("Device size X:", device.dvs_size_X)
print("Device size Y:", device.dvs_size_Y)
print("DVS has statistics:", device.dvs_has_statistics)
print("IMU Type:", device.imu_type)
print("EXT input has generator:", device.ext_input_has_generator)

clip_value = 3
histrange = [(0, v) for v in (device.dvs_size_Y, device.dvs_size_X)]

device.start_data_stream()
# load new config
device.set_bias_from_json("./scripts/configs/dvxplorer_config.json")

print(device.get_bias())

while True:
    try:
        (
            pol_events,
            num_pol_event,
            special_events,
            num_special_event,
            imu_events,
            num_imu_event,
        ) = device.get_event("events_hist")

        print("Number of events:", num_pol_event)

        if num_pol_event != 0:
            img = pol_events[..., 1] - pol_events[..., 0]
            img = np.clip(img, -clip_value, clip_value)
            img = (img + clip_value) / float(clip_value * 2)

            cv2.imshow("image", img)

            cv2.waitKey(1)

    except KeyboardInterrupt:
        device.shutdown()
        cv2.destroyAllWindows()
        break
