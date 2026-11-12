# aurora.py: colored curtains on a Unicorn board.
#
# Two slow sine waves move the curtain baseline. Each column lights from that
# baseline outward with a green to blue gradient, and a few dim stars sit
# behind the display.

import math
import random
import time

import _display

FRAME = 0.10


def main():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    stars = []
    for _ in range(max(4, width // 3)):
        stars.append((random.randrange(width), random.randrange(height),
                      random.uniform(0.15, 0.5)))
    print("aurora.py: curtains on %dx%d" % (width, height))

    t = 0.0
    while True:
        unicornhat.clear()
        for x, y, bright in stars:
            value = int(70 * bright)
            unicornhat.set_pixel(x, y, value, value, value * 2)

        for x in range(width):
            base = (height - 1) / 2.0 \
                + math.sin(x * 0.5 + t * 1.2) * height * 0.30 \
                + math.sin(x * 1.1 - t * 0.8) * height * 0.12
            for y in range(height):
                value = 1.0 - abs(y - base) / (height * 0.25)
                if value <= 0:
                    continue
                value *= 0.7 + 0.3 * math.sin(x * 1.7 + t * 2.1 + y * 0.9)
                r = int(value * (70 + 50 * math.sin(t * 0.7 + x * 0.3)))
                g = int(value * 200)
                b = int(value * (120 + 70 * math.sin(t * 1.1 + x * 0.5)))
                unicornhat.set_pixel(x, y,
                                     max(0, min(255, r)),
                                     max(0, min(255, g)),
                                     max(0, min(255, b)))

        unicornhat.show()
        t += 0.09
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
