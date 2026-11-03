# fire.py — a small fire on a Unicorn board.
#
# Heat rises row by row and cools as it goes. The microdot-phat gets a mono
# flicker instead, since it has no color.

import random
import time

import _display
import _xpi_state


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    heat = [[0.0] * width for _ in range(height)]
    print("fire.py: unicorn fire")

    while True:
        for x in range(width):
            heat[height - 1][x] = random.uniform(0.7, 1.0)
        for y in range(height - 1):
            for x in range(width):
                below = heat[y + 1][x]
                left = heat[y + 1][(x - 1) % width]
                right = heat[y + 1][(x + 1) % width]
                heat[y][x] = max(0.0, (below * 2 + left + right) / 4 - random.uniform(0.05, 0.25))
        for y in range(height):
            for x in range(width):
                v = heat[y][x]
                r = int(min(255, v * 255))
                g = int(min(255, max(0, (v - 0.4)) * 400))
                unicornhat.set_pixel(x, y, r, g, 0)
        unicornhat.show()
        time.sleep(0.12)


def run_microdot():
    import microdotphat

    width = getattr(microdotphat, "WIDTH", 45)
    height = getattr(microdotphat, "HEIGHT", 7)
    print("fire.py: microdot-phat flicker")

    while True:
        microdotphat.clear()
        for _ in range(width // 2):
            x = random.randrange(width)
            for y in range(height - 1, max(-1, height - 1 - random.randrange(3)), -1):
                microdotphat.set_pixel(x, y, 1)
        microdotphat.show()
        time.sleep(0.12)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("fire.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("fire.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
