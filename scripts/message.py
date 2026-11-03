# message.py — text on the microdot-phat, scrolling or word by word.
#
# state.json keys:
#   message        text to show
#   direction      "left" (default) or "right"
#   mode           "scroll" (default) or "word"
#   text_speed     scroll pixels per frame, default 1
#   word_seconds   how long each word stays in word mode, default 1
#   fade           1 to fade each word in and out
#
# Polls the revision, so /action=update changes text and settings live.

import sys
import time

import microdotphat
import _xpi_state

WIDTH = 45


def setting(key, default=None):
    value = _xpi_state.value(key)
    return default if value is None else value


def get_text():
    text = _xpi_state.value("message")
    if text is None and len(sys.argv) > 1:
        text = sys.argv[1]
    return str(text if text is not None else "hi")


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


def brightness_scale():
    try:
        return max(0.0, min(1.0, float(setting("brightness", 1.0))))
    except (TypeError, ValueError):
        return 1.0


def center_offset(text):
    return max(0, (WIDTH - len(text) * 6) // 2)


def run_scroll():
    text = get_text()
    microdotphat.write_string(text)
    print("message.py: scrolling", text, "direction",
          "right" if direction() < 0 else "left")
    current = _xpi_state.revision()
    carry = 0.0

    while True:
        if _xpi_state.revision() != current:
            current = _xpi_state.revision()
            new_text = get_text()
            if new_text != text:
                text = new_text
                microdotphat.clear()
                microdotphat.write_string(text)
                print("message.py: switched to", text)
        carry += speed()
        step = int(carry)
        if step:
            carry -= step
            microdotphat.scroll(amount_x=step * direction())
        microdotphat.show()
        time.sleep(0.05)


def run_words():
    text = get_text()
    words = text.split() or [" "]
    index = 0
    current = _xpi_state.revision()
    print("message.py: words", text)

    while True:
        if _xpi_state.revision() != current:
            current = _xpi_state.revision()
            new_text = get_text()
            if new_text != text:
                text = new_text
                words = text.split() or [" "]
                index = 0
                print("message.py: switched to", text)
        word = words[index % len(words)]
        microdotphat.clear()
        microdotphat.write_string(word, offset_x=center_offset(word),
                                  kerning=False)
        microdotphat.show()
        hold = word_seconds()
        scale = brightness_scale()
        if fade_on():
            steps = 6
            for i in range(steps + 1):
                microdotphat.set_brightness(scale * i / steps)
                microdotphat.show()
                time.sleep(0.05)
            time.sleep(max(0.0, hold - 0.6))
            for i in range(steps, -1, -1):
                microdotphat.set_brightness(scale * i / steps)
                microdotphat.show()
                time.sleep(0.05)
        else:
            time.sleep(hold)
        microdotphat.set_brightness(scale)
        index += 1


def main():
    if word_mode():
        run_words()
    else:
        run_scroll()


if __name__ == "__main__":
    main()
