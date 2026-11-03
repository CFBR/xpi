# github-commits.py — how many commits a repo got today, from the GitHub API.
#
# Repo comes from state.json "repo" (default CFBR/xpi), refresh interval from
# "gh_refresh" in seconds (default 600). Shows "XPI COMMITS <n>" scrolling.
# The API allows 60 requests an hour without a token, so keep the interval
# well above 60 seconds.

import datetime
import json
import time
import urllib.parse
import urllib.request

import _display
import _xpi_state

DEFAULT_REPO = "CFBR/xpi"
DEFAULT_REFRESH = 600
DEFAULT_COLOR = (0, 255, 255)


def repo_name():
    return str(_xpi_state.value("repo") or DEFAULT_REPO)


def refresh_seconds():
    try:
        return max(60, int(_xpi_state.value("gh_refresh") or DEFAULT_REFRESH))
    except (TypeError, ValueError):
        return DEFAULT_REFRESH


def commits_today():
    midnight = datetime.datetime.combine(
        datetime.date.today(), datetime.time.min)
    since = midnight.astimezone(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    url = "https://api.github.com/repos/%s/commits?since=%s&per_page=100" % (
        urllib.parse.quote(repo_name()), since)
    request = urllib.request.Request(url, headers={
        "User-Agent": "xpi", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.load(response)
    return len(data) if isinstance(data, list) else 0


def label(count):
    short = repo_name().split("/")[-1].upper()
    return "%s COMMITS %d" % (short, count)


def fetch(previous):
    """Count for today, or the previous value when the request fails."""
    try:
        return commits_today()
    except Exception as exc:
        print("github-commits.py: fetch failed:", exc)
        return previous


def run_microdot():
    import microdotphat

    count = None
    text = ""
    last = 0.0
    print("github-commits.py: microdot-phat, repo", repo_name())

    while True:
        if count is None or time.time() - last >= refresh_seconds():
            count = fetch(count if count is not None else 0)
            last = time.time()
            text = label(count)
            microdotphat.write_string(text)
            print("github-commits.py:", text)
        microdotphat.scroll()
        microdotphat.show()
        time.sleep(0.05)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    count = None
    text = ""
    grid = _display.text_bitmap(" ")
    offset = 0
    last = 0.0
    last_revision = _xpi_state.revision()
    print("github-commits.py: unicorn, repo", repo_name())

    while True:
        if count is None or time.time() - last >= refresh_seconds():
            count = fetch(count if count is not None else 0)
            last = time.time()
            text = label(count)
            grid = _display.text_bitmap(text)
            offset = 0
            print("github-commits.py:", text)
        new_revision = _xpi_state.revision()
        if new_revision != last_revision:
            last_revision = new_revision
            unicornhat.brightness(_display.brightness_value())
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
