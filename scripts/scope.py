# scope.py: an oscilloscope on the Micro Dot pHAT.
#
# A beam draws Lissajous figures, a spiral, a travelling wave and a rotating
# square. Each pixel keeps a fading glow, so the beam leaves a phosphor trail.

import math
import time

import _dot
import microdotphat

WIDTH = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
HEIGHT = getattr(microdotphat, "HEIGHT", 7)
FRAME = 0.05
DECAY = 0.82
SHAPE_FRAMES = 160
CX = (WIDTH - 1) / 2.0
CY = (HEIGHT - 1) / 2.0


def points(shape, t):
    result = []
    if shape == 0:
        for i in range(90):
            a = i / 90.0 * math.tau
            result.append((CX + 13.5 * math.sin(3 * a + t * 1.2),
                           CY + 2.7 * math.sin(2 * a + t * 0.8)))
    elif shape == 1:
        for i in range(90):
            a = i / 90.0 * 6.0 * math.tau + t
            r = i / 90.0
            result.append((CX + 13.5 * r * math.cos(a),
                           CY + 2.7 * r * math.sin(a)))
    elif shape == 2:
        for x in range(WIDTH):
            result.append((x, CY + 2.6 * math.sin(x * 0.42 + t * 3.0)))
    else:
        for i in range(90):
            a = i / 90.0 * math.tau + t
            dx = math.cos(a)
            dy = math.sin(a)
            span = max(abs(dx), abs(dy), 1e-6)
            result.append((CX + 13.5 * dx / span,
                           CY + 2.7 * dy / span))
    return result


def main():
    print("scope.py: vector scope")
    glow = [[0.0] * WIDTH for _ in range(HEIGHT)]
    frame = 0

    while True:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                glow[y][x] *= DECAY

        t = frame * 0.09
        shape = (frame // SHAPE_FRAMES) % 4
        for x, y in points(shape, t):
            px = int(round(x))
            py = int(round(y))
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                glow[py][px] = 1.0

        microdotphat.clear()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if glow[y][x] > 0.3:
                    microdotphat.set_pixel(_dot.buffer_x(x), y, 1)
        microdotphat.show()

        frame += 1
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
