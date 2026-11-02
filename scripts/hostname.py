# hostname.py — shows this Pi's hostname on whichever display responds.
#
# Text comes from /etc/hostname (fallback os.uname()). On the microdot-phat
# it's plain white scrolling text. On the unicorn pHAT it uses the 3x5
# renderer with a color from state.json ("color": "#RRGGBB" or name).
# Picks the display once at startup, then runs until killed.

import os
import sys
import time

import _xpi_state
import _display

DEFAULT_COLOR = (255, 255, 255)


def get_text():
    try:
        with open("/etc/hostname") as fh:
            name = fh.read().strip()
    except OSError:
        name = os.uname().nodename
    return name or "pi"


def run_microdot(text):
    import microdotphat

    print("hostname.py: microdot-phat showing", text)
    current_color_revision = _xpi_state.revision()
    microdotphat.write_string(text)
    microdotphat.show()

    while True:
        if _xpi_state.revision() != current_color_revision:
            current_color_revision = _xpi_state.revision()
            new_text = get_text()
            if new_text != text:
                text = new_text
                microdotphat.write_string(text)
                print("hostname.py: switched to", text)
        microdotphat.scroll()
        microdotphat.show()
        time.sleep(0.05)


def run_unicorn(text, color=None):
    import unicornhat

    color = _display.parse_color(color, DEFAULT_COLOR)
    shape, unicornhat = _display.setup_unicorn()
    grid = _display.text_bitmap(text)
    offset = 0
    last_revision = _xpi_state.revision()
    print("hostname.py: unicorn showing", text, "color", color)

    while True:
        new_revision = _xpi_state.revision()
        if new_revision != last_revision:
            last_revision = new_revision
            unicornhat.brightness(_display.brightness_value())
            new_color = _display.parse_color(
                _xpi_state.value("color"), DEFAULT_COLOR)
            if new_color != color:
                color = new_color
                print("hostname.py: color switched to", color)
            new_text = get_text()
            if new_text != text:
                text = new_text
                grid = _display.text_bitmap(text)
                offset = 0
                print("hostname.py: switched to", text)
        _display.draw_unicorn(grid, offset, shape, color)
        offset += 1
        time.sleep(0.05)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot(get_text())
    except Exception as exc:
        print("hostname.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("hostname.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    color = _xpi_state.value("color")
    return run_unicorn(get_text(), color)


if __name__ == "__main__":
    main()
