#!/bin/bash

WIFI_SSID='Name (SSID) of your WiFi network.'
WIFI_PASSWORD='Password to the WiFi network.'
WIFI_COUNTRY='US, SE, GB...'

# Enable SSH access
touch /boot/ssh

# Enable WiFi access
echo "country=${WIFI_COUNTRY}
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
      ssid=\"${WIFI_SSID}\"
      psk=\"${WIFI_PASSWORD}\"
}" > /boot/wpa_supplicant.conf

echo ""
echo ""
echo "You need to restart for these changes to take effect"
echo ""
echo ""
