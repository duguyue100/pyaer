"""Testing DVS Noise filter implementation.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import

from pyaer.filters import DVSNoise

# for the case of DVS128
dvs_noise = DVSNoise(128, 128)

dvs_noise.set_bias_from_json("./scripts/configs/dvs_noise_filter_config.json")

print (dvs_noise.get_bias())
