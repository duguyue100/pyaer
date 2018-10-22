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
#include <libcaer/filters/dvs_noise.h>
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
%include <libcaer/filters/dvs_noise.h>

%include "numpy.i"

%init %{
    import_array();
%}

%rename(caerDeviceClose) caerDeviceCloseW;
%rename(caerDeviceConfigGet) caerDeviceConfigGetW;
%rename(caerDeviceConfigGet64) caerDeviceConfigGet64W;
%rename(caerFilterDVSNoiseConfigGet) caerFilterDVSNoiseConfigGetW;

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
uint64_t caerFilterDVSNoiseConfigGetW(caerFilterDVSNoise noiseFilter, uint8_t paramAddr) {
    uint64_t param;
    bool flag = caerFilterDVSNoiseConfigGet(noiseFilter, paramAddr, &param);
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
%apply (uint16_t* ARGOUT_ARRAY1, int32_t DIM1) {(uint16_t* hotpixel_vec, int32_t hotpixel_len)}
%apply (uint64_t* ARGOUT_ARRAY1, int32_t DIM1) {(uint64_t* devices_vec, int32_t device_len)}
%apply (float* ARGOUT_ARRAY1, int32_t DIM1) {(float* event_vec_f, int32_t packet_len)}
%apply (uint8_t* ARGOUT_ARRAY1, int32_t DIM1) {(uint8_t* frame_event_vec, int32_t packet_len)}

/* frame event */
%apply (uint8_t ARGOUT_ARRAY2[ANY][ANY]) {(uint8_t frame_event_240[180][240])};
%apply (uint8_t ARGOUT_ARRAY2[ANY][ANY]) {(uint8_t frame_event_346[260][346])};
%apply (int64_t ARGOUT_ARRAY3[ANY][ANY][ANY]) {(int64_t pol_hist_240[180][240][2])};
%apply (int64_t ARGOUT_ARRAY3[ANY][ANY][ANY]) {(int64_t pol_hist_346[260][346][2])};
%apply (int64_t ARGOUT_ARRAY3[ANY][ANY][ANY]) {(int64_t pol_hist_128[128][128][2])};

%inline %{
void device_discover(int16_t deviceType, uint64_t* devices_vec, int32_t device_len) {
    caerDeviceDiscoveryResult discoveredDevices;
    ssize_t result = caerDeviceDiscover(deviceType, &discoveredDevices);

    size_t i=0;
    for (i=0; i< (size_t) result; i++){
        devices_vec[i*3] = (uint64_t)discoveredDevices[i].deviceType;
        switch (discoveredDevices[i].deviceType){
            case CAER_DEVICE_DVS128: {
                struct caer_dvs128_info *info = &discoveredDevices[i].deviceInfo.dvs128Info;
                devices_vec[i*3+1] = (uint64_t)info->deviceUSBBusNumber;
                devices_vec[i*3+2] = (uint64_t)info->deviceUSBDeviceAddress;
            break;
            }

            case CAER_DEVICE_DAVIS_FX2:
            case CAER_DEVICE_DAVIS_FX3:
            case CAER_DEVICE_DAVIS: {
                struct caer_davis_info *info = &discoveredDevices[i].deviceInfo.davisInfo;
                devices_vec[i*3+1] = (uint64_t)info->deviceUSBBusNumber;
                devices_vec[i*3+2] = (uint64_t)info->deviceUSBDeviceAddress;
                break;
            }

            case CAER_DEVICE_DYNAPSE: {
                struct caer_dynapse_info *info = &discoveredDevices[i].deviceInfo.dynapseInfo;
                devices_vec[i*3+1] = (uint64_t)info->deviceUSBBusNumber;
                devices_vec[i*3+2] = (uint64_t)info->deviceUSBDeviceAddress;
                break;
            }

            case CAER_DEVICE_EDVS: {
                struct caer_edvs_info *info = &discoveredDevices[i].deviceInfo.edvsInfo;
                devices_vec[i*3+1] = 0;
                devices_vec[i*3+2] = (uint64_t)info->serialBaudRate;
                break;
            }

            case CAER_DEVICE_DAVIS_RPI: {
                devices_vec[i*3+1] = 0;
                devices_vec[i*3+2] = 0;
                break;
            }

            default:
                break;
        }
    }
    devices_vec[(size_t)result*3]=42;

    free(discoveredDevices);
}
%}

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
void get_polarity_event_histogram_128(caerPolarityEventPacket event_packet, int32_t packet_len, int64_t pol_hist_128[128][128][2]) {
    memset(pol_hist_128, 0, sizeof(pol_hist_128[0][0][0])*128*128*2);
    long i;
    for (i=0; i<(long)packet_len; i++) {
        caerPolarityEvent event = caerPolarityEventPacketGetEvent(event_packet, i);

        pol_hist_128[(int)caerPolarityEventGetY(event)][(int)caerPolarityEventGetX(event)][(bool)caerPolarityEventGetPolarity(event)] += 1;
    }
}
%}

%inline %{
void get_polarity_event_histogram_240(caerPolarityEventPacket event_packet, int32_t packet_len, int64_t pol_hist_240[180][240][2]) {
    memset(pol_hist_240, 0, sizeof(pol_hist_240[0][0][0])*180*240*2);
    long i;
    for (i=0; i<(long)packet_len; i++) {
        caerPolarityEvent event = caerPolarityEventPacketGetEvent(event_packet, i);

        pol_hist_240[(int)caerPolarityEventGetY(event)][(int)caerPolarityEventGetX(event)][(bool)caerPolarityEventGetPolarity(event)] += 1;
    }
}
%}

%inline %{
void get_counter_neuron_frame_240(caerPolarityEventPacket event_packet, int32_t packet_len, int64_t pol_hist_240[180][240][2]) {
    int64_t counter_neuron[180][240];
    int64_t neuron_prev, pol;
    int y, x;
    memset(counter_neuron, 0, sizeof(counter_neuron[0][0])*180*240);
    memset(pol_hist_240, 0, sizeof(pol_hist_240[0][0][0])*180*240*2);

    long i;
    for (i=0; i<(long)packet_len; i++) {
        caerPolarityEvent event = caerPolarityEventPacketGetEvent(event_packet, i);

        y = (int)caerPolarityEventGetY(event);
        x = (int)caerPolarityEventGetX(event);
        pol = ((int64_t)caerPolarityEventGetPolarity(event))*2-1;

        neuron_prev = counter_neuron[y][x];
        counter_neuron[y][x] += pol;
        
        if (neuron_prev<=1 && counter_neuron[y][x]>1)
            pol_hist_240[y][x][1] += 1;
        if (neuron_prev>1 && counter_neuron[y][x]<=1)
            pol_hist_240[y][x][0] += 1;

        /* if (counter_neuron[y][x] > 4) */
        /*     counter_neuron[y][x] = 4; */
        /* if (counter_neuron[y][x] < 0) */
        /*     counter_neuron[y][x] = 0; */
    }
}
%}

%inline %{
void get_polarity_event_histogram_346(caerPolarityEventPacket event_packet, int32_t packet_len, int64_t pol_hist_346[260][346][2]) {
    memset(pol_hist_346, 0, sizeof(pol_hist_346[0][0][0])*260*346*2);
    long i;
    for (i=0; i<(long)packet_len; i++) {
        caerPolarityEvent event = caerPolarityEventPacketGetEvent(event_packet, i);

        pol_hist_346[(int)caerPolarityEventGetY(event)][(int)caerPolarityEventGetX(event)][(bool)caerPolarityEventGetPolarity(event)] += 1;
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
void get_imu9_event(caerIMU9EventPacket event_packet, float* event_vec_f, int32_t packet_len) {
    long i;
    for (i=0; i<(int)packet_len/11; i++) {
        caerIMU9Event event = caerIMU9EventPacketGetEvent(event_packet, i);
        event_vec_f[i*11] = caerIMU9EventGetTimestamp(event);
        event_vec_f[i*11+1] = caerIMU9EventGetAccelX(event);
        event_vec_f[i*11+2] = caerIMU9EventGetAccelY(event);
        event_vec_f[i*11+3] = caerIMU9EventGetAccelZ(event);
        event_vec_f[i*11+4] = caerIMU9EventGetGyroX(event);
        event_vec_f[i*11+5] = caerIMU9EventGetGyroY(event);
        event_vec_f[i*11+6] = caerIMU9EventGetGyroZ(event);
        event_vec_f[i*11+7] = caerIMU9EventGetCompX(event);
        event_vec_f[i*11+8] = caerIMU9EventGetCompY(event);
        event_vec_f[i*11+9] = caerIMU9EventGetCompZ(event);
        event_vec_f[i*11+10] = caerIMU9EventGetTemp(event);
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

%inline %{
void get_frame_event_240(caerFrameEventConst event, uint8_t frame_event_240[180][240]) {
    long i, j;
    for (i=0; i<180; i++) {
        for (j=0; j<240; j++){
            frame_event_240[i][j] = (uint8_t)(le16toh(event->pixels[i*240+j]) >> 8);
        }
    }
}
%}

%inline %{
void get_frame_event_346(caerFrameEventConst event, uint8_t frame_event_346[260][346]) {
    long i, j;
    for (i=0; i<260; i++) {
        for (j=0; j<346; j++){
            frame_event_346[i][j] = (uint8_t)(le16toh(event->pixels[i*346+j]) >> 8);
        }
    }
}
%}


/*
Filters related
*/

%inline %{
caerPolarityEventPacket apply_dvs_noise_filter(caerFilterDVSNoise noiseFilter, caerPolarityEventPacket polarity) {
    caerFilterDVSNoiseApply(noiseFilter, polarity);
    return polarity;
}
%}

%inline %{
void get_filtered_polarity_event(caerPolarityEventPacket event_packet, int64_t* event_vec, int32_t packet_len) {
    long i;
    for (i=0; i<(int)packet_len/5; i++) {
        caerPolarityEvent event = caerPolarityEventPacketGetEvent(event_packet, i);
        event_vec[i*5] = caerPolarityEventGetTimestamp(event);
        event_vec[i*5+1] = caerPolarityEventGetX(event);
        event_vec[i*5+2] = caerPolarityEventGetY(event);
        event_vec[i*5+3] = caerPolarityEventGetPolarity(event);
        event_vec[i*5+4] = (int64_t)(caerPolarityEventIsValid(event));
    }
}
%}

%inline %{
void get_hot_pixels(caerFilterDVSNoise noiseFilter, uint16_t* hotpix_vec, int32_t hotpix_len) {
    caerFilterDVSPixel hotPixels;
    ssize_t numHotPixels = caerFilterDVSNoiseGetHotPixels(noiseFilter, &hotPixels);

    long i;
    for (i=0; i<(int)hotpix_len/2; i++) {
        hotpix_vec[i*2] = hotPixels[i].x;
        hotpix_vec[i*2+1] = hotPixels[i].y;
    }

    free(hotPixels);
}
%}

%inline %{
int64_t get_num_hot_pixels(caerFilterDVSNoise noiseFilter) {
    caerFilterDVSPixel hotPixels;
    ssize_t numHotPixels = caerFilterDVSNoiseGetHotPixels(noiseFilter, &hotPixels);

    free(hotPixels);

    return (int64_t)(numHotPixels);
}
%}
