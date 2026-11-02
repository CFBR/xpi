# timer.py — microdot-phat mm:ss countdown with live update.
#
# Seconds come from state.json "seconds", falling back to sys.argv[1],
# then 60. A /action=update bumps revision; only then is the countdown re-read.
# At 0:00 it blinks and holds (never exits, never shuts down).

import sys
import time

import microdotphat
import _xpi_state


def get_seconds():
    raw = _xpi_state.value("seconds")
    if raw is None and len(sys.argv) > 1:
        raw = sys.argv[1]
    try:
        return max(0, int(raw))
    except (TypeError, ValueError):
        return 60


def fmt(total):
    return "{}:{:02d}".format(total // 60, total % 60)


def set_show(text):
    microdotphat.write_string(text)
    microdotphat.show()


remaining = get_seconds()
set_show(fmt(remaining))
print("timer.py: counting down from", remaining)
last_shown = fmt(remaining)
handled_revision = _xpi_state.revision()

while True:
    rev = _xpi_state.revision()
    if rev != handled_revision:
        handled_revision = rev
        state = _xpi_state.read_state()
        if state.get("seconds") is not None:
            remaining = max(0, int(state["seconds"]))
            last_shown = fmt(remaining)
            set_show(last_shown)
            print("timer.py: reset countdown to", remaining)
    if remaining > 0:
        remaining -= 1
    now_shown = fmt(remaining) if (remaining > 0 or int(time.time()) % 2 == 0) else ""
    if now_shown != last_shown:
        last_shown = now_shown
        set_show(now_shown)
    time.sleep(1)
