# _health.py — local system metrics for pi-health and the health endpoint.

import os
import subprocess


def _read(path):
    try:
        with open(path) as fh:
            return fh.read().strip()
    except OSError:
        return ""


def temperature():
    raw = _read("/sys/class/thermal/thermal_zone0/temp")
    try:
        return round(int(raw) / 1000.0, 1)
    except ValueError:
        pass
    try:
        out = subprocess.run(["vcgencmd", "measure_temp"], timeout=1,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             text=True).stdout
        return round(float(out.split("=")[1].split("'")[0]), 1)
    except (OSError, IndexError, ValueError, subprocess.SubprocessError):
        return None


def memory():
    values = {}
    for line in _read("/proc/meminfo").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            values[parts[0].rstrip(":")] = int(parts[1])
    total = values.get("MemTotal", 0)
    free = values.get("MemAvailable", values.get("MemFree", 0))
    used = max(0, total - free)
    pct = round(used * 100.0 / total, 1) if total else 0.0
    return total * 1024, used * 1024, pct


def disk():
    try:
        stat = os.statvfs("/")
    except OSError:
        return 0, 0, 0.0
    total = stat.f_blocks * stat.f_frsize
    free = stat.f_bavail * stat.f_frsize
    used = max(0, total - free)
    pct = round(used * 100.0 / total, 1) if total else 0.0
    return total, used, pct


def uptime():
    try:
        return int(float(_read("/proc/uptime").split()[0]))
    except (IndexError, ValueError):
        return 0


def load():
    try:
        return [round(value, 2) for value in os.getloadavg()]
    except OSError:
        return [0.0, 0.0, 0.0]


THROTTLE_BITS = {
    0: "under-voltage",
    1: "arm-frequency-capped",
    2: "throttled",
    3: "soft-temperature-limit",
    16: "under-voltage-occurred",
    17: "arm-frequency-capped-occurred",
    18: "throttled-occurred",
    19: "soft-temperature-limit-occurred",
}


def throttle():
    try:
        out = subprocess.run(["vcgencmd", "get_throttled"], timeout=1,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             text=True).stdout.strip()
        raw = out.split("=", 1)[1]
        value = int(raw, 16)
    except (OSError, IndexError, ValueError, subprocess.SubprocessError):
        return {"raw": None, "now": [], "occurred": []}
    now = [name for bit, name in THROTTLE_BITS.items()
           if bit < 16 and value & (1 << bit)]
    occurred = [name for bit, name in THROTTLE_BITS.items()
                if bit >= 16 and value & (1 << bit)]
    return {"raw": raw, "now": now, "occurred": occurred}


def format_uptime(seconds):
    seconds = max(0, int(seconds))
    days, rest = divmod(seconds, 86400)
    hours, rest = divmod(rest, 3600)
    minutes = rest // 60
    if days:
        return "%dd %dh" % (days, hours)
    if hours:
        return "%dh %dm" % (hours, minutes)
    return "%dm" % minutes


def metrics():
    mem_total, mem_used, mem_pct = memory()
    disk_total, disk_used, disk_pct = disk()
    up = uptime()
    return {
        "temp_c": temperature(),
        "load": load(),
        "mem_total": mem_total,
        "mem_used": mem_used,
        "mem_pct": mem_pct,
        "disk_total": disk_total,
        "disk_used": disk_used,
        "disk_pct": disk_pct,
        "uptime": up,
        "uptime_text": format_uptime(up),
        "throttle": throttle(),
    }
