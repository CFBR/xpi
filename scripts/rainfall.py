# rainfall.py — vertical raindrop streaks on the microdot-phat.
#
# Each drop is a short streak that falls a row at a time and respawns at the
# top. Density comes from state.json "density" (default 1.0) and the global
# speed control scales the frame delay. The Unicorn path gives the streak a
# dim tail.

import random
import time

import _display
import _xpi_state

WIDTH = 45
HEIGHT = 7
BASE_DROPS = 9
FRAME = 0.05
DEFAULT_COLOR = (0, 120, 255)


def density():
    try:
        return max(0.1, min(5.0, float(_xpi_state.value("density") or 1.0)))
    except (TypeError, ValueError):
        return 1.0


def new_drop(width, height):
    return [random.randrange(width), random.uniform(-height, 0),
            random.uniform(0.35, 0.9), random.randint(2, 3)]


def target_count():
    return max(1, int(round(BASE_DROPS * density())))


def run_microdot():
    import microdotphat

    width = getattr(microdotphat, "WIDTH", WIDTH)
    height = getattr(microdotphat, "HEIGHT", HEIGHT)
    drops = []
    print("rainfall.py: microdot-phat rain")

    while True:
        while len(drops) < target_count():
            drops.append(new_drop(width, height))
        microdotphat.clear()
        for drop in drops:
            drop[1] += drop[2]
            if drop[1] > height:
                drop[:] = new_drop(width, height)
            head = int(drop[1])
            for i in range(drop[3]):
                y = head - i
                if 0 <= y < height:
                    microdotphat.set_pixel(drop[0], y, 1)
        if len(drops) > target_count():
            del drops[target_count():]
        microdotphat.show()
        time.sleep(FRAME)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    width, height = shape
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    drops = []
    print("rainfall.py: unicorn rain")

    while True:
        while len(drops) < target_count():
            drops.append(new_drop(width, height))
        unicornhat.clear()
        r, g, b = color
        for drop in drops:
            drop[1] += drop[2]
            if drop[1] > height:
                drop[:] = new_drop(width, height)
            head = int(drop[1])
            for i in range(drop[3]):
                y = head - i
                if 0 <= y < height and 0 <= drop[0] < width:
                    level = max(0.15, 1.0 - i * 0.35)
                    unicornhat.set_pixel(drop[0], y, int(r * level),
                                         int(g * level), int(b * level))
        if len(drops) > target_count():
            del drops[target_count():]
        unicornhat.show()
        time.sleep(FRAME)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("rainfall.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("rainfall.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
