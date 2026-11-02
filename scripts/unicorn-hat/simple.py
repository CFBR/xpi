#!/usr/bin/env python
# Source: https://github.com/CFBR/unicorn-hat/blob/master/examples/simple.py
# Original: Pimoroni Ltd, MIT License. See LICENSES/pimoroni-unicorn-hat.txt

import time

import unicornhat as unicorn


print("""Simple

Turns each pixel on in turn and updates the display.

If you're using a Unicorn HAT and only half the screen lights up, 
edit this example and  change 'unicorn.AUTO' to 'unicorn.HAT' below.
""")

unicorn.set_layout(unicorn.AUTO)
unicorn.rotation(0)
unicorn.brightness(0.5)
width,height=unicorn.get_shape()


for y in range(height):
  for x in range(width):
    unicorn.set_pixel(x,y,255,0,255)
    unicorn.show()
    time.sleep(0.05)

time.sleep(1)
