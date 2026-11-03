# pomodoro.py — work and break phases with a countdown.
#
# Work and break lengths come from state.json "work" and "break" in minutes
# (default 25 and 5). The board shows MM:SS and switches color per phase:
# red for work, green for break. Restarting starts a work phase.

import time

import _display
import _xpi_state

WORK_COLOR = (255, 60, 60)
BREAK_COLOR = (60, 220, 120)


def minutes(key, default):
    try:
        return max(1, int(_xpi_state.value(key) or default))
    except (TypeError, ValueError):
        return default


def run_microdot():
    import microdotphat

    work = minutes("work", 25) * 60
    rest = minutes("break", 5) * 60
    phase, left = "work", work
    print("pomodoro.py: microdot-phat work", work, "break", rest)

    while True:
        text = "%02d:%02d" % (left // 60, left % 60)
        microdotphat.clear()
        microdotphat.write_string(text, kerning=False)
        microdotphat.show()
        time.sleep(1)
        left -= 1
        if left < 0:
            phase = "break" if phase == "work" else "work"
            left = rest if phase == "break" else work
            print("pomodoro.py: phase", phase)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    work = minutes("work", 25) * 60
    rest = minutes("break", 5) * 60
    phase, left = "work", work
    print("pomodoro.py: unicorn work", work, "break", rest)

    while True:
        color = WORK_COLOR if phase == "work" else BREAK_COLOR
        text = "%02d:%02d" % (left // 60, left % 60)
        grid = _display.text_bitmap(text)
        for frame in range(20):
            _display.draw_unicorn(grid, frame, shape, color)
            time.sleep(0.05)
        left -= 1
        if left < 0:
            phase = "break" if phase == "work" else "work"
            left = rest if phase == "break" else work
            print("pomodoro.py: phase", phase)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("pomodoro.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("pomodoro.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
