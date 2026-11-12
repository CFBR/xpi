# pong.py: an automatic Pong rally on the Micro Dot pHAT.
#
# Two paddles chase the ball with lag and a slowly changing error. The ball
# leaves a short trail. When a side misses, that side flashes, then serves
# again.

import random
import time

import _dot
import microdotphat

WIDTH = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
HEIGHT = getattr(microdotphat, "HEIGHT", 7)
PADDLE = 3
FRAME = 0.05
SPEED = 0.65
MAX_VY = 0.45


class Game:
    def __init__(self):
        self.left = (HEIGHT - PADDLE) / 2.0
        self.right = (HEIGHT - PADDLE) / 2.0
        self.left_err = 0.0
        self.right_err = 0.0
        self.flash = 0
        self.flash_left = False
        self.serve(1)

    def serve(self, direction):
        self.x = WIDTH / 2.0
        self.y = HEIGHT / 2.0
        self.vx = SPEED * direction
        self.vy = random.uniform(-0.25, 0.25)
        self.trail = []

    def move_paddle(self, pos, err, target):
        desired = target - PADDLE / 2.0 + err
        delta = max(-0.28, min(0.28, desired - pos))
        return max(0.0, min(HEIGHT - PADDLE, pos + delta))

    def step(self):
        if self.flash:
            self.flash -= 1
            return

        self.trail.append((self.x, self.y))
        if len(self.trail) > 3:
            self.trail.pop(0)

        self.left_err = max(-0.8, min(0.8, self.left_err + random.uniform(-0.08, 0.08)))
        self.right_err = max(-0.8, min(0.8, self.right_err + random.uniform(-0.08, 0.08)))
        self.left = self.move_paddle(self.left, self.left_err, self.y)
        self.right = self.move_paddle(self.right, self.right_err, self.y)

        self.x += self.vx
        self.y += self.vy

        if self.y < 0:
            self.y = 0
            self.vy = abs(self.vy)
        elif self.y > HEIGHT - 1:
            self.y = HEIGHT - 1
            self.vy = -abs(self.vy)

        if self.vx < 0 and self.x <= 1.0:
            if self.left <= self.y <= self.left + PADDLE - 1:
                self.x = 1.0
                self.vx = abs(self.vx)
                self.vy += (self.y - (self.left + PADDLE / 2.0)) * 0.22
                self.vy = max(-MAX_VY, min(MAX_VY, self.vy))
        elif self.vx > 0 and self.x >= WIDTH - 2.0:
            if self.right <= self.y <= self.right + PADDLE - 1:
                self.x = WIDTH - 2.0
                self.vx = -abs(self.vx)
                self.vy += (self.y - (self.right + PADDLE / 2.0)) * 0.22
                self.vy = max(-MAX_VY, min(MAX_VY, self.vy))

        if self.x < -1.0:
            self.flash = 8
            self.flash_left = True
            self.serve(1)
        elif self.x > WIDTH:
            self.flash = 8
            self.flash_left = False
            self.serve(-1)

    def draw(self):
        microdotphat.clear()
        if self.flash:
            start = 0 if self.flash_left else WIDTH - 3
            for y in range(HEIGHT):
                for x in range(start, start + 3):
                    microdotphat.set_pixel(_dot.buffer_x(x), y, 1)
        else:
            for y in range(int(round(self.left)), int(round(self.left)) + PADDLE):
                if 0 <= y < HEIGHT:
                    microdotphat.set_pixel(_dot.buffer_x(0), y, 1)
            for y in range(int(round(self.right)), int(round(self.right)) + PADDLE):
                if 0 <= y < HEIGHT:
                    microdotphat.set_pixel(_dot.buffer_x(WIDTH - 1), y, 1)
            for tx, ty in self.trail:
                px = int(round(tx))
                py = int(round(ty))
                if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                    microdotphat.set_pixel(_dot.buffer_x(px), py, 1)
            px = int(round(self.x))
            py = int(round(self.y))
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                microdotphat.set_pixel(_dot.buffer_x(px), py, 1)
        microdotphat.show()


def main():
    print("pong.py: automatic rally")
    game = Game()
    while True:
        game.step()
        game.draw()
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
