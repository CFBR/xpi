# big-text.py — one or two characters as large as the board allows.
#
# Text comes from state.json "text" (default OK). The microdot-phat shows it
# with the library font; the 8x4 Unicorn pHAT shows the top four rows of the
# shared 3x5 font, so short words are best.

import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)


def text():
    return str(_xpi_state.value("text") or "OK").upper()


def run_microdot():
    import microdotphat

    value = text()
    print("big-text.py: microdot-phat", value)
    microdotphat.clear()
    microdotphat.write_string(value, kerning=False)
    microdotphat.show()

    while True:
        new_value = text()
        if new_value != value:
            value = new_value
            microdotphat.clear()
            microdotphat.write_string(value, kerning=False)
            microdotphat.show()
            print("big-text.py:", value)
        time.sleep(0.25)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    value = text()
    print("big-text.py: unicorn", value)

    def draw(symbols):
        rows = _display.text_bitmap(symbols)[:height]
        unicornhat.clear()
        r, g, b = color
        for y, row in enumerate(rows):
            for x, lit in enumerate(row[:width]):
                if lit:
                    unicornhat.set_pixel(x, y, r, g, b)
        unicornhat.show()

    draw(value)
    last_revision = _xpi_state.revision()

    while True:
        new_value = text()
        new_revision = _xpi_state.revision()
        if new_value != value or new_revision != last_revision:
            value = new_value
            last_revision = new_revision
            color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
            draw(value)
            print("big-text.py:", value)
        time.sleep(0.25)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("big-text.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("big-text.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
