# clear.py — clears whichever board answers, then exits.
# microdot-phat first, then unicorn-hat; used by server /action=clear.

import sys

try:
    import microdotphat
    microdotphat.fill(0)
    microdotphat.show()
    print("clear.py: microdot-phat cleared")
except Exception as exc:
    print("clear.py: no microdot-phat:", exc)

try:
    import unicornhat
    unicornhat.clear()
    unicornhat.show()
    print("clear.py: unicorn-hat cleared")
except Exception as exc:
    print("clear.py: no unicorn-hat:", exc)

sys.exit(0)
