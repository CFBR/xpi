# melt.py: a message assembles from falling pixels, holds, then melts away.
#
# The text comes from state.json "message". Pixels fly in from below, settle
# into the 3x5 font, wait, then fall off the bottom of the board.

import random
import time

import _display
import _dot
import _xpi_state
import microdotphat

WIDTH = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
HEIGHT = getattr(microdotphat, "HEIGHT", 7)
FRAME = 0.06
HOLD = 30
GRAVITY = 0.055


def build_targets():
    text = str(_xpi_state.value("message", "MELT")).upper() or "MELT"
    grid = _display.text_bitmap(text[:WIDTH // _display.CHAR_W])
    x0 = max(0, (WIDTH - len(grid[0])) // 2)
    y0 = (HEIGHT - len(grid)) // 2
    targets = []
    for gy, row in enumerate(grid):
        for gx, value in enumerate(row):
            if value and y0 + gy < HEIGHT:
                targets.append((x0 + gx, y0 + gy))
    return targets


def draw_targets(targets):
    microdotphat.clear()
    for x, y in targets:
        microdotphat.set_pixel(_dot.buffer_x(x), y, 1)
    microdotphat.show()


def assemble(targets):
    particles = []
    for tx, ty in targets:
        if random.random() < 0.7:
            y = HEIGHT + random.uniform(0, 5)
        else:
            y = random.uniform(0, HEIGHT - 1)
        particles.append([random.uniform(0, WIDTH - 1), y, tx, ty])

    for _ in range(120):
        settled = True
        for p in particles:
            p[0] += (p[2] - p[0]) * 0.28
            p[1] += (p[3] - p[1]) * 0.28
            if abs(p[0] - p[2]) > 0.35 or abs(p[1] - p[3]) > 0.35:
                settled = False

        microdotphat.clear()
        for p in particles:
            px = int(round(p[0]))
            py = int(round(p[1]))
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                microdotphat.set_pixel(_dot.buffer_x(px), py, 1)
        microdotphat.show()
        time.sleep(FRAME)
        if settled:
            break

    draw_targets(targets)


def hold(targets):
    for _ in range(HOLD):
        draw_targets(targets)
        time.sleep(FRAME)


def melt(targets):
    particles = []
    for tx, ty in targets:
        particles.append([float(tx), float(ty),
                          random.uniform(-0.12, 0.12),
                          random.uniform(-0.06, 0.02)])

    for _ in range(180):
        alive = 0
        for p in particles:
            p[2] += random.uniform(-0.01, 0.01)
            p[3] += GRAVITY
            p[0] += p[2]
            p[1] += p[3]
            if p[1] < HEIGHT + 2:
                alive += 1

        microdotphat.clear()
        for p in particles:
            px = int(round(p[0]))
            py = int(round(p[1]))
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                microdotphat.set_pixel(_dot.buffer_x(px), py, 1)
        microdotphat.show()
        if not alive:
            break
        time.sleep(FRAME)


def main():
    print("melt.py: text melt")
    while True:
        targets = build_targets()
        if not targets:
            time.sleep(1)
            continue
        assemble(targets)
        hold(targets)
        melt(targets)
        time.sleep(0.4)


if __name__ == "__main__":
    main()
