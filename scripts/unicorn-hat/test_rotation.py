#!/usr/bin/env python
# Source: https://github.com/pimoroni/unicorn-hat/blob/master/examples/test_rotation.py
# Original: Pimoroni Ltd, MIT License. See LICENSES/pimoroni-unicorn-hat.txt

import unicornhat as unicorn
import time
from random import randint

unicorn.set_layout(unicorn.AUTO)
unicorn.rotation(0)
unicorn.brightness(0.4)
uh_width,uh_height=unicorn.get_shape()


for rot in [0, 90, 180, 270]:
  print(rot)
  unicorn.rotation(rot)
  unicorn.set_pixel(0,0,255,255,255)
  print(unicorn.get_rotation())
  unicorn.show()
  time.sleep(1)
