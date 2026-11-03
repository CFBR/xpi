# stats.py — this Pi's temperature, load and free memory, scrolling.
#
# Reads /sys/class/thermal, os.getloadavg() and /proc/meminfo, so it needs no
# hardware and works on either board. Refreshes every few seconds.

import os
import time

import _display
import _xpi_state

DEFAULT_COLOR = (0, 255, 255)
REFRESH = 5


def temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as fh:
            return int(fh.read().strip()) / 1000.0
    except (OSError, ValueError):
        return None


def available_mb():
    try:
        with open("/proc/meminfo") as fh:
            for line in fh:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) // 1024
    except (OSError, ValueError):
        pass
    return None


def get_text():
    parts = []
    temp = temperature()
    if temp is not None:
        parts.append("CPU %dC" % round(temp))
    parts.append("LOAD %.2f" % os.getloadavg()[0])
    free = available_mb()
    if free is not None:
        parts.append("MEM %dM" % free)
    return "  ".join(parts)


def run_microdot():
    import microdotphat

    print("stats.py: microdot-phat system stats")
    text = get_text()
    microdotphat.write_string(text)
    microdotphat.show()
    last = time.time()

    while True:
        if time.time() - last >= REFRESH:
            last = time.time()
            new_text = get_text()
            if new_text != text:
                text = new_text
                microdotphat.write_string(text)
                print("stats.py:", text)
        microdotphat.scroll()
        microdotphat.show()
        time.sleep(0.05)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    text = get_text()
    grid = _display.text_bitmap(text)
    offset = 0
    last = time.time()
    last_revision = _xpi_state.revision()
    print("stats.py: unicorn system stats")

    while True:
        if time.time() - last >= REFRESH:
            last = time.time()
            new_text = get_text()
            if new_text != text:
                text = new_text
                grid = _display.text_bitmap(text)
                offset = 0
                print("stats.py:", text)
        new_revision = _xpi_state.revision()
        if new_revision != last_revision:
            last_revision = new_revision
            color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
        _display.draw_unicorn(grid, offset, shape, color)
        offset += 1
        time.sleep(0.05)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("stats.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("stats.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
