# clear_daemon.py — long lived clear helper for the supervisor.
#
# Reads "microdot", "unicorn", or "all" from stdin and replies OK or ERR.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for path in (os.path.join(ROOT, "scripts"),
             os.path.join(ROOT, "vendor", "microdot-phat"),
             os.path.join(ROOT, "vendor", "unicorn-hat")):
    if path not in sys.path:
        sys.path.insert(0, path)

import _xpi_clear


def main():
    for line in sys.stdin:
        target = line.strip()
        try:
            _xpi_clear.clear(None if target == "all" else target)
            print("OK", flush=True)
        except Exception as exc:
            print("ERR %s" % exc, flush=True)


if __name__ == "__main__":
    main()
