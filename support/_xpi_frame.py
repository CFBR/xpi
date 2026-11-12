# _xpi_frame.py — publishes the last shown frame for the page's live viewer.
#
# The vendored display libraries call publish_microdot() or publish_unicorn()
# from show(). Writes are throttled and atomic, so a slow or stopped script
# leaves the last frame in place for /action=frame to serve.

import base64
import json
import os
import tempfile
import threading
import time

FRAME_FILE = os.path.join(tempfile.gettempdir(), "xpi-frame.json")
MIN_INTERVAL = 0.20
STATIC_REPEAT = 2.0

_lock = threading.Lock()
_last_write = 0.0
_last_attempt = 0.0
_last_key = None


def due():
    """True at most once per MIN_INTERVAL, so show() can skip the copy."""
    global _last_attempt
    now = time.monotonic()
    with _lock:
        if now - _last_attempt < MIN_INTERVAL:
            return False
        _last_attempt = now
        return True


def _write(payload):
    global _last_write, _last_key
    now = time.monotonic()
    key = (payload.get("board"), payload.get("rows"), payload.get("data"))
    with _lock:
        if key == _last_key and now - _last_write < STATIC_REPEAT:
            return
        if now - _last_write < MIN_INTERVAL:
            return
        _last_write = now
        _last_key = key
        payload["ts"] = time.time()
        tmp = "%s.%d.tmp" % (FRAME_FILE, os.getpid())
        try:
            with open(tmp, "w") as fh:
                json.dump(payload, fh, separators=(",", ":"))
            os.replace(tmp, FRAME_FILE)
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def publish_microdot(buffer):
    """Publish the 30 visible columns of a scrolled microdot buffer."""
    rows = []
    for y in range(7):
        row = []
        for matrix in range(6):
            for x in range(5):
                buffer_x = matrix * 8 + x
                try:
                    lit = bool(buffer[y][buffer_x])
                except (IndexError, TypeError):
                    lit = False
                row.append("1" if lit else "0")
        rows.append("".join(row))
    _write({"board": "microdot-phat", "width": 30, "height": 7,
            "mono": True, "rows": rows})


def publish_unicorn(shape, pixels):
    width, height = shape
    raw = bytearray()
    for y in range(height):
        for x in range(width):
            try:
                r, g, b = pixels[y][x]
            except (IndexError, TypeError):
                r = g = b = 0
            raw.extend((int(r) & 255, int(g) & 255, int(b) & 255))
    board = "unicorn-hat" if width >= 16 else "unicorn-phat"
    _write({"board": board, "width": width, "height": height,
            "mono": False,
            "data": base64.b64encode(bytes(raw)).decode("ascii")})
