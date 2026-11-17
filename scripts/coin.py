# coin.py — flips a coin when it starts.
#
# Shows H or T. Restart the script (Run on the page) to flip again.

import random
import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)


def flip():
    return random.choice(["H", "T"])


def run_microdot():
    import microdotphat

    side = flip()
    print("coin.py: microdot-phat flipped", side)
    microdotphat.clear()
    microdotphat.write_string(side)
    microdotphat.show()
    while True:
        time.sleep(1)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    side = flip()
    print("coin.py: unicorn flipped", side)

    grid = _display.text_bitmap(side[0], rows=height)
    rows = min(len(grid), height)
    r, g, b = color
    unicornhat.clear()
    x0 = max(0, (width - len(grid[0])) // 2)
    y0 = max(0, (height - rows) // 2)
    for y, row in enumerate(grid[:rows]):
        for x, lit in enumerate(row):
            if lit:
                unicornhat.set_pixel(x0 + x, y0 + y, r, g, b)
    unicornhat.show()
    while True:
        time.sleep(1)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("coin.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("coin.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
