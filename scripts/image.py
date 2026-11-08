# image.py — draws an image file, or a folder of them, on a Unicorn board.
#
# Usage, from the page or the API:
#   ?action=switch&script=image&arg=/opt/xpi/images/logo.png
#   ?action=switch&script=image&arg=/opt/xpi/images
#
# Images are scaled to the display height with the aspect ratio kept. One that
# fits is centred. One that is wider scrolls, right to left, with blank columns
# between repeats. Animated GIF and WebP files play their frames.
#
# A single file is drawn once and redrawn when the file changes on disk, so you
# can replace it through the page without restarting the script. Wide and
# animated files repeat instead of watching, since there is nothing to see
# between frames.
#
# A folder cycles its images in filename order, holding each for a moment.
#
# Needs Pillow. install.sh installs python3-pil, so the Pi has it.

import glob
import os
import sys
import time

import _display

try:
    from PIL import Image
except ImportError:
    Image = None

EXTENSIONS = (".png", ".gif", ".jpg", ".jpeg", ".bmp", ".webp")
SCROLL_DELAY = 0.06     # seconds per column, scaled by state.json "speed"
HOLD_SECONDS = 3.0      # how long a folder image stays before the next
POLL_SECONDS = 1.0      # how often a single file's mtime is checked
DEFAULT_FRAME_MS = 100  # frame delay for an animation that declares none
BACKGROUND = (0, 0, 0)


def image_files(path):
    """A folder gives its images in filename order, a file gives just itself."""
    if os.path.isdir(path):
        return sorted(
            entry for entry in glob.glob(os.path.join(path, "*"))
            if entry.lower().endswith(EXTENSIONS))
    if os.path.isfile(path):
        return [path]
    return []


def frame_delay(opened):
    """Seconds between frames of an animation."""
    try:
        milliseconds = float(opened.info.get("duration") or DEFAULT_FRAME_MS)
    except (TypeError, ValueError):
        milliseconds = DEFAULT_FRAME_MS
    return max(0.02, milliseconds / 1000.0)


def scale(opened, shape):
    """Scale an open PIL image to the display height, keeping the aspect."""
    height = shape[1]
    source_w, source_h = opened.size
    if source_w < 1 or source_h < 1:
        return None
    rgb = opened.convert("RGB")
    target_w = max(1, int(round(source_w * (height / source_h))))
    # small images are usually pixel art, so keep their pixels crisp
    resample = Image.NEAREST if source_h <= height else Image.LANCZOS
    return rgb.resize((target_w, height), resample)


def frames(opened, shape):
    """Every frame of an open image, scaled. One entry for a still image."""
    pictures = []
    for index in range(getattr(opened, "n_frames", 1)):
        opened.seek(index)
        picture = scale(opened, shape)
        if picture is not None:
            pictures.append(picture)
    return pictures


def open_frames(path, shape):
    """Frames of a file, plus the delay between them. Empty on failure."""
    try:
        opened = Image.open(path)
    except OSError as exc:
        print("image.py: cannot read %s: %s" % (path, exc))
        return [], 0
    pictures = frames(opened, shape)
    if not pictures:
        print("image.py: no pixels in %s" % path)
        return [], 0
    return pictures, frame_delay(opened)


def paint(canvas, unicornhat):
    """Send a display sized PIL image to the board."""
    data = canvas.load()
    width, height = canvas.size
    unicornhat.clear()
    for y in range(height):
        for x in range(width):
            r, g, b = data[x, y][:3]
            unicornhat.set_pixel(x, y, r, g, b)
    unicornhat.show()


def still(picture, shape, unicornhat):
    """Centre an image that fits and show it."""
    width = shape[0]
    canvas = Image.new("RGB", shape, BACKGROUND)
    canvas.paste(picture, ((width - picture.size[0]) // 2, 0))
    paint(canvas, unicornhat)


def scroll(picture, shape, unicornhat, repeat):
    """Slide a wide image across the display, right to left."""
    width = shape[0]
    gap = width                       # blank columns between repeats
    while True:
        for offset in range(width, -(picture.size[0] + gap), -1):
            canvas = Image.new("RGB", shape, BACKGROUND)
            canvas.paste(picture, (offset, 0))
            paint(canvas, unicornhat)
            time.sleep(SCROLL_DELAY)
        if not repeat:
            return


def draw(picture, shape, unicornhat):
    """Centre a picture that fits, scroll one that is wider."""
    if picture.size[0] > shape[0]:
        scroll(picture, shape, unicornhat, repeat=False)
    else:
        still(picture, shape, unicornhat)


def mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def single(path, shape, unicornhat):
    """Draw one file, then follow it while it is on screen.

    Returns False when the file could not be read. Does not return for a wide
    or animated file, which repeats forever.
    """
    pictures, delay = open_frames(path, shape)
    if not pictures:
        return False
    if len(pictures) > 1:
        while True:
            for picture in pictures:
                draw(picture, shape, unicornhat)
                time.sleep(delay)
    picture = pictures[0]
    if picture.size[0] > shape[0]:
        scroll(picture, shape, unicornhat, repeat=True)
    still(picture, shape, unicornhat)

    seen = mtime(path)
    while True:
        time.sleep(POLL_SECONDS)
        current = mtime(path)
        if current is not None and current != seen:
            seen = current
            pictures, delay = open_frames(path, shape)
            if pictures:
                draw(pictures[0], shape, unicornhat)


def folder(paths, shape, unicornhat):
    """Cycle a folder's images until the server stops the script."""
    while True:
        for path in paths:
            pictures, delay = open_frames(path, shape)
            for picture in pictures:
                draw(picture, shape, unicornhat)
                if len(pictures) > 1:
                    time.sleep(delay)
            time.sleep(HOLD_SECONDS)


def main():
    if Image is None:
        print("image.py: needs Pillow, install with: sudo apt install python3-pil")
        return 1
    if len(sys.argv) < 2:
        print("image.py: give an image file or a folder as the first argument")
        print("  ?action=switch&script=image&arg=/opt/xpi/images/logo.png")
        return 2
    target = sys.argv[1]
    paths = image_files(target)
    if not paths:
        print("image.py: no images at %s" % target)
        return 1

    try:
        shape, unicornhat = _display.setup_unicorn()
    except Exception as exc:
        print("image.py: no unicorn-hat:", exc)
        return 1

    print("image.py: %d image(s) at %s on a %dx%d display"
          % (len(paths), target, shape[0], shape[1]))
    if len(paths) > 1:
        folder(paths, shape, unicornhat)
        return 0
    return 0 if single(paths[0], shape, unicornhat) else 1


if __name__ == "__main__":
    sys.exit(main())
