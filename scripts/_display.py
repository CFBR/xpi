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

# 3x4 glyphs for the 8x4 Unicorn pHAT. A 5-row glyph does not fit there;
# clipping the bottom row made text hard to read.
FONT_COMPACT = {
    "A": ["010", "101", "111", "101"], "B": ["110", "101", "110", "101"],
    "C": ["011", "100", "100", "011"], "D": ["110", "101", "101", "110"],
    "E": ["111", "100", "110", "100"], "F": ["111", "100", "100", "100"],
    "G": ["011", "100", "101", "011"], "H": ["101", "101", "111", "101"],
    "I": ["111", "010", "010", "111"], "J": ["001", "001", "101", "010"],
    "K": ["101", "110", "101", "101"], "L": ["100", "100", "100", "111"],
    "M": ["101", "111", "111", "101"], "N": ["101", "111", "111", "101"],
    "O": ["010", "101", "101", "010"], "P": ["110", "101", "110", "100"],
    "Q": ["010", "101", "101", "011"], "R": ["110", "101", "110", "101"],
    "S": ["011", "100", "010", "110"], "T": ["111", "010", "010", "010"],
    "U": ["101", "101", "101", "011"], "V": ["101", "101", "101", "010"],
    "W": ["101", "101", "111", "101"], "X": ["101", "101", "010", "101"],
    "Y": ["101", "101", "010", "010"], "Z": ["111", "001", "010", "111"],
    "0": ["111", "101", "101", "111"], "1": ["010", "110", "010", "111"],
    "2": ["110", "001", "010", "111"], "3": ["110", "001", "110", "001"],
    "4": ["101", "101", "111", "001"], "5": ["111", "100", "110", "011"],
    "6": ["011", "100", "110", "101"], "7": ["111", "001", "010", "010"],
    "8": ["010", "101", "010", "101"], "9": ["110", "101", "011", "110"],
    ".": ["000", "000", "000", "010"], "-": ["000", "000", "111", "000"],
    ":": ["000", "010", "000", "010"], "_": ["000", "000", "000", "111"],
    " ": ["000", "000", "000", "000"], "!": ["010", "010", "010", "000"],
    "?": ["110", "001", "010", "000"], "/": ["001", "001", "010", "100"],
    "+": ["000", "010", "111", "010"], "%": ["101", "001", "010", "101"],
}
FAILSAFE_COMPACT = ["111", "101", "101", "111"]
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


class TextGrid(list):
    """Bitmap rows plus the text they came from.

    Keeping the text lets a 4-row display re-render the glyphs with the
    compact font instead of clipping the bottom row of the 5-row font.
    """

    def __init__(self, rows, text):
        super().__init__(rows)
        self.text = str(text)


def text_bitmap(text, rows=5):
    """Render `text` to rows of 0/1 columns.

    `rows` 4 uses the compact 3x4 font for the Unicorn pHAT. Five or more
    uses the taller 3x5 font.
    """
    text = str(text)
    compact = rows <= 4
    height = 4 if compact else 5
    font = FONT_COMPACT if compact else FONT
    fallback = FAILSAFE_COMPACT if compact else FAILSAFE
    cols = len(text) * CHAR_W
    grid = [[0] * cols for _ in range(height)]
    for i, ch in enumerate(text):
        glyph = font.get(ch, fallback)
        for gy in range(height):
            for gx in range(3):
                grid[gy][i * CHAR_W + gx] = int(glyph[gy][gx])
    return TextGrid(grid, text)


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


def format_count(value):
    """Short count for a small display: 1234, 1.2M, 12B."""
    try:
        value = max(0, int(value))
    except (TypeError, ValueError):
        return "0"
    if value < 1000000:
        return str(value)
    if value < 100000000:
        return ("%.1fM" % (value / 1000000.0)).replace(".0M", "M")
    if value < 1000000000:
        return "%dM" % round(value / 1000000.0)
    if value < 100000000000:
        return ("%.1fB" % (value / 1000000000.0)).replace(".0B", "B")
    if value < 1000000000000:
        return "%dB" % round(value / 1000000000.0)
    return ("%.1fT" % (value / 1000000000000.0)).replace(".0T", "T")


def setup_unicorn(layout=None):
    """Initialize unicornhat, honoring the *real* board layout.

    The vendored setup() now asks for AUTO. Trigger it once so the map is
    resolved, then apply an explicit layout if one was requested.
    """
    import unicornhat
    unicornhat.get_shape()                     # runs setup() once
    unicornhat.set_layout(layout or unicornhat.AUTO)
    unicornhat.rotation(0)
    unicornhat.brightness(1.0)
    return unicornhat.get_shape(), unicornhat


def scroll_delay(shape):
    """Seconds per text column, slower on the short 8-column boards."""
    width = shape[0] if shape else 0
    if width <= 8:
        return 0.14
    if width <= 16:
        return 0.09
    return 0.05


def _grid_for_height(grid, height):
    if height < 5 and getattr(grid, "text", None) is not None:
        return text_bitmap(grid.text, rows=height)
    return grid


def draw_unicorn(grid, offset, shape, color):
    """Scroll `grid` across a unicorn display; one show() per call."""
    w, h = shape
    import unicornhat
    grid = _grid_for_height(grid, h)
    rows = min(len(grid), h)
    y0 = max(0, (h - rows) // 2)
    r, g, b = color
    unicornhat.clear()
    for x in range(w):
        src = (x + offset) % len(grid[0])
        for y in range(rows):
            if grid[y][src]:
                unicornhat.set_pixel(x, y0 + y, r, g, b)
    unicornhat.show()


def draw_unicorn_fit(grid, offset, shape, color):
    """Center short text; scroll it when it is wider than the board.

    Returns the next scroll offset.
    """
    if len(grid[0]) <= shape[0]:
        draw_unicorn_centered(grid, shape, color)
        return offset
    draw_unicorn(grid, offset, shape, color)
    return offset + 1


def draw_unicorn_centered(grid, shape, color):
    """Draw a short grid centered; one show() per call."""
    w, h = shape
    import unicornhat
    grid = _grid_for_height(grid, h)
    rows = min(len(grid), h)
    x0 = max(0, (w - len(grid[0])) // 2)
    y0 = max(0, (h - rows) // 2)
    r, g, b = color
    unicornhat.clear()
    for y in range(rows):
        for x in range(min(len(grid[0]), w - x0)):
            if grid[y][x]:
                unicornhat.set_pixel(x0 + x, y0 + y, r, g, b)
    unicornhat.show()
