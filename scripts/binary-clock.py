# binary-clock.py — BCD time and date on the six Micro Dot matrices.
#
# Each matrix is one decimal digit. The four rows from top to bottom are the
# bits 8, 4, 2, 1, so a digit is the sum of the lit rows.
#
# State:
#   binary_mode     time, date, or both (default both)
#   binary_seconds  seconds per page, default 5

import time

import _dot
import _xpi_state


def seconds():
    try:
        return max(1.0, min(30.0, float(_xpi_state.value("binary_seconds") or 5)))
    except (TypeError, ValueError):
        return 5.0


def mode():
    value = str(_xpi_state.value("binary_mode") or "both").strip().lower()
    return value if value in ("time", "date", "both") else "both"


def bits(digit):
    return [(digit >> shift) & 1 for shift in (3, 2, 1, 0)]


def draw_digits(text):
    import microdotphat

    microdotphat.clear()
    for index, char in enumerate(text[:6]):
        if not char.isdigit():
            continue
        x0 = index * _dot.MATRIX
        for bit_index, bit in enumerate(bits(int(char))):
            if not bit:
                continue
            y = 1 + bit_index
            for dx in (1, 2, 3):
                microdotphat.set_pixel(_dot.buffer_x(x0 + dx), y, 1)
    microdotphat.show()


def show_time(seconds_to_show):
    end = time.time() + seconds_to_show
    while time.time() < end:
        draw_digits(time.strftime("%H%M%S"))
        time.sleep(1)


def show_date(seconds_to_show):
    draw_digits(time.strftime("%y%m%d"))
    time.sleep(seconds_to_show)


def main():
    import microdotphat

    if not microdotphat.is_connected():
        print("binary-clock.py: no microdot-phat")
        return
    print("binary-clock.py: microdot-phat, mode", mode())
    while True:
        current = mode()
        if current in ("time", "both"):
            show_time(seconds())
        if current in ("date", "both"):
            show_date(seconds())


if __name__ == "__main__":
    main()
