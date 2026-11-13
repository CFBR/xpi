# pi-health.py — CPU temperature, load, memory, disk, uptime and throttle.
#
# state.json keys:
#   health_seconds  seconds per page on the Micro Dot, default 4
#   color           Unicorn color name or #RRGGBB
#
# The Micro Dot cycles one metric per page. The Unicorn scrolls a summary.
# Metrics come from /proc and /sys, plus vcgencmd when it is available.

import time

import _display
import _dot
import _health
import _xpi_state

DEFAULT_COLOR = (0, 255, 0)


def hold_seconds():
    try:
        return max(1.0, min(30.0, float(_xpi_state.value("health_seconds") or 4)))
    except (TypeError, ValueError):
        return 4.0


def temperature_text(metrics):
    value = metrics.get("temp_c")
    return "TEMP?" if value is None else "%.1fC" % value


def load_text(metrics):
    values = metrics.get("load") or [0, 0, 0]
    return "%.2f" % values[0]


def memory_text(metrics):
    return "M%d%%" % round(metrics.get("mem_pct") or 0)


def disk_text(metrics):
    return "D%d%%" % round(metrics.get("disk_pct") or 0)


def uptime_text(metrics):
    text = str(metrics.get("uptime_text") or "0m")
    return text.replace(" ", "").upper()[:6]


def throttle_text(metrics):
    now = (metrics.get("throttle") or {}).get("now") or []
    return "THR" if now else "OK"


def pages(metrics):
    return [
        temperature_text(metrics),
        load_text(metrics),
        memory_text(metrics),
        disk_text(metrics),
        uptime_text(metrics),
        throttle_text(metrics),
    ]


def summary(metrics):
    temp = metrics.get("temp_c")
    temp_text = "NA" if temp is None else "%.1fC" % temp
    return "TEMP %s LOAD %s MEM %d DISK %d UP %s %s" % (
        temp_text, load_text(metrics), round(metrics.get("mem_pct") or 0),
        round(metrics.get("disk_pct") or 0), uptime_text(metrics),
        throttle_text(metrics))


def run_microdot():
    import microdotphat

    print("pi-health.py: microdot-phat")
    while True:
        metrics = _health.metrics()
        for text in pages(metrics):
            microdotphat.clear()
            _dot.big_text(text)
            microdotphat.show()
            time.sleep(hold_seconds())


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    metrics = _health.metrics()
    grid = _display.text_bitmap(summary(metrics))
    offset = 0
    last = 0.0
    print("pi-health.py: unicorn", shape)

    while True:
        now = time.time()
        if now - last >= 10:
            metrics = _health.metrics()
            grid = _display.text_bitmap(summary(metrics))
            offset = 0
            last = now
            if (metrics.get("throttle") or {}).get("now"):
                color = (255, 64, 64)
            else:
                color = _display.parse_color(
                    _xpi_state.value("color"), DEFAULT_COLOR)
        _display.draw_unicorn(grid, offset, shape, color)
        offset += 1
        time.sleep(0.05)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("pi-health.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("pi-health.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
