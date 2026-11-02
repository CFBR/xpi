# message.py — microdot-phat scrolling text with live update.
#
# Text comes from state.json "message" (live), falling back to sys.argv[1],
# then "hi". Polls xpi_state.revision() each scroll frame so an
# /action=update&message=... call changes text without a restart.

import sys
import time

import microdotphat
import xpi_state


def get_message():
    text = xpi_state.value("message")
    if text is None and len(sys.argv) > 1:
        text = sys.argv[1]
    return str(text if text is not None else "hi")


text = get_message()
microdotphat.write_string(text)
print("message.py: displaying", text)

current_revision = xpi_state.revision()

while True:
    new_revision = xpi_state.revision()
    if new_revision != current_revision:
        current_revision = new_revision
        new_text = get_message()
        if new_text != text:
            text = new_text
            microdotphat.write_string(text)
            print("message.py: switched to", text)
    microdotphat.scroll()
    microdotphat.show()
    time.sleep(0.05)
