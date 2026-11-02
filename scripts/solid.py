# solid.py — fills the whole board with one color.
#
# Color comes from state.json "color" (a name or "#RRGGBB"), default white.
# Handy as a lamp, a brightness test, or to check every pixel. Polls the
# revision, so /action=update&color=red recolors it without a restart.

import time

import _display
import _xpi_state

DEFAULT_COLOR = (255, 255, 255)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    print("solid.py: unicorn filling", shape, "with", color)

    def fill(rgb):
        unicornhat.clear()
        r, g, b = rgb
        for y in range(height):
            for x in range(width):
                unicornhat.set_pixel(x, y, r, g, b)
        unicornhat.show()

    fill(color)
    last_revision = _xpi_state.revision()

    while True:
        if _xpi_state.revision() != last_revision:
            last_revision = _xpi_state.revision()
            unicornhat.brightness(_display.brightness_value())
            new_color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
            if new_color != color:
                color = new_color
                print("solid.py: color switched to", color)
            fill(color)
        time.sleep(0.25)


def run_microdot():
    import microdotphat

    print("solid.py: microdot-phat filling all pixels")
    microdotphat.fill(1)
    microdotphat.show()
    last_revision = _xpi_state.revision()

    while True:
        if _xpi_state.revision() != last_revision:
            last_revision = _xpi_state.revision()
            microdotphat.fill(1)
            microdotphat.show()
        time.sleep(0.25)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("solid.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("solid.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
