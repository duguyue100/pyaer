/* pyflags.i - Python libcaer interface file
* Authors:
	Federico Corradi - federico.corradi@inilabs.com
	Luca Longinotti - luca.longinotti@inilabs.com
    Yuuang Hu - duguyue100@gmail.com
*/
%module libcaer_wrap
%{
#define SWIG_FILE_WITH_INIT
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
#include <libcaer/devices/device_discover.h>
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
%include <libcaer/devices/device_discover.h>
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

%include "numpy.i"

%init %{
    import_array();
%}

%rename(caerDeviceClose) caerDeviceCloseW;
%rename(caerDeviceConfigGet) caerDeviceConfigGetW;
%rename(caerDeviceConfigGet64) caerDeviceConfigGet64W;

%inline %{
bool caerDeviceCloseW(caerDeviceHandle handle) {
    return (caerDeviceClose(&handle));
}
%}

%inline %{
uint32_t caerDeviceConfigGetW(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr) {
    uint32_t param;
    bool flag = caerDeviceConfigGet(handle, modAddr, paramAddr, &param);
    if (flag == true) {
        return param;
    }
    else {
        return 0;
    }
}
%}

%inline %{
uint64_t caerDeviceConfigGet64W(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr) {
    uint64_t param;
    bool flag = caerDeviceConfigGet64(handle, modAddr, paramAddr, &param);
    if (flag == true) {
        return param;
    }
    else {
        return 0;
    }
}
%}

%inline %{
uint16_t cf_n_type_set(uint8_t coarse_value, uint8_t fine_value) {
    struct caer_bias_coarsefine coarseFineBias;

    coarseFineBias.coarseValue = coarse_value;
    coarseFineBias.fineValue = fine_value;
    coarseFineBias.enabled = true;
    coarseFineBias.sexN = true;
    coarseFineBias.typeNormal = true;
    coarseFineBias.currentLevelNormal = true;

    return caerBiasCoarseFineGenerate(coarseFineBias);
}
%}

%inline %{
uint16_t cf_p_type_set(uint8_t coarse_value, uint8_t fine_value) {
    struct caer_bias_coarsefine coarseFineBias;

    coarseFineBias.coarseValue = coarse_value;
    coarseFineBias.fineValue = fine_value;
    coarseFineBias.enabled = true;
    coarseFineBias.sexN = false;
    coarseFineBias.typeNormal = true;
    coarseFineBias.currentLevelNormal = true;

    return caerBiasCoarseFineGenerate(coarseFineBias);
}
%}

%inline %{
uint16_t cf_n_type_cas_set(uint8_t coarse_value, uint8_t fine_value) {
    struct caer_bias_coarsefine coarseFineBias;

    coarseFineBias.coarseValue = coarse_value;
    coarseFineBias.fineValue = fine_value;
    coarseFineBias.enabled = true;
    coarseFineBias.sexN = true;
    coarseFineBias.typeNormal = false;
    coarseFineBias.currentLevelNormal = true;

    return caerBiasCoarseFineGenerate(coarseFineBias);
}
%}

%inline %{
uint16_t cf_n_type_off_set(uint8_t coarse_value, uint8_t fine_value) {
    struct caer_bias_coarsefine coarseFineBias;

    coarseFineBias.coarseValue = coarse_value;
    coarseFineBias.fineValue = fine_value;
    coarseFineBias.enabled = false;
    coarseFineBias.sexN = true;
    coarseFineBias.typeNormal = true;
    coarseFineBias.currentLevelNormal = true;

    return caerBiasCoarseFineGenerate(coarseFineBias);
}
%}

%inline %{
uint16_t cf_p_type_off_set(uint8_t coarse_value, uint8_t fine_value) {
    struct caer_bias_coarsefine coarseFineBias;

    coarseFineBias.coarseValue = coarse_value;
    coarseFineBias.fineValue = fine_value;
    coarseFineBias.enabled = false;
    coarseFineBias.sexN = false;
    coarseFineBias.typeNormal = true;
    coarseFineBias.currentLevelNormal = true;

    return caerBiasCoarseFineGenerate(coarseFineBias);
}
%}

%inline %{
uint16_t shiftsource_set(uint8_t ref, uint8_t reg, enum caer_bias_shiftedsource_operating_mode opmode) {
    struct caer_bias_shiftedsource caerBiasShiftSource;

    caerBiasShiftSource.refValue = ref;
    caerBiasShiftSource.regValue = reg;
    caerBiasShiftSource.operatingMode = opmode;
    caerBiasShiftSource.voltageLevel = SPLIT_GATE;

    return caerBiasShiftedSourceGenerate(caerBiasShiftSource);
}
%}

%inline %{
uint16_t vdac_set(uint8_t volt, uint8_t curr) {
    struct caer_bias_vdac caerBiasVDAC;

    caerBiasVDAC.voltageValue = volt;
    caerBiasVDAC.currentValue = curr;

    return caerBiasVDACGenerate(caerBiasVDAC);
}
%}

%inline %{
uint32_t set_dynapse_bias(uint8_t biasAddress, uint8_t coarseValue, uint8_t fineValue,
bool biasHigh, bool typeNormal, bool sexN, bool enabled) {
    struct caer_bias_dynapse biasValue;

    biasValue.biasAddress = biasAddress;
    biasValue.coarseValue = coarseValue;
    biasValue.fineValue = fineValue;
    biasValue.enabled = enabled;
    biasValue.sexN = sexN;
    biasValue.typeNormal = typeNormal;
    biasValue.biasHigh = biasHigh;

    return caerBiasDynapseGenerate(biasValue);
}
%}

/*
Numpy related
*/
%apply (int64_t* ARGOUT_ARRAY1, int32_t DIM1) {(int64_t* event_vec, int32_t packet_len)}
%apply (float* ARGOUT_ARRAY1, int32_t DIM1) {(float* event_vec_f, int32_t packet_len)}
%apply (uint8_t* ARGOUT_ARRAY1, int32_t DIM1) {(uint8_t* frame_event_vec, int32_t packet_len)}

%inline %{
void get_polarity_event(caerPolarityEventPacket event_packet, int64_t* event_vec, int32_t packet_len) {
    long i;
    for (i=0; i<(int)packet_len/4; i++) {
        caerPolarityEvent event = caerPolarityEventPacketGetEvent(event_packet, i);
        event_vec[i*4] = caerPolarityEventGetTimestamp(event);
        event_vec[i*4+1] = caerPolarityEventGetX(event);
        event_vec[i*4+2] = caerPolarityEventGetY(event);
        event_vec[i*4+3] = caerPolarityEventGetPolarity(event);
    }
}
%}

%inline %{
void get_special_event(caerSpecialEventPacket event_packet, int64_t* event_vec, int32_t packet_len) {
    long i;
    for (i=0; i<(int)packet_len/2; i++) {
        caerSpecialEvent event = caerSpecialEventPacketGetEvent(event_packet, i);
        event_vec[i*2] = caerSpecialEventGetTimestamp(event);
        event_vec[i*2+1] = caerSpecialEventGetData(event);
    }
}
%}

%inline %{
void get_imu6_event(caerIMU6EventPacket event_packet, float* event_vec_f, int32_t packet_len) {
    long i;
    for (i=0; i<(int)packet_len/8; i++) {
        caerIMU6Event event = caerIMU6EventPacketGetEvent(event_packet, i);
        event_vec_f[i*8] = caerIMU6EventGetTimestamp(event);
        event_vec_f[i*8+1] = caerIMU6EventGetAccelX(event);
        event_vec_f[i*8+2] = caerIMU6EventGetAccelY(event);
        event_vec_f[i*8+3] = caerIMU6EventGetAccelZ(event);
        event_vec_f[i*8+4] = caerIMU6EventGetGyroX(event);
        event_vec_f[i*8+5] = caerIMU6EventGetGyroY(event);
        event_vec_f[i*8+6] = caerIMU6EventGetGyroZ(event);
        event_vec_f[i*8+7] = caerIMU6EventGetTemp(event);
    }
}
%}

%inline %{
void get_spike_event(caerSpikeEventPacket event_packet, int64_t* event_vec, int32_t packet_len) {
    long i;
    for (i=0; i<(int)packet_len/4; i++) {
        caerSpikeEvent event = caerSpikeEventPacketGetEvent(event_packet, i);
        event_vec[i*4] = caerSpikeEventGetTimestamp(event);
        event_vec[i*4+1] = caerSpikeEventGetNeuronID(event);
        event_vec[i*4+2] = caerSpikeEventGetSourceCoreID(event);
        event_vec[i*4+3] = caerSpikeEventGetChipID(event);
    }
}
%}

%inline %{
void get_frame_event(caerFrameEventConst event, uint8_t* frame_event_vec, int32_t packet_len) {
    long i;
    for (i=0; i<(int)packet_len; i++) {
        frame_event_vec[i] = (uint8_t)(le16toh(event->pixels[i]) >> 8);
    }
}
%}
