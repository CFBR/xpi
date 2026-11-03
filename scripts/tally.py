# tally.py — one number from state.json, for counting things up or down.
#
# Set it with /action=update&count=7. Shows the number on the microdot-phat
# and scrolls it on a Unicorn board. Color and brightness come from state.

import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)


def count():
    try:
        return int(_xpi_state.value("count") or 0)
    except (TypeError, ValueError):
        return 0


def run_microdot():
    import microdotphat

    print("tally.py: microdot-phat showing the count")
    value = count()
    microdotphat.write_string(str(value))
    microdotphat.show()

    while True:
        new_value = count()
        if new_value != value:
            value = new_value
            microdotphat.clear()
            microdotphat.write_string(str(value))
            microdotphat.show()
            print("tally.py: count", value)
        time.sleep(0.2)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    value = count()
    grid = _display.text_bitmap(str(value))
    offset = 0
    last_revision = _xpi_state.revision()
    print("tally.py: unicorn showing the count")

    while True:
        new_value = count()
        if new_value != value:
            value = new_value
            grid = _display.text_bitmap(str(value))
            offset = 0
            print("tally.py: count", value)
        new_revision = _xpi_state.revision()
        if new_revision != last_revision:
            last_revision = new_revision
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
        print("tally.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("tally.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
