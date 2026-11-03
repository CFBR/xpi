# fast-countdown.py — 999999 at midnight, 0 at the end of the day.
#
# The counter is scaled to the day, so it drops about 11.6 per second instead
# of one. Works on the microdot-phat and on a Unicorn HAT/pHAT. Color and
# brightness come from state.json.

import datetime
import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)
TOP = 999999
DAY_SECONDS = 86400


def seconds_left():
    """Seconds until the next midnight, 86400 at exactly 00:00:00."""
    now = datetime.datetime.now()
    midnight = datetime.datetime.combine(
        now.date() + datetime.timedelta(days=1), datetime.time.min)
    return max(0, int((midnight - now).total_seconds()))


def counter():
    """999999 at the start of the day, 0 as the day ends."""
    return int(round(TOP * seconds_left() / float(DAY_SECONDS)))


def run_microdot():
    import microdotphat

    print("fast-countdown.py: microdot-phat, 999999 at midnight")

    while True:
        microdotphat.clear()
        microdotphat.write_string("%06d" % counter(), kerning=False)
        microdotphat.show()
        time.sleep(0.2)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    text = "%06d" % counter()
    grid = _display.text_bitmap(text)
    offset = 0
    last_revision = _xpi_state.revision()
    print("fast-countdown.py: unicorn showing", text, "color", color)

    while True:
        now_text = "%06d" % counter()
        if now_text != text:
            text = now_text
            grid = _display.text_bitmap(text)
            offset = 0
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
        print("fast-countdown.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("fast-countdown.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
