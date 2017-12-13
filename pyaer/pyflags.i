/* pyflags.i - Python libcaer interface file
* Authors:
	Federico Corradi - federico.corradi@inilabs.com
	Luca Longinotti - luca.longinotti@inilabs.com
*/
%module libcaer_wrap
%{
#include <libcaer/libcaer.h>
#include <libcaer/network.h>
#include <libcaer/frame_utils.h>
#include <libcaer/devices/device.h>
#include <libcaer/devices/usb.h>
#include <libcaer/devices/serial.h>
#include <libcaer/devices/dvs128.h>
#include <libcaer/devices/edvs.h>
#include <libcaer/devices/davis.h>
#include <libcaer/devices/dynapse.h>
#include <libcaer/events/common.h>
#include <libcaer/events/config.h>
#include <libcaer/events/ear.h>
#include <libcaer/events/frame.h>
#include <libcaer/events/imu6.h>
#include <libcaer/events/imu9.h>
#include <libcaer/events/packetContainer.h>
#include <libcaer/events/point1d.h>
#include <libcaer/events/point2d.h>
#include <libcaer/events/point3d.h>
#include <libcaer/events/point4d.h>
#include <libcaer/events/polarity.h>
#include <libcaer/events/sample.h>
#include <libcaer/events/special.h>
#include <libcaer/events/spike.h>
%}

%feature("autodoc", "1");

%ignore caerDeviceClose;

%include "stdint.i"
%include <libcaer/libcaer.h>
%include <libcaer/network.h>
%include <libcaer/frame_utils.h>
%include <libcaer/devices/device.h>
%include <libcaer/devices/usb.h>
%include <libcaer/devices/serial.h>
%include <libcaer/devices/dvs128.h>
%include <libcaer/devices/edvs.h>
%include <libcaer/devices/davis.h>
%include <libcaer/devices/dynapse.h>
%include <libcaer/events/common.h>
%include <libcaer/events/config.h>
%include <libcaer/events/ear.h>
%include <libcaer/events/frame.h>
%include <libcaer/events/imu6.h>
%include <libcaer/events/imu9.h>
%include <libcaer/events/packetContainer.h>
%include <libcaer/events/point1d.h>
%include <libcaer/events/point2d.h>
%include <libcaer/events/point3d.h>
%include <libcaer/events/point4d.h>
%include <libcaer/events/polarity.h>
%include <libcaer/events/sample.h>
%include <libcaer/events/special.h>
%include <libcaer/events/spike.h>

%rename(caerDeviceClose) caerDeviceCloseW;

%inline %{
bool caerDeviceCloseW(caerDeviceHandle handle) {
	return (caerDeviceClose(&handle));
}
%}
