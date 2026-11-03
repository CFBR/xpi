# _display.py — helpers shared by shipped display scripts.
#
# Contains the tiny 3x5 scrollable-text renderer used by unicorn scripts and
# the color parser. Keeping it here means unicorn_message.py, hostname.py etc.
# don't each carry their own copy of the font.

import re

import _xpi_state

# 3x5 pixel font for uppercase letters, digits and a few punctuation.
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
    ".": ["000"] * 4 + ["010"], "-": ["000", "000", "111", "000", "000"],
    ":": ["000", "010", "000", "010", "000"],
    "_": ["000"] * 4 + ["111"], " ": ["000"] * 5,
}
FAILSAFE = ["111", "101", "101", "101", "111"]
CHAR_W = 4             # 3 px glyph + 1 px gap

COLORS = {
    "red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255),
    "white": (255, 255, 255), "yellow": (255, 255, 0),
    "orange": (255, 128, 0), "purple": (128, 0, 255),
    "magenta": (255, 0, 255), "cyan": (0, 255, 255),
    "pink": (255, 64, 128),
}


def parse_color(value, default=(255, 255, 255)):
    """Accepts '#RRGGBB', 'RRGGBB' or a color name; falls back to default."""
    if value is None:
        return default
    if isinstance(value, (tuple, list)) and len(value) == 3:
        return tuple(max(0, min(255, int(v))) for v in value)
    text = str(value).strip().lower().lstrip("#")
    if text in COLORS:
        return COLORS[text]
    if re.fullmatch("[0-9a-f]{3}", text):
        text = "".join(c + c for c in text)
    if re.fullmatch("[0-9a-f]{6}", text):
        return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))
    return default


def text_bitmap(text):
    """Render `text` to a list of 5 rows, each a list of 0/1 columns."""
    cols = len(text) * CHAR_W
    grid = [[0] * cols for _ in range(5)]
    for i, ch in enumerate(text):
        glyph = FONT.get(ch, FAILSAFE)
        for gy in range(5):
            for gx in range(3):
                grid[gy][i * CHAR_W + gx] = int(glyph[gy][gx])
    return grid


def brightness_value(default=0.5):
    """Brightness from state.json "brightness", clamped to 0.0-1.0.

    The microdot-phat has no brightness control; only unicornhat scripts use
    this.
    """
    raw = _xpi_state.value("brightness")
    if raw is None:
        return default
    try:
        return max(0.0, min(1.0, float(raw)))
    except (TypeError, ValueError):
        return default


def setup_unicorn(layout=None):
    """Initialize unicornhat, honoring the *real* board layout.

    unicornhat.setup() defaults to the HAT layout and get_shape() triggers
    setup() on first call, which clobbers any earlier set_layout(). So:
    trigger setup() once (reading the shape we throw away), then set the
    layout we actually want, then read the true shape.
    """
    import unicornhat
    unicornhat.get_shape()                     # runs setup() once -> HAT
    unicornhat.set_layout(layout or unicornhat.AUTO)
    unicornhat.rotation(0)
    unicornhat.brightness(1.0)
    return unicornhat.get_shape(), unicornhat


def draw_unicorn(grid, offset, shape, color):
    """Scroll `grid` across a unicorn display; one show() per call."""
    w, h = shape
    import unicornhat
    r, g, b = color
    unicornhat.clear()
    y0 = max(0, (h - 5) // 2)
    for x in range(w):
        src = (x + offset) % len(grid[0])
        for y in range(5):
            if grid[y][src] and y0 + y < h:
                unicornhat.set_pixel(x, y0 + y, r, g, b)
    unicornhat.show()
