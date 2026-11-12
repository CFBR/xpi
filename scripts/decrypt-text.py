# decrypt-text.py — scramble each word, then decode it one letter at a time.
#
# state.json keys:
#   message       words to show, default "DECODE THE SIGNAL"
#   word_seconds  pause after each decoded word, default 1.4
#   text_speed    decode speed multiplier, default 1
#   color         Unicorn color name or #RRGGBB
#
# The Micro Dot pHAT shows one character per 5x7 matrix. Words longer than
# six characters scroll one matrix at a time as each new character resolves.
# The script polls the revision, so message changes apply at the next word.

import random
import string
import sys
import time

import _display
import _dot
import _xpi_state

DEFAULT_MESSAGE = "DECODE THE SIGNAL"
DEFAULT_COLOR = (255, 255, 255)
ALPHABET = string.ascii_uppercase + string.digits + "!?#$%&@*+-=<>"
MICRODOT_SLOTS = 6


def setting(key, default=None):
    value = _xpi_state.value(key)
    return default if value is None else value


def speed():
    try:
        return max(0.1, min(8.0, float(setting("text_speed", 1))))
    except (TypeError, ValueError):
        return 1.0


def frame_delay():
    return 0.10 / speed()


def hold_seconds():
    try:
        return max(0.2, min(10.0, float(setting("word_seconds", 1.4))))
    except (TypeError, ValueError):
        return 1.4


def get_words():
    raw = _xpi_state.value("message")
    if raw is None and len(sys.argv) > 1:
        raw = " ".join(sys.argv[1:])
    text = str(raw if raw is not None else DEFAULT_MESSAGE).upper()
    text = "".join(ch if 32 <= ord(ch) < 127 else " " for ch in text)
    words = text.split()
    return words or DEFAULT_MESSAGE.split()


def random_char(char):
    if char == " ":
        return " "
    choices = [c for c in ALPHABET if c != char]
    return random.choice(choices)


def render_window(word, start, slots, revealed):
    chars = []
    for i in range(start, min(start + slots, len(word))):
        chars.append(word[i] if i < revealed else random_char(word[i]))
    return "".join(chars)


def show_word(word, draw, slots, delay, hold):
    """Run one word through the scramble and reveal cycle."""
    length = len(word)
    if length == 0:
        return
    limit = min(length, slots)
    for revealed in range(limit + 1):
        draw(render_window(word, 0, slots, revealed))
        time.sleep(delay())
    if length <= slots:
        time.sleep(hold())
        return
    for new_index in range(slots, length):
        start = new_index - slots + 1
        draw(render_window(word, start, slots, new_index))
        time.sleep(delay())
        draw(render_window(word, start, slots, new_index + 1))
        time.sleep(delay())
    time.sleep(hold())


def draw_microdot(text, slots):
    import microdotphat
    from microdotphat.font import font

    microdotphat.clear()
    start = (slots - len(text)) // 2
    for i, char in enumerate(text):
        glyph = font.get(ord(char))
        if glyph is None:
            continue
        x0 = (start + i) * _dot.MATRIX
        for gx, column in enumerate(glyph):
            for gy in range(7):
                if column & (1 << gy):
                    microdotphat.set_pixel(_dot.buffer_x(x0 + gx), gy, 1)
    microdotphat.show()


def draw_unicorn(text, shape, unicornhat, color):
    grid = _display.text_bitmap(text)
    width, height = shape
    x0 = max(0, (width - len(grid[0])) // 2)
    y0 = max(0, (height - 5) // 2)
    r, g, b = color
    unicornhat.clear()
    for y in range(min(5, height)):
        for x in range(min(len(grid[0]), width - x0)):
            if grid[y][x]:
                unicornhat.set_pixel(x0 + x, y0 + y, r, g, b)
    unicornhat.show()


def run_effect(draw, slots):
    words = get_words()
    index = 0
    revision = _xpi_state.revision()
    print("decrypt-text.py: words", " ".join(words), "slots", slots)
    while True:
        if _xpi_state.revision() != revision:
            revision = _xpi_state.revision()
            new_words = get_words()
            if new_words != words:
                words = new_words
                index = 0
                print("decrypt-text.py: switched to", " ".join(words))
        word = words[index % len(words)]
        show_word(word, draw, slots, frame_delay, hold_seconds)
        index += 1


def run_microdot():
    import microdotphat

    width = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
    slots = max(1, min(width // _dot.MATRIX, MICRODOT_SLOTS))

    def draw(text):
        draw_microdot(text, slots)

    print("decrypt-text.py: microdot-phat", slots, "matrices")
    return run_effect(draw, slots)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    slots = max(1, shape[0] // _display.CHAR_W)

    def draw(text):
        color = _display.parse_color(
            _xpi_state.value("color"), DEFAULT_COLOR)
        draw_unicorn(text, shape, unicornhat, color)

    print("decrypt-text.py: unicorn", shape, slots, "characters")
    return run_effect(draw, slots)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("decrypt-text.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("decrypt-text.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
