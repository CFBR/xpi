# unicorn_message.py — unicornhat scrolling text with live update.
#
# Text comes from state.json "message" (live), falling back to sys.argv[1],
# then "hi". Uses a tiny built-in 3x5 bitmap font (printable ASCII subset),
# so no pyfiglet/figlet dependency. Polls xpi_state.revision() each scroll
# frame so an /action=update&message=... call changes text without a restart.

import sys
import time

import unicornhat
import xpi_state

BRIGHTNESS = 0.5
CHAR_W = 4          # 3 px glyph + 1 px gap
BLANK = ["000"] * 5
FAILSAFE = ["111", "101", "101", "101", "111"]

FONT = {
    "A": ["010", "101", "111", "101", "101"], "B": ["110", "101", "110", "101", "110"],
    "C": ["011", "100", "100", "100", "011"], "D": ["110", "101", "101", "101", "110"],
    "E": ["111", "100", "110", "100", "111"], "F": ["111", "100", "110", "100", "100"],
    "G": ["011", "100", "101", "101", "011"], "H": ["101", "101", "111", "101", "101"],
    "I": ["111", "010", "010", "010", "111"], "J": ["001", "001", "001", "101", "010"],
    "K": ["101", "110", "101", "101", "101"], "L": ["100", "100", "100", "100", "111"],
    "M": ["101", "111", "111", "101", "101"], "N": ["101", "111", "111", "111", "101"],
    "O": ["010", "101", "101", "101", "010"], "P": ["110", "101", "110", "100", "100"],
    "Q": ["010", "101", "101", "011", "001"], "R": ["110", "101", "110", "101", "101"],
    "S": ["011", "100", "010", "001", "110"], "T": ["111", "010", "010", "010", "010"],
    "U": ["101", "101", "101", "101", "011"], "V": ["101", "101", "101", "010", "010"],
    "W": ["101", "101", "111", "111", "101"], "X": ["101", "101", "010", "101", "101"],
    "Y": ["101", "101", "010", "010", "010"], "Z": ["111", "001", "010", "100", "111"],
    "0": ["010", "101", "101", "101", "010"], "1": ["010", "110", "010", "010", "111"],
    "2": ["110", "001", "010", "100", "111"], "3": ["110", "001", "110", "001", "110"],
    "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "110", "001", "110"],
    "6": ["011", "100", "110", "101", "010"], "7": ["111", "001", "010", "010", "010"],
    "8": ["010", "101", "010", "101", "010"], "9": ["010", "101", "011", "001", "110"],
    " ": BLANK, "!": ["010", "010", "010", "000", "010"], "?": ["110", "001", "010", "000", "010"],
    ".": BLANK[:4] + ["010"], ",": BLANK[:3] + ["010", "100"], "'": ["010", "010", "000", "000", "000"],
    "-": ["000", "000", "111", "000", "000"], ":": BLANK[:1] + ["010", "000", "010"],
    "_": BLANK[:4] + ["111"], "/": ["001", "001", "010", "100", "100"],
    "+": BLANK[:1] + ["010", "111", "010"],
}


def get_message():
    text = xpi_state.value("message")
    if text is None and len(sys.argv) > 1:
        text = sys.argv[1]
    return str(text if text is not None else "hi").upper()


def text_bitmap(text):
    cols = len(text) * CHAR_W
    rows = 5
    grid = [[0] * cols for _ in range(rows)]
    for i, ch in enumerate(text):
        glyph = FONT.get(ch, FAILSAFE)
        for gy in range(rows):
            for gx in range(3):
                grid[gy][i * CHAR_W + gx] = int(glyph[gy][gx])
    return grid


def render(grid, offset, shape):
    w, h = shape
    unicornhat.clear()
    y0 = max(0, (h - 5) // 2)
    for x in range(w):
        src = (x + offset) % len(grid[0])
        for y in range(5):
            if grid[y][src] and y0 + y < h:
                unicornhat.set_pixel(x, y0 + y, 255, 255, 255)
    unicornhat.show()


shape = unicornhat.get_shape()
unicornhat.set_layout(unicornhat.AUTO)
unicornhat.rotation(0)
unicornhat.brightness(BRIGHTNESS)

text = get_message()
grid = text_bitmap(text)
offset = 0
last_revision = xpi_state.revision()
print("unicorn_message.py: displaying", text, "shape", shape)

while True:
    new_revision = xpi_state.revision()
    if new_revision != last_revision:
        last_revision = new_revision
        new_text = get_message()
        if new_text != text:
            text = new_text
            grid = text_bitmap(text)
            offset = 0
            print("unicorn_message.py: switched to", text)
    render(grid, offset, shape)
    offset += 1
    time.sleep(0.05)
