# dice.py — rolls a six-sided die when it starts.
#
# The microdot-phat shows the number; the Unicorn pHAT shows pips. Restart the
# script (Run on the page) to roll again.

import random
import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)
PIPS = {
    1: [(1, 1)],
    2: [(0, 0), (2, 2)],
    3: [(0, 0), (1, 1), (2, 2)],
    4: [(0, 0), (2, 0), (0, 2), (2, 2)],
    5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)],
    6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)],
}


def run_microdot():
    import microdotphat

    roll = random.randint(1, 6)
    print("dice.py: microdot-phat rolled", roll)
    microdotphat.clear()
    microdotphat.write_string(str(roll))
    microdotphat.show()
    while True:
        time.sleep(1)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    roll = random.randint(1, 6)
    print("dice.py: unicorn rolled", roll)

    x0 = max(0, (width - 3) // 2)
    y0 = max(0, (height - 3) // 2)
    unicornhat.clear()
    r, g, b = color
    for px, py in PIPS[roll]:
        unicornhat.set_pixel(x0 + px, y0 + py, r, g, b)
    unicornhat.show()
    while True:
        time.sleep(1)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("dice.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("dice.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
