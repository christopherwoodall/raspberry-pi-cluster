#!/usr/bin/env python3

"""blink.py: Turn off and on the onboard RaspberryPi LEDS."""

__author__      = "Christopher Woodall"
__copyright__   = "None"

import sys, os, time

statusGPIO = '/sys/class/leds/led0'

os.system( f"echo gpio | sudo tee {statusGPIO}/trigger > /dev/null 2>&1" )

for j in range(10):
  # led on
  os.system( f"echo 1 | sudo dd status=none of={statusGPIO}/brightness" )
  time.sleep(1)
  # led off
  os.system( f"echo 0 | sudo dd status=none of={statusGPIO}/brightness" )
  time.sleep(1)
