# sonar.py: a radar sweep on the Micro Dot pHAT.
#
# A beam sweeps around an ellipse while echoes appear and fade. The board is
# wide, so the scope uses an elliptical range that fills all 30 visible
# columns.

import math
import random
import time

import _dot
import microdotphat

WIDTH = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
HEIGHT = getattr(microdotphat, "HEIGHT", 7)
FRAME = 0.07
CX = (WIDTH - 1) / 2.0
CY = (HEIGHT - 1) / 2.0
RX = WIDTH / 2.0
RY = HEIGHT / 2.0
SWEEP = 0.20
BLIP_CHANCE = 0.05


def beam(angle):
    for i in range(40):
        f = i / 39.0
        x = CX + RX * f * math.cos(angle)
        y = CY + RY * f * math.sin(angle)
        px = int(round(x))
        py = int(round(y))
        if 0 <= px < WIDTH and 0 <= py < HEIGHT:
            microdotphat.set_pixel(_dot.buffer_x(px), py, 1)


def main():
    print("sonar.py: radar sweep")
    angle = 0.0
    blips = []

    while True:
        angle += SWEEP
        if random.random() < BLIP_CHANCE:
            a = random.uniform(0.0, math.tau)
            f = random.uniform(0.35, 1.0)
            blips.append([CX + RX * f * math.cos(a),
                          CY + RY * f * math.sin(a),
                          1.0])

        microdotphat.clear()
        beam(angle)
        beam(angle - 0.18)
        beam(angle - 0.36)

        alive = []
        for blip in blips:
            blip[2] -= 0.012
            if blip[2] <= 0:
                continue
            px = int(round(blip[0]))
            py = int(round(blip[1]))
            if 0 <= px < WIDTH and 0 <= py < HEIGHT \
                    and (blip[2] > 0.45 or random.random() < blip[2]):
                microdotphat.set_pixel(_dot.buffer_x(px), py, 1)
            alive.append(blip)
        blips = alive

        microdotphat.show()
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
