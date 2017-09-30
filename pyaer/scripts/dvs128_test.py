"""DVS128 Test.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""

from pyaer import libcaer

handle = libcaer.caerDeviceOpen(
    1, libcaer.CAER_DEVICE_DVS128, 0, 0, "")

info = libcaer.caerDVS128InfoGet(handle)

print (type(info))
print (dir(info))
print (info.deviceID)

#  print("device ID: "+str(libcaer.caer_dvs128_info_deviceID_get(info)))

#  if(libcaer.caer_dvs128_info_deviceIsMaster_get(info)):
#      print("device is Master: ")
#  else:
#      print("device is Slave")
#
#  print("device Serial Number"+str(libcaer.caer_dvs128_info_deviceSerialNumber_get(info)))
#
#  print(libcaer.caer_dvs128_info_deviceString_get(info))
