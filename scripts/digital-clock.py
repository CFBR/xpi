# clock.py — scrolls the time (HH:MM) on whichever board answers.
#
# Works on the microdot-phat and the Unicorn HAT/pHAT. The text refreshes at
# each minute. Color and brightness come from state.json, so /action=update
# recolors it without a restart.

import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)


def get_text():
    return time.strftime("%H:%M")


def run_microdot():
    import microdotphat

    text = get_text()
    print("clock.py: microdot-phat showing", text)
    microdotphat.write_string(text)
    microdotphat.show()

    while True:
        now = get_text()
        if now != text:
            text = now
            microdotphat.write_string(text)
            print("clock.py: showing", text)
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
    print("clock.py: unicorn showing", text, "color", color)

    while True:
        now = get_text()
        if now != text:
            text = now
            grid = _display.text_bitmap(text)
            offset = 0
            print("clock.py: showing", text)
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
        print("clock.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("clock.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
