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
