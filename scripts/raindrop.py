# raindrop.py — random pixels appear, then fade away.
#
# On the microdot-phat the fade is done by flicker: a drop is drawn with a
# chance equal to its remaining life, so it thins out instead of vanishing.
# On a Unicorn board the pixel dims with its life. The global speed control
# scales the frame delay.

import random
import time

import _display
import _xpi_state

WIDTH = 45
HEIGHT = 7
SPAWN = 3
DECAY = 0.06
FRAME = 0.08
DEFAULT_COLOR = (0, 120, 255)


def spawn(drops, width, height):
    for _ in range(SPAWN):
        drops.append([random.randrange(width), random.randrange(height), 1.0])
    return drops


def run_microdot():
    import microdotphat

    width = getattr(microdotphat, "WIDTH", WIDTH)
    height = getattr(microdotphat, "HEIGHT", HEIGHT)
    drops = []
    print("raindrop.py: microdot-phat drops")

    while True:
        spawn(drops, width, height)
        microdotphat.clear()
        alive = []
        for x, y, life in drops:
            life -= DECAY
            if life <= 0:
                continue
            if random.random() < life:
                microdotphat.set_pixel(x, y, 1)
            alive.append([x, y, life])
        drops = alive
        microdotphat.show()
        time.sleep(FRAME)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    drops = []
    print("raindrop.py: unicorn drops")

    while True:
        spawn(drops, width, height)
        unicornhat.clear()
        r, g, b = color
        alive = []
        for x, y, life in drops:
            life -= DECAY
            if life <= 0:
                continue
            if x < width and y < height:
                unicornhat.set_pixel(x, y, int(r * life), int(g * life),
                                     int(b * life))
            alive.append([x, y, life])
        drops = alive
        unicornhat.show()
        time.sleep(FRAME)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("raindrop.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("raindrop.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
