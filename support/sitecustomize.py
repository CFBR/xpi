# sitecustomize.py — imported automatically by every display script.
#
# Scales time.sleep by state.json "speed" so the speed control works for any
# script, including the Pimoroni examples. 1.0 is normal speed, 2.0 is twice
# as fast, 0.5 is half speed.

import json
import os
import time

STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state.json")

_original_sleep = time.sleep
_scale = 1.0
_mtime = None


def _current_scale():
    global _scale, _mtime
    try:
        mtime = os.path.getmtime(STATE_FILE)
    except OSError:
        return 1.0
    if mtime != _mtime:
        try:
            with open(STATE_FILE) as fh:
                value = float(json.load(fh).get("speed", 1.0))
        except (OSError, ValueError, TypeError):
            value = 1.0
        _mtime = mtime
        _scale = max(0.1, min(8.0, value))
    return _scale


def sleep(seconds):
    _original_sleep(seconds / _current_scale())


time.sleep = sleep
