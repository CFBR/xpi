# lightning.py: a storm on a Unicorn board.
#
# Dim clouds cover the top rows, rain falls, and a branching bolt flashes down
# every few seconds. The bolt cools over a handful of frames.

import math
import random
import time

import _display

FRAME = 0.05


def make_bolt(width, height):
    x = random.randrange(width)
    points = []
    for y in range(height):
        points.append((x, y))
        if random.random() < 0.65:
            x = max(0, min(width - 1, x + random.choice((-1, 1))))
            points.append((x, y))

        if y > 1 and random.random() < 0.30:
            bx = x
            for _ in range(random.randint(1, 2)):
                bx = max(0, min(width - 1, bx + random.choice((-1, 1))))
                points.append((bx, min(height - 1, y + 1)))
    return points


def main():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    rain = [[random.uniform(0, width), random.uniform(0, height),
             random.uniform(0.3, 0.9)] for _ in range(width * 2)]
    bolts = []
    frame = 0
    next_bolt = random.randint(20, 60)
    flash = 0
    print("lightning.py: storm on %dx%d" % (width, height))

    while True:
        frame += 1
        if frame >= next_bolt:
            for x, y in make_bolt(width, height):
                bolts.append([x, y, 10])
            flash = 4
            next_bolt = frame + random.randint(40, 120)

        unicornhat.clear()

        for y in range(min(2, height)):
            for x in range(width):
                value = 0.05 + 0.04 * math.sin(x * 0.8 + frame * 0.15 + y)
                unicornhat.set_pixel(x, y, int(value * 80),
                                     int(value * 90), int(value * 140))

        for drop in rain:
            drop[1] += drop[2]
            if drop[1] >= height:
                drop[0] = random.uniform(0, width)
                drop[1] = 0
                drop[2] = random.uniform(0.3, 0.9)
            x = int(drop[0]) % width
            y = int(drop[1])
            if 0 <= y < height:
                unicornhat.set_pixel(x, y, 30, 60, 160)

        alive = []
        for bolt in bolts:
            x, y, life = bolt
            bolt[2] -= 1
            if bolt[2] <= 0:
                continue
            value = min(255, 120 + life * 15)
            unicornhat.set_pixel(int(x), int(y), value, value, 255)
            alive.append(bolt)
        bolts = alive

        if flash:
            flash -= 1
            if flash % 2:
                for y in range(height):
                    for x in range(width):
                        unicornhat.set_pixel(x, y, 120, 140, 200)

        unicornhat.show()
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
