#!/bin/bash
touch /tmp/65-inilabs.rules
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="152a", ATTR{idProduct}=="84[0-1]?", MODE="0666"
' >> /tmp/65-inilabs.rules
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6014", MODE="0666"' >> /tmp/65-inilabs.rules

# copied from https://github.com/uzh-rpg/rpg_dvs_ros
echo "Copying udev rule (needs root privileges)."
sudo cp /tmp/65-inilabs.rules /etc/udev/rules.d/

echo "Reloading udev rules."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "Done!"
