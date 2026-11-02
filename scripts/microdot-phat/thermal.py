#!/usr/bin/env python
# Source: https://github.com/pimoroni/microdot-phat/blob/master/examples/thermal.py
# Original: Pimoroni Ltd, MIT License. See LICENSES/pimoroni-microdot-phat.txt

import datetime
import time

from microdotphat import write_string, set_decimal, clear, show


print("""Thermal

Displays the temperature measured from thermal zone 0, using
/sys/class/thermal/thermal_zone0/temp

Press Ctrl+C to exit.
""")

delay = 1

while True:
    clear()
    path="/sys/class/thermal/thermal_zone0/temp"
    f = open(path, "r")
    temp_raw = int(f.read().strip())
    temp = float(temp_raw / 1000.0)
    write_string( "%.2f" % temp + "c", kerning=False)
    show()
    time.sleep(delay)
