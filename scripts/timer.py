# timer.py — microdot-phat mm:ss countdown with live update.
#
# Seconds come from state.json "seconds", falling back to sys.argv[1],
# then 60. Refreshes the display once per second; at 0:00 it blinks and
# holds (never exits, never shuts down).

import sys
import time

import microdotphat
import xpi_state


def get_seconds():
    raw = xpi_state.value("seconds")
    if raw is None and len(sys.argv) > 1:
        raw = sys.argv[1]
    try:
        return max(0, int(raw))
    except (TypeError, ValueError):
        return 60


def fmt(total):
    return "{}:{:02d}".format(total // 60, total % 60)


remaining = get_seconds()
microdotphat.write_string(fmt(remaining))
microdotphat.show()
print("timer.py: counting down from", remaining)

last_shown = None

while True:
    state = xpi_state.read_state()
    if state.get("seconds") is not None and int(state["seconds"]) != remaining:
        remaining = get_seconds()
        microdotphat.write_string(fmt(remaining))
        microdotphat.show()
        print("timer.py: restarted countdown at", remaining)
    if remaining > 0:
        remaining -= 1
    now_shown = fmt(remaining) if (remaining > 0 or int(time.time()) % 2 == 0) else ""
    if now_shown != last_shown:
        last_shown = now_shown
        microdotphat.write_string(now_shown)
        microdotphat.show()
    time.sleep(1)
