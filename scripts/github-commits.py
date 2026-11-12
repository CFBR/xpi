# github-commits.py: total commits for a GitHub user or repo.
#
# Target comes from state.json "gh_target": a username, owner/repo, or a
# GitHub URL. It falls back to "repo", then CFBR/xpi. The number refreshes
# every minute (gh_refresh, minimum 60). A user target uses the commit search
# API; a repo target reads the last page of the commits API.
#
# The search API allows 10 requests a minute without a token. The commits API
# allows 60 an hour, so one repo request a minute is the limit.

import json
import re
import time
import urllib.parse
import urllib.request

import _display
import _dot
import _xpi_state

DEFAULT_TARGET = "CFBR/xpi"
DEFAULT_REFRESH = 60
DEFAULT_COLOR = (0, 255, 255)


def target_text():
    raw = str(_xpi_state.value("gh_target")
              or _xpi_state.value("repo")
              or DEFAULT_TARGET).strip()
    raw = re.sub(r"^@", "", raw)
    raw = re.sub(r"^https?://", "", raw, flags=re.I)
    raw = re.sub(r"^www\.", "", raw, flags=re.I)
    raw = re.sub(r"^github\.com/", "", raw, flags=re.I)
    raw = re.split(r"[?#]", raw)[0].strip("/")
    if raw.endswith(".git"):
        raw = raw[:-4]
    return raw


def target_query():
    parts = [part for part in target_text().split("/") if part]
    if not parts:
        parts = DEFAULT_TARGET.split("/")
    if len(parts) >= 2:
        return "repo", "/".join(parts[:2])
    return "user", parts[0]


def refresh_seconds():
    try:
        return max(60, int(_xpi_state.value("gh_refresh") or DEFAULT_REFRESH))
    except (TypeError, ValueError):
        return DEFAULT_REFRESH


def request(url):
    return urllib.request.Request(url, headers={
        "User-Agent": "xpi", "Accept": "application/vnd.github+json"})


def user_commits(user):
    query = urllib.parse.quote("author:%s" % user, safe="")
    url = "https://api.github.com/search/commits?q=%s&per_page=1" % query
    with urllib.request.urlopen(request(url), timeout=15) as response:
        data = json.load(response)
    return int(data.get("total_count") or 0)


def repo_commits(repo):
    path = urllib.parse.quote(repo, safe="/")
    url = "https://api.github.com/repos/%s/commits?per_page=1" % path
    with urllib.request.urlopen(request(url), timeout=15) as response:
        link = response.headers.get("Link", "")
        data = json.load(response)
    match = re.search(r'[?&]page=(\d+)>; rel="last"', link)
    if match:
        return int(match.group(1))
    return len(data) if isinstance(data, list) else 0


def fetch(previous):
    kind, name = target_query()
    try:
        count = repo_commits(name) if kind == "repo" else user_commits(name)
        print("github-commits.py: %s %s has %d commits" % (kind, name, count))
        return count
    except Exception as exc:
        print("github-commits.py: fetch failed for %s %s: %s"
              % (kind, name, exc))
        return previous


def draw_microdot(number, offset=0):
    import microdotphat

    width = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
    height = getattr(microdotphat, "HEIGHT", 7)
    grid = _display.text_bitmap(number)
    text_w = len(grid[0])
    y0 = (height - len(grid)) // 2

    microdotphat.clear()
    if text_w <= width:
        x0 = (width - text_w) // 2
        for y in range(len(grid)):
            for x in range(text_w):
                if grid[y][x]:
                    microdotphat.set_pixel(_dot.buffer_x(x0 + x), y0 + y, 1)
    else:
        for x in range(width):
            src = (x + offset) % text_w
            for y in range(len(grid)):
                if grid[y][src]:
                    microdotphat.set_pixel(_dot.buffer_x(x), y0 + y, 1)
    microdotphat.show()


def run_microdot():
    import microdotphat

    count = 0
    text = "0"
    last = 0.0
    offset = 0
    width = _dot.visible_width(getattr(microdotphat, "WIDTH", 45))
    print("github-commits.py: microdot-phat, target", target_text() or DEFAULT_TARGET)

    while True:
        if time.time() - last >= refresh_seconds():
            count = fetch(count)
            last = time.time()
            text = str(count)
            offset = 0

        if len(text) * _display.CHAR_W <= width:
            draw_microdot(text)
            time.sleep(0.5)
        else:
            draw_microdot(text, offset)
            offset = (offset + 1) % (len(text) * _display.CHAR_W)
            time.sleep(0.05)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    count = 0
    grid = _display.text_bitmap("0")
    offset = 0
    last = 0.0
    last_revision = _xpi_state.revision()
    print("github-commits.py: unicorn, target", target_text() or DEFAULT_TARGET)

    while True:
        if time.time() - last >= refresh_seconds():
            count = fetch(count)
            last = time.time()
            grid = _display.text_bitmap(str(count))
            offset = 0

        new_revision = _xpi_state.revision()
        if new_revision != last_revision:
            last_revision = new_revision
            color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)

        _display.draw_unicorn(grid, offset, shape, color)
        offset += 1
        time.sleep(0.05)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("github-commits.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("github-commits.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
