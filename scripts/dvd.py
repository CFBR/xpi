# dvd.py: the bouncing DVD logo on the Micro Dot pHAT.
#
# The logo drifts across the board and bounces off the edges. A corner hit sets
# off a short full-board flash. Long gaps between corners are the point.

import random
import time

import _display
import _dot
import microdotphat

WIDTH = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
HEIGHT = getattr(microdotphat, "HEIGHT", 7)
FRAME = 0.06


def draw(grid, x, y):
    for gy, row in enumerate(grid):
        for gx, value in enumerate(row):
            if value:
                microdotphat.set_pixel(_dot.buffer_x(x + gx), y + gy, 1)


def main():
    grid = _display.text_bitmap("DVD")
    logo_w = len(grid[0])
    logo_h = len(grid)
    x = random.uniform(0, WIDTH - logo_w)
    y = random.uniform(0, HEIGHT - logo_h)
    vx = random.choice((-0.45, 0.45))
    vy = random.choice((-0.25, 0.25))
    flash = 0
    print("dvd.py: bouncing logo")

    while True:
        x += vx
        y += vy
        hit_x = hit_y = False

        if x <= 0:
            x = 0.0
            vx = abs(vx)
            hit_x = True
        elif x >= WIDTH - logo_w:
            x = float(WIDTH - logo_w)
            vx = -abs(vx)
            hit_x = True
        if y <= 0:
            y = 0.0
            vy = abs(vy)
            hit_y = True
        elif y >= HEIGHT - logo_h:
            y = float(HEIGHT - logo_h)
            vy = -abs(vy)
            hit_y = True

        if hit_x and hit_y:
            flash = 10

        microdotphat.clear()
        if flash:
            flash -= 1
            if flash % 2:
                microdotphat.fill(1)
            else:
                draw(grid, int(round(x)), int(round(y)))
        else:
            draw(grid, int(round(x)), int(round(y)))
        microdotphat.show()
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
