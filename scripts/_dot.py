# _dot.py: visible-area helpers for the Micro Dot pHAT.
#
# The library buffer is 45 columns wide: six 5x7 matrices with three hidden
# columns between each pair. Scripts draw on the 30 visible columns and map
# each one to its buffer column.

MATRIX = 5
STRIDE = 8


def visible_width(width):
    """Number of columns the board actually shows."""
    return ((width + STRIDE - MATRIX) // STRIDE) * MATRIX


def buffer_x(x):
    """Map a visible column to the library buffer, skipping hidden columns."""
    return (x // MATRIX) * STRIDE + x % MATRIX


def big_text(text, y=0):
    """Draw 5x7 text one glyph per 5-column matrix, centred."""
    import microdotphat
    from microdotphat.font import font

    text = str(text).upper()[:6]
    start = (6 - len(text)) // 2
    for i, char in enumerate(text):
        glyph = font.get(ord(char))
        if glyph is None:
            continue
        x0 = (start + i) * MATRIX
        for gx, column in enumerate(glyph):
            for gy in range(7):
                if column & (1 << gy):
                    microdotphat.set_pixel(buffer_x(x0 + gx), y + gy, 1)
