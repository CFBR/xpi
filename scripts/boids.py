# boids.py: a flock of colored particles on a Unicorn board.
#
# Each boid steers away from close neighbours, matches their heading and drifts
# toward the local centre. A dim color trail shows where the flock has been.

import colorsys
import math
import random
import time

import _display

FRAME = 0.06


def hsv(hue):
    r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 1.0, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)


def main():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    count = max(6, width * height // 10)
    near = 9.0 if width >= 16 else 4.0

    boids = []
    for _ in range(count):
        boids.append([random.uniform(0, width), random.uniform(0, height),
                      random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6)])
    trail = [[(0.0, 0.0, 0.0) for _ in range(width)] for _ in range(height)]
    print("boids.py: %d boids on %dx%d" % (count, width, height))

    while True:
        for y in range(height):
            for x in range(width):
                r, g, b = trail[y][x]
                trail[y][x] = (r * 0.82, g * 0.82, b * 0.82)

        for i, boid in enumerate(boids):
            x, y, vx, vy = boid
            ax = ay = 0.0
            cx = cy = 0.0
            seen = 0
            for j, other in enumerate(boids):
                if i == j:
                    continue
                dx = other[0] - x
                dy = other[1] - y
                d2 = dx * dx + dy * dy
                if d2 < 1.0:
                    ax -= dx * 0.05
                    ay -= dy * 0.05
                elif d2 < near:
                    ax += other[2] * 0.02
                    ay += other[3] * 0.02
                    cx += other[0]
                    cy += other[1]
                    seen += 1
            if seen:
                ax += (cx / seen - x) * 0.004
                ay += (cy / seen - y) * 0.004

            ax += random.uniform(-0.02, 0.02)
            ay += random.uniform(-0.02, 0.02)
            vx += ax
            vy += ay
            speed = math.hypot(vx, vy)
            if speed < 0.35:
                vx *= 1.08
                vy *= 1.08
            elif speed > 0.9:
                vx *= 0.92
                vy *= 0.92

            x = (x + vx) % width
            y = (y + vy) % height
            boids[i] = [x, y, vx, vy]

            r, g, b = hsv(math.atan2(vy, vx) / math.tau)
            trail[int(y) % height][int(x) % width] = (r, g, b)

        unicornhat.clear()
        for y in range(height):
            for x in range(width):
                r, g, b = trail[y][x]
                if max(r, g, b) > 12:
                    unicornhat.set_pixel(x, y, int(r), int(g), int(b))
        unicornhat.show()
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
