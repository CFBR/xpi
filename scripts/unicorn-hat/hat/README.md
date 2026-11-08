Unicorn HAT Examples
====================

Copied from `pimoroni/unicorn-hat` `examples/hat/README.md`, MIT License,
Pimoroni Ltd. Edited for xpi: the `show_png.py` entry is gone, see the note at
the end.

The examples in this folder must be run with `sudo`, like so:

    sudo ./clock.py

or

    sudo python clock.py


The examples in this folder are intended for the Unicorn HAT and have not been designed for the pHAT geometry. Feel free to give it a try and move them up inside the main examples folder if you are successful making them work adequately with both boards.

candle.py
---------

A simple animation simulating a candle flame.

candle_with_timer.py
--------------------

Builds upon candle.py by adding a fade-out effect to make it useful as a soothing sleep light that will reduce in size and brightnes gradually.

clock.py
--------

Uses `graphics.py` and shows how you can, but probably shouldn't, display an analogue clock on Unicorn HAT!

graphics.py
-----------

Used by clock.py

eve.py
------

Monitors the usb bus and displays a checkmark when a new device is detected.

matrix.py
---------

Knock, knock, Neo.

Note on show_png.py
-------------------

Pimoroni's `show_png.py` example and its `lofi.png` sprite are not in this
repo. The sprite art is CC BY-NC-SA 3.0, which cannot ship in an MIT repo.
xpi's own `image` script, at `scripts/image.py`, does the same job with any
PNG, GIF or JPEG you point it at.
