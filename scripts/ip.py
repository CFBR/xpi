# ip.py — scrolls this Pi's hostname and LAN address on whichever board answers.
#
# The address comes from _net.local_ip(); it refreshes when state.json's
# revision changes, so /action=update re-reads it after a DHCP change.

import os
import time

import _display
import _net
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)


def get_text():
    ip = _net.local_ip() or "no ip"
    return ("%s %s" % (os.uname().nodename, ip)).upper()


def run_microdot():
    import microdotphat

    text = get_text()
    print("ip.py: microdot-phat showing", text)
    microdotphat.write_string(text)
    microdotphat.show()
    last_revision = _xpi_state.revision()

    while True:
        if _xpi_state.revision() != last_revision:
            last_revision = _xpi_state.revision()
            new_text = get_text()
            if new_text != text:
                text = new_text
                microdotphat.write_string(text)
                print("ip.py: switched to", text)
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
    print("ip.py: unicorn showing", text, "color", color)

    while True:
        if _xpi_state.revision() != last_revision:
            last_revision = _xpi_state.revision()
            unicornhat.brightness(_display.brightness_value())
            color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
            new_text = get_text()
            if new_text != text:
                text = new_text
                grid = _display.text_bitmap(text)
                offset = 0
                print("ip.py: switched to", text)
        _display.draw_unicorn(grid, offset, shape, color)
        offset += 1
        time.sleep(0.05)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("ip.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("ip.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
