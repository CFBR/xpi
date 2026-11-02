# unicorn_message.py — unicornhat scrolling text with live update.
#
# Text comes from state.json "message" (live), falling back to sys.argv[1],
# then "hi"; color from state.json "color" (live), names or "#RRGGBB",
# default white. Uses the shared 3x5 renderer in _display.py and polls
# xpi_state.revision() each scroll frame, so an /action=update revises
# text/color without restarting.

import sys
import time

import unicornhat
import xpi_state
import _display

DEFAULT_COLOR = (255, 255, 255)
BRIGHTNESS = 0.5


def get_message():
    text = xpi_state.value("message")
    if text is None and len(sys.argv) > 1:
        text = sys.argv[1]
    return str(text if text is not None else "hi").upper()


unicornhat.set_layout(unicornhat.AUTO)
shape = unicornhat.get_shape()
unicornhat.rotation(0)
unicornhat.brightness(BRIGHTNESS)

text = get_message()
color = _display.parse_color(xpi_state.value("color"), DEFAULT_COLOR)
grid = _display.text_bitmap(text)
offset = 0
last_revision = xpi_state.revision()
print("unicorn_message.py: displaying", text, "color", color, "shape", shape)

while True:
    if xpi_state.revision() != last_revision:
        last_revision = xpi_state.revision()
        new_color = _display.parse_color(xpi_state.value("color"), DEFAULT_COLOR)
        if new_color != color:
            color = new_color
            print("unicorn_message.py: color switched to", color)
        new_text = get_message()
        if new_text != text:
            text = new_text
            grid = _display.text_bitmap(text)
            offset = 0
            print("unicorn_message.py: switched to", text)
    _display.draw_unicorn(grid, offset, shape, color)
    offset += 1
    time.sleep(0.05)
