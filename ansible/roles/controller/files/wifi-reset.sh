#!/bin/bash

# Reset Wireless interface

# network interface name
interface="wlan0"

# syslog tag
tag="wifi-resume"

# check for "interface: link is not ready"
(dmesg | tail -10 | grep "${interface}: link is not ready")>/dev/null

if [ "$?" -eq 0 ]; then
    logger -t $tag "$interface is not ready"
    if [ -z "$(iwgetid --raw $interface)" ]; then
        logger -t $tag "$interface is not connected to any network"
        #modprobe -r ath10k_pci
        #modprobe ath10k_pci
    fi
fi
