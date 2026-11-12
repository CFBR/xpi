# snake.py: snakes crawl over the Micro Dot pHAT in column order.
#
# The default path starts at the top left, runs down the first column, steps
# one column right, runs up, and repeats until the last column. Lit runs of
# LENGTH pixels travel the path with GAP dark pixels between them, so several
# snakes are on the board at once.
#
# Set state.json "snake_path" to "sideways" (or use the snake control on the
# page) to run rows instead: top right to left, down a row, left to right, and
# so on. The script polls the revision, so the path changes live.
#
# The library buffer pads three hidden columns between each 5x7 matrix, so
# visible columns are mapped onto the buffer. Without the mapping the snakes
# would vanish for a third of every lap.
#
# The page speed slider works here because support/sitecustomize.py scales
# time.sleep by state.json "speed". Lower FRAME for a faster default.

import time

import _xpi_state
import microdotphat

WIDTH = getattr(microdotphat, "WIDTH", 45)
HEIGHT = getattr(microdotphat, "HEIGHT", 7)

MATRIX = 5              # visible columns per 5x7 matrix
STRIDE = 8              # buffer columns from one matrix start to the next
MATRICES = (WIDTH + STRIDE - MATRIX) // STRIDE
VISIBLE = MATRICES * MATRIX
LENGTH = 8              # lit pixels in each snake
GAP = 34                # dark pixels between snakes
FRAME = 0.08            # seconds per step, before the speed slider


def buffer_x(x):
    """Map a visible column to the library buffer, skipping hidden columns."""
    return (x // MATRIX) * STRIDE + x % MATRIX


def build_columns():
    """Top left down, one right, up, one right, down ..."""
    path = []
    for x in range(VISIBLE):
        if x % 2:
            rows = range(HEIGHT - 1, -1, -1)
        else:
            rows = range(HEIGHT)
        for y in rows:
            path.append((buffer_x(x), y))
    return path


def build_rows():
    """Top right to left, down a row, left to right, down a row ..."""
    path = []
    for y in range(HEIGHT):
        if y % 2:
            columns = range(VISIBLE)
        else:
            columns = range(VISIBLE - 1, -1, -1)
        for x in columns:
            path.append((buffer_x(x), y))
    return path


def build_path(sideways):
    return build_rows() if sideways else build_columns()


def sideways_now():
    value = str(_xpi_state.value("snake_path", "down")).strip().lower()
    return value == "sideways"


def main():
    sideways = sideways_now()
    path = build_path(sideways)
    period = LENGTH + GAP
    snakes = max(1, len(path) // period)
    print("snake.py: %d snakes over %d pixels, %s"
          % (snakes, len(path), "sideways" if sideways else "down"))

    offset = 0
    frames = 0
    revision = _xpi_state.revision()
    while True:
        microdotphat.clear()
        for step, (x, y) in enumerate(path):
            if (step - offset) % period < LENGTH:
                microdotphat.set_pixel(x, y, 1)
        microdotphat.show()
        offset = (offset + 1) % period

        frames += 1
        if frames % 6 == 0:
            current = _xpi_state.revision()
            if current != revision:
                revision = current
                new_sideways = sideways_now()
                if new_sideways != sideways:
                    sideways = new_sideways
                    path = build_path(sideways)
                    offset = 0
                    print("snake.py: path switched to",
                          "sideways" if sideways else "down")
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
