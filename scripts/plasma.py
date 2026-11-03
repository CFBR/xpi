# plasma.py — slow color plasma on a Unicorn board.
#
# Falls back to a moving mono wave on the microdot-phat.

import math
import time

import _display
import _xpi_state


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    print("plasma.py: unicorn plasma")
    t = 0.0

    while True:
        for x in range(width):
            for y in range(height):
                v = math.sin(x * 0.7 + t) + math.sin(y * 0.9 + t * 1.3) \
                    + math.sin((x + y) * 0.5 + t * 0.7)
                r = int((math.sin(v) + 1) * 127)
                g = int((math.sin(v + 2.1) + 1) * 127)
                b = int((math.sin(v + 4.2) + 1) * 127)
                unicornhat.set_pixel(x, y, r, g, b)
        unicornhat.show()
        t += 0.15
        time.sleep(0.08)


def run_microdot():
    import microdotphat

    width = getattr(microdotphat, "WIDTH", 45)
    height = getattr(microdotphat, "HEIGHT", 7)
    print("plasma.py: microdot-phat wave")
    t = 0.0

    while True:
        microdotphat.clear()
        for x in range(width):
            level = int((math.sin(x * 0.25 + t) + 1) * (height - 1) / 2)
            for y in range(level + 1):
                microdotphat.set_pixel(x, height - 1 - y, 1)
        microdotphat.show()
        t += 0.3
        time.sleep(0.08)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("plasma.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("plasma.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
