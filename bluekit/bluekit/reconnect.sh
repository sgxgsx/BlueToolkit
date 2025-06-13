#!/bin/bash

mac=$1 # DEH-4400BT

#if [ "$1" = "off" ]; then
#    bluetoothctl -- disconnect
#    exit $?
#fi

# turn on bluetooth in case it's off
rfkill unblock bluetooth

bluetoothctl -- power on
bluetoothctl -- discoverable on
bluetoothctl -- pairable on
bluetoothctl -- agent NoInputNoOutput    # if you delete this part it will pair as normal, one would need to accept pairing only on the device (test)
bluetoothctl -- default-agent
bluetoothctl -- remove $mac
sudo hcitool info $mac
bluetoothctl -- trust $mac
bluetoothctl -- connect $mac
bluetoothctl -- remove $mac
bluetoothctl -- disconnect


#exit 0

# Use it as default output for PulseAudio

#sink=$(pactl list short sinks | grep bluez | awk '{print $2}')

#if [ -n "$sink" ]; then
#    pacmd set-default-sink "$sink" && echo "OK default sink : $sink"
#else
#    echo could not find bluetooth sink
#    exit 1
#fi
