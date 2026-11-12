# maze.py: a maze runner on the Micro Dot pHAT.
#
# A depth-first maze is generated on the visible grid, solved with a breadth
# first search, then a dot runs the solution leaving a short trail. The maze
# flashes when the run finishes and a fresh one appears.

import random
import time
from collections import deque

import _dot
import microdotphat

WIDTH = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
HEIGHT = getattr(microdotphat, "HEIGHT", 7)
MAZE_W = WIDTH if WIDTH % 2 else WIDTH - 1
MAZE_H = HEIGHT if HEIGHT % 2 else HEIGHT - 1
FRAME = 0.10
TRAIL = 5

MOVES = ((0, -1), (1, 0), (0, 1), (-1, 0))


def generate(width, height):
    walls = [[1] * width for _ in range(height)]
    walls[1][1] = 0
    stack = [(1, 1)]

    while stack:
        x, y = stack[-1]
        options = []
        for dx, dy in ((0, -2), (2, 0), (0, 2), (-2, 0)):
            nx = x + dx
            ny = y + dy
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and walls[ny][nx]:
                options.append((nx, ny, x + dx // 2, y + dy // 2))
        if not options:
            stack.pop()
            continue
        nx, ny, wx, wy = random.choice(options)
        walls[wy][wx] = 0
        walls[ny][nx] = 0
        stack.append((nx, ny))
    return walls


def solve(walls, start, end):
    width = len(walls[0])
    height = len(walls)
    queue = deque([start])
    prev = {start: None}

    while queue:
        x, y = queue.popleft()
        if (x, y) == end:
            break
        for dx, dy in MOVES:
            nx = x + dx
            ny = y + dy
            if 0 <= nx < width and 0 <= ny < height \
                    and not walls[ny][nx] and (nx, ny) not in prev:
                prev[(nx, ny)] = (x, y)
                queue.append((nx, ny))

    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path if path and path[0] == start else []


def draw(walls, trail):
    microdotphat.clear()
    for y, row in enumerate(walls):
        for x, wall in enumerate(row):
            if wall:
                microdotphat.set_pixel(_dot.buffer_x(x), y, 1)
    for x, y in trail:
        microdotphat.set_pixel(_dot.buffer_x(x), y, 1)
    microdotphat.show()


def main():
    print("maze.py: maze runner")
    while True:
        walls = generate(MAZE_W, MAZE_H)
        path = solve(walls, (1, 1), (MAZE_W - 2, MAZE_H - 2))
        if not path:
            continue
        print("maze.py: %d step path" % len(path))

        trail = []
        for pos in path:
            trail.append(pos)
            if len(trail) > TRAIL:
                trail.pop(0)
            draw(walls, trail)
            time.sleep(FRAME)

        for _ in range(4):
            microdotphat.fill(1)
            microdotphat.show()
            time.sleep(0.12)
            microdotphat.clear()
            microdotphat.show()
            time.sleep(0.12)
        time.sleep(0.4)


if __name__ == "__main__":
    main()
