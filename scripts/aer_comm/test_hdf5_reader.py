"""Test the HDF5 reader.

Author: Yuhuang Hu
Email : yuhuang.hu@ini.uzh.ch
"""

from __future__ import print_function, absolute_import

import os
from contextlib import suppress
from pyaer.comm import AERHDF5Reader


data_path = os.path.join(
    os.environ["HOME"], "data", "pyaer_test.hdf5")

reader = AERHDF5Reader(data_path)

for device, groups in reader.get_keys().items():
    for group_name in groups:

        frame = reader.get_frame(device, group_name)
        events = reader.get_polarity_events(device, group_name)
        imu = reader.get_imu_events(device, group_name)
        special = reader.get_special_events(device, group_name)

        print("-"*50)
        with suppress(Exception):
            print("Frame:", frame.shape)

        with suppress(Exception):
            print("Events:", events.shape)

        with suppress(Exception):
            print("IMU:", imu.shape)

        with suppress(Exception):
            print("Special:", special.shape)
