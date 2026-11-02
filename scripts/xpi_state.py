# xpi_state.py — tiny helper shared by shipped display scripts.
#
# Server puts scripts/ on the child's PYTHONPATH, so `import xpi_state` works.
# Reads ROOT/state.json; missing or invalid file -> {}.

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(ROOT, "state.json")


def read_state():
    try:
        with open(STATE_FILE, "r") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def revision():
    return read_state().get("revision", 0)


def value(key, default=None):
    return read_state().get(key, default)
