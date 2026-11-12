# aquarium.py: a small tank on a Unicorn board.
#
# A dark blue water gradient sits behind swaying seaweed, rising bubbles and a
# few fish. Fish turn at the edges and occasionally change depth.

import math
import random
import time

import _display

FRAME = 0.12

FISH_COLORS = [(255, 120, 30), (255, 200, 40),
               (60, 180, 255), (220, 90, 200)]


def sprite(direction):
    if direction > 0:
        return ((0, 1, 1), (1, 1, 1))
    return ((1, 1, 0), (1, 1, 1))


def main():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    count = max(1, width // 6)
    fish = []
    for _ in range(count):
        fish.append([random.uniform(0, width - 3),
                     random.uniform(0, max(0, height - 2)),
                     random.choice((-1, 1)) * random.uniform(0.08, 0.16),
                     random.choice(FISH_COLORS)])
    bubbles = []
    for _ in range(max(3, width // 3)):
        bubbles.append([random.uniform(0, width), random.uniform(0, height),
                        random.uniform(0.12, 0.3)])
    seaweed = [max(1, width // 8) + i * max(3, width // 4)
               for i in range(3)]
    print("aquarium.py: tank on %dx%d" % (width, height))

    t = 0.0
    while True:
        unicornhat.clear()
        for y in range(height):
            for x in range(width):
                shade = y / max(1, height - 1)
                unicornhat.set_pixel(x, y, 0,
                                     int(10 - shade * 4),
                                     int(34 - shade * 16))

        for i, sx in enumerate(seaweed):
            stalk = 2 + (i % 2)
            sway = math.sin(t * 1.2 + i * 1.7) * 0.7
            for k in range(stalk):
                x = int(round(sx + sway * (k / float(stalk))))
                y = height - 1 - k
                if 0 <= x < width and 0 <= y < height:
                    unicornhat.set_pixel(x, y, 0, 90 + k * 40, 20)

        for bubble in bubbles:
            bubble[1] -= bubble[2]
            if bubble[1] < 0:
                bubble[0] = random.uniform(0, width)
                bubble[1] = float(height - 1)
            x = int(bubble[0]) % width
            y = int(bubble[1])
            if 0 <= y < height:
                unicornhat.set_pixel(x, y, 70, 120, 180)

        for item in fish:
            item[0] += item[2]
            direction = 1 if item[2] > 0 else -1
            if item[0] <= 0:
                item[0] = 0.0
                item[2] = abs(item[2])
            elif item[0] >= width - 3:
                item[0] = float(width - 3)
                item[2] = -abs(item[2])
            if random.random() < 0.02:
                item[1] = max(0.0, min(height - 2.0,
                                      item[1] + random.choice((-1, 1))))

            x0 = int(round(item[0]))
            y0 = int(round(item[1]))
            body = sprite(direction)
            r, g, b = item[3]
            for sy, row in enumerate(body):
                for sx, value in enumerate(row):
                    if value and 0 <= x0 + sx < width and 0 <= y0 + sy < height:
                        unicornhat.set_pixel(x0 + sx, y0 + sy, r, g, b)
            ex = x0 + (2 if direction > 0 else 0)
            if 0 <= ex < width and 0 <= y0 < height:
                unicornhat.set_pixel(ex, y0, 255, 255, 255)

        unicornhat.show()
        t += 0.12
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
