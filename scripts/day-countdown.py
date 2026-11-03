# day-countdown.py — counts down the time left in the day.
#
# Shows 24:00:00 at midnight, then 23:59:59 and down. Works on the
# microdot-phat and on a Unicorn HAT/pHAT. Color and brightness come from
# state.json, so /action=update recolors it without a restart.

import datetime
import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)


def remaining_seconds():
    """Seconds until the next midnight, 86400 at exactly 00:00:00."""
    now = datetime.datetime.now()
    midnight = datetime.datetime.combine(
        now.date() + datetime.timedelta(days=1), datetime.time.min)
    return max(0, int((midnight - now).total_seconds()))


def split(seconds):
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return hours, minutes, secs


def format_text(seconds):
    hours, minutes, secs = split(seconds)
    return "%02d:%02d:%02d" % (hours, minutes, secs)


def run_microdot():
    import microdotphat

    print("day-countdown.py: microdot-phat counting down to midnight")

    while True:
        seconds = remaining_seconds()
        hours, minutes, secs = split(seconds)
        microdotphat.clear()
        # blinking separators, same positions the Pimoroni clock uses
        on = 1 if int(time.time()) % 2 == 0 else 0
        microdotphat.set_decimal(2, on)
        microdotphat.set_decimal(4, on)
        microdotphat.write_string("%02d%02d%02d" % (hours, minutes, secs),
                                  kerning=False)
        microdotphat.show()
        time.sleep(0.2)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    text = format_text(remaining_seconds())
    grid = _display.text_bitmap(text)
    offset = 0
    last_revision = _xpi_state.revision()
    print("day-countdown.py: unicorn showing", text, "color", color)

    while True:
        now_text = format_text(remaining_seconds())
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
        print("day-countdown.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("day-countdown.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
