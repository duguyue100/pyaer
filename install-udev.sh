#!/bin/bash
touch /tmp/65-inivation.rules
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="152a", ATTR{idProduct}=="84[0-1]?", MODE="0666"
' >> /tmp/65-inivation.rules
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6014", MODE="0666"' >> /tmp/65-inivation.rules

echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1134", ATTR{idProduct}=="8001", MODE="0666"' >> /tmp/65-inivation.rules

echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="04b4", ATTR{idProduct}=="8613", MODE="0666"' >> /tmp/65-inivation.rules

echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="04b4", ATTR{idProduct}=="0053", MODE="0666"' >> /tmp/65-inivation.rules

echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="04b4", ATTR{idProduct}=="00f3", MODE="0666"' >> /tmp/65-inivation.rules

echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="04b4", ATTR{idProduct}=="00f1", MODE="0666"' >> /tmp/65-inivation.rules

# copied from https://gitlab.com/inivation/libcaer
echo "Copying udev rule (needs root privileges)."
sudo cp /tmp/65-inivation.rules /etc/udev/rules.d/

echo "Reloading udev rules."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "Done!"
