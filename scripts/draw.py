# draw.py — renders a pixel design pushed from the control page.
#
# State (via /action=update&script=draw&pixels=<urlencoded JSON>):
#   pixels: [[x, y, "#RRGGBB"], ...]  → unicorn (RGB)
#           [[x, y], ...]             → microdot-phat (mono, on/off)
# An empty list clears the board. Polls revision, so sending a new pixels
# value with /action=update (no restart) redraws live.

import json
import sys
import time

import _xpi_state
import _display


def get_pixels():
    raw = _xpi_state.value("pixels")
    if raw is None and len(sys.argv) > 1:
        raw = sys.argv[1]
    if raw is None:
        return []
    try:
        data = json.loads(str(raw))
        return data if isinstance(data, list) else []
    except ValueError:
        print("draw.py: invalid pixels payload")
        return []


def run_unicorn(pixels):
    import unicornhat

    unicornhat.set_layout(unicornhat.AUTO)
    unicornhat.rotation(0)
    unicornhat.brightness(0.5)
    shape = unicornhat.get_shape()
    print("draw.py: unicorn drawing", len(pixels), "pixels, shape", shape)
    render(pixels, shape, unicornhat.show)
    current = _xpi_state.revision()

    while True:
        if _xpi_state.revision() != current:
            current = _xpi_state.revision()
            pixels = get_pixels()
            print("draw.py: new design,", len(pixels), "pixels")
            render(pixels, shape, unicornhat.show)
        time.sleep(0.5)


def render(pixels, shape, show):
    import unicornhat

    unicornhat.clear()
    w, h = shape
    for entry in pixels:
        x = y = None
        if isinstance(entry, (list, tuple)):
            if len(entry) == 2 and isinstance(entry[0], int):
                x, y = entry[0], entry[1]
            elif len(entry) >= 3:
                x, y = entry[0], entry[1]
                color = _display.parse_color(entry[2], (255, 255, 255))
        if x is None or not (0 <= x < w and 0 <= y < h):
            continue
        if len(entry) >= 3:
            r, g, b = color
            unicornhat.set_pixel(x, y, r, g, b)
        else:
            unicornhat.set_pixel(x, y, 255, 255, 255)
    show()


def run_microdot(pixels):
    import microdotphat

    print("draw.py: microdot-phat drawing", len(pixels), "pixels")
    draw(pixels, microdotphat.show)
    current = _xpi_state.revision()

    while True:
        if _xpi_state.revision() != current:
            current = _xpi_state.revision()
            pixels = get_pixels()
            print("draw.py: new design,", len(pixels), "pixels")
            draw(pixels, microdotphat.show)
        time.sleep(0.5)


def draw(pixels, show):
    """The microdot-phat is 45x7 monochrome; pixels outside are skipped."""
    microdotphat.fill(0)
    for entry in pixels:
        if isinstance(entry, (list, tuple)) and len(entry) >= 2 and \
                isinstance(entry[0], int) and isinstance(entry[1], int):
            if 0 <= entry[0] < 45 and 0 <= entry[1] < 7:
                microdotphat.set_pixel(entry[0], entry[1], 1)
    show()


def main():
    pixels = get_pixels()
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot(pixels)
    except Exception as exc:
        print("draw.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("draw.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn(pixels)


if __name__ == "__main__":
    main()
