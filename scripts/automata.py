# automata.py: a cellular automata sampler on the Micro Dot pHAT.
#
# Life, HighLife, Seeds and Brian's Brain take turns. Each rule starts from a
# random soup and reseeds when it dies out or stops changing.

import random
import time

import _dot
import microdotphat

WIDTH = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
HEIGHT = getattr(microdotphat, "HEIGHT", 7)
FRAME = 0.10
MODE_FRAMES = 300
NEIGHBOURS = ((0, -1), (1, -1), (1, 0), (1, 1),
              (0, 1), (-1, 1), (-1, 0), (-1, -1))

RULES = [
    ("life", {3}, {2, 3}),
    ("highlife", {3, 6}, {2, 3}),
    ("seeds", {2}, set()),
    ("brian", None, None),
]


def random_grid():
    return [[1 if random.random() < 0.35 else 0 for _ in range(WIDTH)]
            for _ in range(HEIGHT)]


def neighbours(grid, x, y):
    count = 0
    for dx, dy in NEIGHBOURS:
        if grid[(y + dy) % HEIGHT][(x + dx) % WIDTH] == 1:
            count += 1
    return count


def step_life(grid, birth, survive):
    new = [[0] * WIDTH for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            count = neighbours(grid, x, y)
            if grid[y][x]:
                new[y][x] = 1 if count in survive else 0
            else:
                new[y][x] = 1 if count in birth else 0
    return new


def step_brian(grid):
    new = [[0] * WIDTH for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] == 1:
                new[y][x] = 2
            elif grid[y][x] == 2:
                new[y][x] = 0
            else:
                new[y][x] = 1 if neighbours(grid, x, y) == 2 else 0
    return new


def alive(grid):
    return sum(row.count(1) for row in grid)


def main():
    print("automata.py: cellular automata")
    mode = 0
    grid = random_grid()
    mode_frame = 0
    still = 0

    while True:
        if mode_frame >= MODE_FRAMES:
            mode = (mode + 1) % len(RULES)
            grid = random_grid()
            mode_frame = 0
            still = 0
            print("automata.py:", RULES[mode][0])

        name, birth, survive = RULES[mode]
        if name == "brian":
            new = step_brian(grid)
        else:
            new = step_life(grid, birth, survive)

        still = still + 1 if new == grid else 0
        grid = new
        if still > 2 or alive(grid) < 3:
            grid = random_grid()
            still = 0

        microdotphat.clear()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if grid[y][x] == 1:
                    microdotphat.set_pixel(_dot.buffer_x(x), y, 1)
        microdotphat.show()

        mode_frame += 1
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
