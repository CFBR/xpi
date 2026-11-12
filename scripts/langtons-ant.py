# langtons-ant.py: Langton's ant walks the Micro Dot pHAT.
#
# The ant turns right on a dark cell, left on a lit one, flips that cell, and
# moves on. The grid wraps at the edges. A new run starts after RESET moves so
# the ant never settles into the same highway forever.

import random
import time

import _dot
import microdotphat

WIDTH = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
HEIGHT = getattr(microdotphat, "HEIGHT", 7)
STEPS = 3               # ant moves per frame
RESET = 2000            # moves before a fresh run
FRAME = 0.06

MOVE = ((0, -1), (1, 0), (0, 1), (-1, 0))   # up, right, down, left


def main():
    print("langtons-ant.py: Langton's ant")
    while True:
        black = [[0] * WIDTH for _ in range(HEIGHT)]
        x = random.randrange(WIDTH)
        y = random.randrange(HEIGHT)
        direction = random.randrange(4)

        for _ in range(RESET // STEPS):
            for _ in range(STEPS):
                if black[y][x]:
                    direction = (direction - 1) % 4
                else:
                    direction = (direction + 1) % 4
                black[y][x] ^= 1
                dx, dy = MOVE[direction]
                x = (x + dx) % WIDTH
                y = (y + dy) % HEIGHT

            microdotphat.clear()
            for gy in range(HEIGHT):
                for gx in range(WIDTH):
                    if black[gy][gx]:
                        microdotphat.set_pixel(_dot.buffer_x(gx), gy, 1)
            microdotphat.show()
            time.sleep(FRAME)


if __name__ == "__main__":
    main()
