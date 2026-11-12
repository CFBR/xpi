# ntfy.py: subscribe to an ntfy topic and show alerts.
#
# The ntfy server, topic and optional token come from config.json "ntfy".
# A background thread keeps the stream open and queues messages while the
# main loop scrolls them. After the last alert the display returns to a clock.
#
# ntfy URL format: a base such as https://ntfy.sh, plus a topic name. The
# script subscribes to <base>/<topic>/json and reconnects on errors.

import json
import os
import queue
import threading
import time
import urllib.parse
import urllib.request

import _display
import _xpi_state

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(ROOT, "config.json")
DEFAULT_URL = "https://ntfy.sh"
DEFAULT_HOLD = 20
DEFAULT_COLOR = (0, 255, 255)


def ntfy_config():
    try:
        with open(CONFIG_FILE) as fh:
            config = json.load(fh)
    except (OSError, ValueError):
        config = {}
    ntfy = config.get("ntfy") or {}
    url = str(ntfy.get("url") or DEFAULT_URL).rstrip("/")
    topic = str(ntfy.get("topic") or "").strip()
    token = str(ntfy.get("token") or "").strip()
    return url, topic, token


def hold_seconds():
    try:
        return max(3.0, float(_xpi_state.value("ntfy_hold") or DEFAULT_HOLD))
    except (TypeError, ValueError):
        return float(DEFAULT_HOLD)


def text_speed():
    try:
        return max(0.1, min(8.0, float(_xpi_state.value("text_speed") or 1)))
    except (TypeError, ValueError):
        return 1.0


def listen(url, topic, token, messages):
    endpoint = "%s/%s/json" % (url.rstrip("/"), urllib.parse.quote(topic))
    headers = {"User-Agent": "xpi", "Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token

    while True:
        try:
            request = urllib.request.Request(endpoint, headers=headers)
            with urllib.request.urlopen(request, timeout=120) as response:
                print("ntfy.py: subscribed to", endpoint)
                for raw in response:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    if event.get("event") != "message":
                        continue
                    title = str(event.get("title") or "").strip()
                    message = str(event.get("message") or "").strip()
                    if title and message:
                        text = title + ": " + message
                    else:
                        text = title or message
                    if not text:
                        continue
                    try:
                        priority = int(event.get("priority") or 3)
                    except (TypeError, ValueError):
                        priority = 3
                    messages.put((text[:400], priority))
        except Exception as exc:
            print("ntfy.py: stream error:", exc)
        time.sleep(5)


def flash_microdot():
    import microdotphat

    for _ in range(3):
        microdotphat.fill(1)
        microdotphat.show()
        time.sleep(0.08)
        microdotphat.clear()
        microdotphat.show()
        time.sleep(0.08)


def run_microdot():
    import microdotphat

    url, topic, token = ntfy_config()
    if not topic:
        print("ntfy.py: no topic set on the page")
        return
    messages = queue.Queue()
    threading.Thread(target=listen, args=(url, topic, token, messages),
                     daemon=True).start()

    text = time.strftime("%H:%M")
    showing_clock = True
    hold_until = 0.0
    carry = 0.0
    microdotphat.clear()
    microdotphat.write_string(text)
    microdotphat.show()
    print("ntfy.py: microdot-phat, topic", topic)

    while True:
        try:
            message, priority = messages.get_nowait()
        except queue.Empty:
            message = None

        if message:
            text = message
            showing_clock = False
            hold_until = time.time() + hold_seconds()
            carry = 0.0
            if priority >= 4:
                flash_microdot()
            microdotphat.clear()
            microdotphat.write_string(text)
            print("ntfy.py: alert:", text)
        elif not showing_clock and time.time() >= hold_until:
            text = time.strftime("%H:%M")
            showing_clock = True
            microdotphat.clear()
            microdotphat.write_string(text)

        if showing_clock:
            clock = time.strftime("%H:%M")
            if clock != text:
                text = clock
                microdotphat.clear()
                microdotphat.write_string(text)
            microdotphat.show()
            time.sleep(0.2)
        else:
            carry += text_speed()
            step = int(carry)
            if step:
                carry -= step
                microdotphat.scroll(amount_x=step)
            microdotphat.show()
            time.sleep(0.05)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    url, topic, token = ntfy_config()
    if not topic:
        print("ntfy.py: no topic set on the page")
        return
    messages = queue.Queue()
    threading.Thread(target=listen, args=(url, topic, token, messages),
                     daemon=True).start()

    text = time.strftime("%H:%M")
    grid = _display.text_bitmap(text)
    offset = 0
    showing_clock = True
    hold_until = 0.0
    print("ntfy.py: unicorn, topic", topic)

    while True:
        try:
            message, priority = messages.get_nowait()
        except queue.Empty:
            message = None

        if message:
            text = message
            grid = _display.text_bitmap(text)
            offset = 0
            showing_clock = False
            hold_until = time.time() + hold_seconds()
            if priority >= 4:
                for _ in range(3):
                    unicornhat.clear()
                    for y in range(shape[1]):
                        for x in range(shape[0]):
                            unicornhat.set_pixel(x, y, 255, 255, 255)
                    unicornhat.show()
                    time.sleep(0.08)
                    unicornhat.clear()
                    unicornhat.show()
                    time.sleep(0.08)
            print("ntfy.py: alert:", text)
        elif not showing_clock and time.time() >= hold_until:
            text = time.strftime("%H:%M")
            grid = _display.text_bitmap(text)
            offset = 0
            showing_clock = True

        if showing_clock:
            clock = time.strftime("%H:%M")
            if clock != text:
                text = clock
                grid = _display.text_bitmap(text)
                offset = 0
        _display.draw_unicorn(grid, offset, shape, color)
        offset += 1
        time.sleep(0.05)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("ntfy.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("ntfy.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
