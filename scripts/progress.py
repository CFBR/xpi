# progress.py — a 0 to 100 bar from state.json.
#
# Set it with /action=update&percent=40. The bar fills left to right; on a
# Unicorn board it uses the state color, on the microdot-phat it lights the
# leftmost columns. Useful for disk use, a build, or a long job.

import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)


def percent():
    try:
        value = float(_xpi_state.value("percent") or 0)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(100.0, value))


def run_microdot():
    import microdotphat

    width = getattr(microdotphat, "WIDTH", 45)
    height = getattr(microdotphat, "HEIGHT", 7)
    print("progress.py: microdot-phat bar")

    last = None
    while True:
        value = percent()
        if value != last:
            last = value
            filled = int(round(width * value / 100.0))
            microdotphat.clear()
            for x in range(filled):
                for y in range(height):
                    microdotphat.set_pixel(x, y, 1)
            microdotphat.show()
            print("progress.py: %d%%" % value)
        time.sleep(0.2)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    print("progress.py: unicorn bar")

    last = None
    last_revision = _xpi_state.revision()
    while True:
        value = percent()
        new_revision = _xpi_state.revision()
        if value != last or new_revision != last_revision:
            last = value
            last_revision = new_revision
            unicornhat.brightness(_display.brightness_value())
            color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
            filled = int(round(width * value / 100.0))
            unicornhat.clear()
            r, g, b = color
            for x in range(filled):
                for y in range(height):
                    unicornhat.set_pixel(x, y, r, g, b)
            unicornhat.show()
            print("progress.py: %d%%" % value)
        time.sleep(0.2)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("progress.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("progress.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
