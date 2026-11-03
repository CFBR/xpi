# morse.py — blinks a message in Morse code.
#
# Text comes from state.json "message" (default SOS). Dot, dash and gap
# lengths come from "unit" in seconds (default 0.15). Works on either board.

import time

import _display
import _xpi_state

CODE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
}
DEFAULT_COLOR = (0, 255, 255)


def unit():
    try:
        return max(0.05, float(_xpi_state.value("unit") or 0.15))
    except (TypeError, ValueError):
        return 0.15


def message():
    return str(_xpi_state.value("message") or "SOS").upper()


def symbols(text):
    for word in text.split():
        for char in word:
            for mark in CODE.get(char, ""):
                yield mark
            yield "/"
        yield "//"


def run_microdot():
    import microdotphat

    print("morse.py: microdot-phat blinking", message())
    while True:
        for mark in symbols(message()):
            if mark == "/":
                microdotphat.clear()
                microdotphat.show()
                time.sleep(unit() * 2)
            elif mark == "//":
                time.sleep(unit() * 4)
            else:
                microdotphat.fill(1)
                microdotphat.show()
                time.sleep(unit() * (1 if mark == "." else 3))
                microdotphat.clear()
                microdotphat.show()
                time.sleep(unit())


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    print("morse.py: unicorn blinking", message(), "color", color)

    r, g, b = color
    for y in range(height):
        for x in range(width):
            unicornhat.set_pixel(x, y, r, g, b)

    while True:
        for mark in symbols(message()):
            if mark == "/":
                unicornhat.clear()
                unicornhat.show()
                time.sleep(unit() * 2)
            elif mark == "//":
                time.sleep(unit() * 4)
            else:
                for y in range(height):
                    for x in range(width):
                        unicornhat.set_pixel(x, y, r, g, b)
                unicornhat.show()
                time.sleep(unit() * (1 if mark == "." else 3))
                unicornhat.clear()
                unicornhat.show()
                time.sleep(unit())


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("morse.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("morse.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
