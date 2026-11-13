# _xpi_config.py — read non-secret settings and tokens from config.json.

import json
import os

from _xpi_state import ROOT

CONFIG_FILE = os.path.join(ROOT, "config.json")


def value(key, default=None):
    try:
        with open(CONFIG_FILE) as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return default
    if not isinstance(data, dict):
        return default
    return data.get(key, default)
