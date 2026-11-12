# fireworks.py: rockets and bursts on either board.
#
# Rockets climb from the bottom, explode into sparks, and the sparks fall
# under gravity. The Micro Dot pHAT gets a mono flicker; Unicorn boards get
# colored bursts.

import math
import random
import time

import _dot

FRAME = 0.05
GRAVITY = 0.07
ROCKET_CHANCE = 0.05
MAX_ROCKETS = 3

COLORS = [
    (255, 80, 20), (255, 200, 40), (80, 200, 255),
    (255, 60, 200), (120, 255, 120), (255, 255, 255),
]


def new_rocket(width, height):
    return [random.randrange(width), float(height - 1),
            random.uniform(-0.15, 0.15), -random.uniform(0.55, 0.95),
            random.uniform(1.0, height * 0.6), random.choice(COLORS)]


def burst(x, y, count):
    sparks = []
    for _ in range(count):
        angle = random.uniform(0.0, math.tau)
        speed = random.uniform(0.15, 0.75)
        sparks.append([x, y, speed * math.cos(angle), speed * math.sin(angle),
                       1.0, random.choice(COLORS)])
    return sparks


def make_draw(width, height, colored, board):
    if colored:
        def draw(x, y, life, color):
            px = int(x)
            py = int(y)
            if 0 <= px < width and 0 <= py < height:
                fade = max(0.0, min(1.0, life))
                r, g, b = color
                board.set_pixel(px, py, int(r * fade), int(g * fade), int(b * fade))
    else:
        def draw(x, y, life, color):
            px = int(x)
            py = int(y)
            if 0 <= px < width and 0 <= py < height:
                board.set_pixel(_dot.buffer_x(px), py, 1)
    return draw


def run(width, height, colored, board):
    draw = make_draw(width, height, colored, board)
    rockets = []
    sparks = []
    print("fireworks.py: %s on %dx%d"
          % ("color" if colored else "mono", width, height))

    while True:
        if len(rockets) < MAX_ROCKETS and random.random() < ROCKET_CHANCE:
            rockets.append(new_rocket(width, height))

        for rocket in rockets[:]:
            rocket[0] += rocket[2]
            rocket[1] += rocket[3]
            sparks.append([rocket[0], rocket[1], 0.0, 0.0, 0.35, rocket[5]])
            if rocket[1] <= rocket[4]:
                rockets.remove(rocket)
                sparks.extend(burst(rocket[0], rocket[1],
                                    24 if colored else 14))

        alive = []
        for spark in sparks:
            spark[0] += spark[2]
            spark[1] += spark[3]
            spark[3] += GRAVITY
            spark[4] -= 0.022
            if spark[4] > 0 and spark[1] <= height + 2:
                alive.append(spark)
        sparks = alive

        board.clear()
        for rocket in rockets:
            draw(rocket[0], rocket[1], 1.0, rocket[5])
        for spark in sparks:
            if colored or spark[4] > 0.12 or random.random() < spark[4]:
                draw(spark[0], spark[1], spark[4], spark[5])
        board.show()
        time.sleep(FRAME)


def run_microdot():
    import microdotphat

    width = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
    height = getattr(microdotphat, "HEIGHT", 7)
    return run(width, height, False, microdotphat)


def run_unicorn():
    import _display

    shape, unicornhat = _display.setup_unicorn()
    return run(shape[0], shape[1], True, unicornhat)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("fireworks.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("fireworks.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
