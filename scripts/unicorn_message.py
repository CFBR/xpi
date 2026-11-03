# unicorn_message.py — text on a Unicorn board, scrolling or word by word.
#
# state.json keys:
#   message        text to show
#   color          name or #RRGGBB
#   direction      "left" (default) or "right"
#   mode           "scroll" (default) or "word"
#   text_speed     scroll pixels per frame, default 1
#   word_seconds   how long each word stays in word mode, default 1
#   fade           1 to fade each word in and out

import sys
import time

import unicornhat
import _xpi_state
import _display

DEFAULT_COLOR = (255, 255, 255)


def setting(key, default=None):
    value = _xpi_state.value(key)
    return default if value is None else value


def get_message():
    text = _xpi_state.value("message")
    if text is None and len(sys.argv) > 1:
        text = sys.argv[1]
    return str(text if text is not None else "hi").upper()


def direction():
    return -1 if str(setting("direction", "left")).lower() == "right" else 1


def speed():
    try:
        return max(0.1, min(8.0, float(setting("text_speed", 1))))
    except (TypeError, ValueError):
        return 1.0


def word_seconds():
    try:
        return max(0.2, float(setting("word_seconds", 1.0)))
    except (TypeError, ValueError):
        return 1.0


def fade_on():
    return str(setting("fade", "0")).lower() in ("1", "true", "yes", "on")


def word_mode():
    return str(setting("mode", "scroll")).lower() == "word"


shape, unicornhat = _display.setup_unicorn()
text = get_message()
color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)


def run_scroll():
    global text, color
    grid = _display.text_bitmap(text)
    offset = 0
    carry = 0.0
    last_revision = _xpi_state.revision()
    print("unicorn_message.py: scrolling", text, "color", color)

    while True:
        if _xpi_state.revision() != last_revision:
            last_revision = _xpi_state.revision()
            new_color = _display.parse_color(
                _xpi_state.value("color"), DEFAULT_COLOR)
            if new_color != color:
                color = new_color
            new_text = get_message()
            if new_text != text:
                text = new_text
                grid = _display.text_bitmap(text)
                offset = 0
                print("unicorn_message.py: switched to", text)
        carry += speed()
        step = int(carry)
        if step:
            carry -= step
            offset += step * direction()
        _display.draw_unicorn(grid, offset, shape, color)
        time.sleep(0.05)


def run_words():
    global text, color
    words = text.split() or [" "]
    index = 0
    last_revision = _xpi_state.revision()
    print("unicorn_message.py: words", text, "color", color)

    while True:
        if _xpi_state.revision() != last_revision:
            last_revision = _xpi_state.revision()
            color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
            new_text = get_message()
            if new_text != text:
                text = new_text
                words = text.split() or [" "]
                index = 0
                print("unicorn_message.py: switched to", text)
        word = words[index % len(words)]
        grid = _display.text_bitmap(word)
        width, _ = shape
        frames = max(1, int(word_seconds() / 0.05))
        fade_frames = max(1, int(0.3 / 0.05))
        for frame in range(frames):
            if len(grid[0]) <= width:
                offset = (width - len(grid[0])) // 2
            else:
                offset = int((len(grid[0]) - width) * frame / frames)
            level = 1.0
            if fade_on():
                if frame < fade_frames:
                    level = frame / float(fade_frames)
                elif frame > frames - fade_frames:
                    level = (frames - frame) / float(fade_frames)
            unicornhat.brightness(max(0.05, level))
            _display.draw_unicorn(grid, offset, shape, color)
            time.sleep(0.05)
        unicornhat.brightness(1.0)
        index += 1


def main():
    if word_mode():
        run_words()
    else:
        run_scroll()


if __name__ == "__main__":
    main()
