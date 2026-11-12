# ripple.py: interfering waves on the Micro Dot pHAT.
#
# Three sources drift around the board and send out sine ripples. The summed
# field is thresholded, so crossing fronts turn into bright interference lines
# and moving moire patterns.

import math
import time

import _dot
import microdotphat

WIDTH = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
HEIGHT = getattr(microdotphat, "HEIGHT", 7)
SOURCES = 3
FRAME = 0.06
THRESHOLD = 0.40


def main():
    print("ripple.py: wave interference")
    t = 0.0
    while True:
        sources = []
        for i in range(SOURCES):
            phase = i * 2.094
            sx = WIDTH / 2.0 + WIDTH * 0.33 * math.cos(t * 0.7 + phase)
            sy = HEIGHT / 2.0 + HEIGHT * 0.30 * math.sin(t * 1.1 + phase * 1.7)
            sources.append((sx, sy))

        microdotphat.clear()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                value = 0.0
                for sx, sy in sources:
                    d = math.hypot(x - sx, y - sy)
                    value += math.sin(d * 1.1 - t * 3.5) / (1.0 + d * 0.18)
                if value > THRESHOLD:
                    microdotphat.set_pixel(_dot.buffer_x(x), y, 1)
        microdotphat.show()

        t += 0.10
        time.sleep(FRAME)


if __name__ == "__main__":
    main()
