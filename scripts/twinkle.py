# twinkle.py: dots appear and vanish on the Micro Dot pHAT.
#
# No sweep and no travel. Each dot picks a pixel, stays for a short random
# life, then flickers out. New dots keep appearing, so the field keeps
# changing in place.

import random
import time

import _dot
import microdotphat

WIDTH = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
HEIGHT = getattr(microdotphat, "HEIGHT", 7)
FRAME = 0.07
TARGET = 20
MIN_LIFE = 6
MAX_LIFE = 34


def main():
    print("twinkle.py: twinkling dots")
    dots = []

    while True:
        if len(dots) < TARGET:
            dots.append([random.randrange(WIDTH),
                         random.randrange(HEIGHT),
                         random.randint(MIN_LIFE, MAX_LIFE)])

        microdotphat.clear()
        alive = []
        for dot in dots:
            dot[2] -= 1
            if dot[2] <= 0:
                continue
            if dot[2] > 4 or random.random() < 0.55:
                microdotphat.set_pixel(_dot.buffer_x(dot[0]), dot[1], 1)
            alive.append(dot)
        dots = alive
        microdotphat.show()
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
