"""Check device discovery."""

from pyaer import libcaer


discovered_result = libcaer.device_discover_new(-1)

print(discovered_result.deviceInfo.davisInfo.deviceString)
