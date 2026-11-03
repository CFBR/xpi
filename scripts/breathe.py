# breathe.py — fades a solid color up and down.
#
# On a Unicorn board it drives the brightness; the microdot-phat can only turn
# pixels on and off, so it blinks the fill instead. Color from state.json.

import math
import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    print("breathe.py: unicorn breathing", color)

    r, g, b = color
    for y in range(height):
        for x in range(width):
            unicornhat.set_pixel(x, y, r, g, b)
    unicornhat.show()

    step = 0.0
    while True:
        level = (math.sin(step) + 1) / 2
        unicornhat.brightness(max(0.05, level))
        unicornhat.show()
        step += 0.06
        time.sleep(0.05)


def run_microdot():
    import microdotphat

    print("breathe.py: microdot-phat blink")
    on = False

    while True:
        on = not on
        if on:
            microdotphat.fill(1)
        else:
            microdotphat.clear()
        microdotphat.show()
        time.sleep(0.6)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("breathe.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("breathe.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
