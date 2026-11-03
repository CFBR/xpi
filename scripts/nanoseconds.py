# nanoseconds.py — six digits that change at every refresh.
#
# Shows time.time_ns() mod 1000000, so each frame is a new value, like the
# nanoseconds column of a clock. Works on the microdot-phat and on a Unicorn
# HAT/pHAT.

import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)


def value():
    return time.time_ns() % 1000000


def run_microdot():
    import microdotphat

    print("nanoseconds.py: microdot-phat flashing digits")

    while True:
        microdotphat.clear()
        microdotphat.write_string("%06d" % value(), kerning=False)
        microdotphat.show()
        time.sleep(0.01)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    offset = 0
    last_revision = _xpi_state.revision()
    print("nanoseconds.py: unicorn flashing digits, color", color)

    while True:
        grid = _display.text_bitmap("%06d" % value())
        new_revision = _xpi_state.revision()
        if new_revision != last_revision:
            last_revision = new_revision
            unicornhat.brightness(_display.brightness_value())
            color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
        _display.draw_unicorn(grid, offset, shape, color)
        offset += 1
        time.sleep(0.05)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("nanoseconds.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("nanoseconds.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
