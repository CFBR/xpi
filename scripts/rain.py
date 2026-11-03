# rain.py — falling green rain on a Unicorn board.
#
# On the microdot-phat it falls back to a mono dot rain, since the display has
# no color. The global speed control scales its frame delay.

import random
import time

import _display


def delay():
    # fixed base delay; sitecustomize scales it by state.json "speed"
    return 0.12


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    drops = [random.randint(0, height) for _ in range(width)]
    print("rain.py: unicorn rain")

    while True:
        unicornhat.clear()
        for x in range(width):
            y = drops[x]
            if y < height:
                unicornhat.set_pixel(x, y, 0, 255, 70)
            if 0 <= y - 1 < height:
                unicornhat.set_pixel(x, y - 1, 0, 120, 30)
            if 0 <= y - 2 < height:
                unicornhat.set_pixel(x, y - 2, 0, 40, 10)
            drops[x] = (y + 1) % (height + 2) if random.random() > 0.08 else y
        unicornhat.show()
        time.sleep(delay())


def run_microdot():
    import microdotphat

    width = getattr(microdotphat, "WIDTH", 45)
    height = getattr(microdotphat, "HEIGHT", 7)
    print("rain.py: microdot-phat dot rain")

    while True:
        microdotphat.clear()
        for _ in range(width // 3):
            x = random.randrange(width)
            y = random.randrange(height)
            microdotphat.set_pixel(x, y, 1)
            if y + 1 < height:
                microdotphat.set_pixel(x, y + 1, 1)
        microdotphat.show()
        time.sleep(delay())


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("rain.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("rain.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
