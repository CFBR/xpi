# _xpi_clear.py — blank the attached display without starting a new process.
#
# The clear daemon imports this once and keeps the display libraries loaded, so
# a later switch does not pay the numpy startup cost again.

import sys


def clear(target=None):
    wanted = target or ""
    errors = []
    if wanted in ("", "microdot"):
        try:
            import microdotphat
            microdotphat.clear()
            microdotphat.show()
        except Exception as exc:
            errors.append("microdot: %s" % exc)
    if wanted in ("", "unicorn"):
        try:
            import unicornhat
            import _display
            shape, unicorn = _display.setup_unicorn()
            unicorn.clear()
            unicorn.show()
        except Exception as exc:
            errors.append("unicorn: %s" % exc)
    if errors and wanted:
        raise RuntimeError("; ".join(errors))
    return not errors
