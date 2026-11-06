#!/usr/bin/env python
# Source: https://github.com/pimoroni/unicorn-hat/blob/master/examples/simple.py
# Original: Pimoroni Ltd, MIT License. See LICENSES/pimoroni-unicorn-hat.txt
# Variant: red pixels, rotation 180, 0.5s steps.

import time

import unicornhat as unicorn


print("""Simple

Turns each pixel on in turn and updates the display.

If you're using a Unicorn HAT and only half the screen lights up, 
edit this example and  change 'unicorn.AUTO' to 'unicorn.HAT' below.
""")

unicorn.set_layout(unicorn.AUTO)
unicorn.rotation(180)
unicorn.brightness(0.5)
width,height=unicorn.get_shape()


for y in range(height):
  for x in range(width):
    unicorn.set_pixel(x,y,90, 0, 0)
    unicorn.show()
    time.sleep(0.5)

time.sleep(1)
