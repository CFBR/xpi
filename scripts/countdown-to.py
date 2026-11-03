# countdown-to.py — counts down to a date and time from state.json.
#
# Set the target with /action=update&target=2026-12-25T00:00:00 (local time).
# Shows "3D 04:05:06" while more than a day is left, then "04:05:06", and
# "DONE" once the target passes. Works on either board.

import datetime
import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)


def target():
    raw = _xpi_state.value("target")
    if not raw:
        return None
    try:
        return datetime.datetime.fromisoformat(str(raw).strip())
    except ValueError:
        return None


def get_text():
    when = target()
    if when is None:
        return "NO TARGET"
    left = int((when - datetime.datetime.now()).total_seconds())
    if left <= 0:
        return "DONE"
    days, rest = divmod(left, 86400)
    hours, rest = divmod(rest, 3600)
    minutes, seconds = divmod(rest, 60)
    if days:
        return "%dD %02d:%02d:%02d" % (days, hours, minutes, seconds)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


def run_microdot():
    import microdotphat

    print("countdown-to.py: microdot-phat counting to", target())
    text = get_text()
    microdotphat.write_string(text)
    microdotphat.show()

    while True:
        new_text = get_text()
        if new_text != text:
            text = new_text
            microdotphat.write_string(text)
            print("countdown-to.py:", text)
        microdotphat.scroll()
        microdotphat.show()
        time.sleep(0.05)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    text = get_text()
    grid = _display.text_bitmap(text)
    offset = 0
    last_revision = _xpi_state.revision()
    print("countdown-to.py: unicorn counting to", target())

    while True:
        new_text = get_text()
        if new_text != text:
            text = new_text
            grid = _display.text_bitmap(text)
            offset = 0
            print("countdown-to.py:", text)
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
        print("countdown-to.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("countdown-to.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
