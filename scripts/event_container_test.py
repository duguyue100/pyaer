"""Testing Event Container.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""

from __future__ import print_function

from timer import Timer

from pyaer.davis import DAVIS


device = DAVIS(noise_filter=True)

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
print("Background Activity Filter:", device.dvs_has_background_activity_filter)
print("Color Filter", device.aps_color_filter, type(device.aps_color_filter))
print(device.aps_color_filter == 1)

device.start_data_stream()
# setting bias after data stream started
device.set_bias_from_json("./scripts/configs/davis346_config.json")

clip_value = 3
histrange = [(0, v) for v in (260, 346)]


def get_event(device):
    data = device.get_event()

    return data


num_packet_before_disable = 1000

while True:
    try:
        with Timer("container_test", show_hist=True):
            event_container = device.get_event_container()

        if event_container is not None:
            print(
                "Duration (s): {}, Num Events: {}, Event Rate (ev/s): {}".format(
                    event_container.pol_event_duration,
                    event_container.num_pol_events,
                    event_container.pol_event_rate,
                )
            )
            print(
                "Signal Rate (ev/s): {}, Noise Rate (ev/s): {}".format(
                    event_container.valid_pol_events_rate,
                    event_container.invalid_pol_events_rate,
                )
            )

            #  print("Number of events:", num_pol_event, "Number of Frames:",
            #        frames.shape, "Exposure:",
            #        device.get_config(
            #            libcaer.DAVIS_CONFIG_APS,
            #            libcaer.DAVIS_CONFIG_APS_EXPOSURE),
            #        "Autoexposure:", device.get_config(
            #            libcaer.DAVIS_CONFIG_APS,
            #            libcaer.DAVIS_CONFIG_APS_AUTOEXPOSURE))
        else:
            pass

    except KeyboardInterrupt:
        device.shutdown()
        break
