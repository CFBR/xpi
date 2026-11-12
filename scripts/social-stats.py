# social-stats.py: one social number on the board.
#
# State:
#   social_site    github or youtube
#   social_target  username, channel, owner/repo, or URL
#   social_metric  commits, followers, following, stars,
#                  subscribers, views, videos
#
# GitHub uses the REST and search APIs. YouTube reads the public about page,
# so it needs no API key. The number refreshes every minute (social_refresh,
# minimum 60).

import re
import time
import urllib.parse
import urllib.request

import _display
import _dot
import _github
import _xpi_state

DEFAULT_REFRESH = 60
DEFAULT_COLOR = (0, 255, 255)
METRICS = {
    "github": ("commits", "followers", "following", "stars"),
    "youtube": ("subscribers", "views", "videos"),
}


def site():
    value = str(_xpi_state.value("social_site") or "github").strip().lower()
    return value if value in METRICS else "github"


def metric():
    value = str(_xpi_state.value("social_metric") or "").strip().lower()
    if value not in METRICS[site()]:
        return METRICS[site()][0]
    return value


def target_text():
    return str(_xpi_state.value("social_target")
               or _xpi_state.value("gh_target")
               or _xpi_state.value("repo")
               or _github.DEFAULT_TARGET).strip()


def refresh_seconds():
    try:
        return max(60, int(_xpi_state.value("social_refresh") or DEFAULT_REFRESH))
    except (TypeError, ValueError):
        return DEFAULT_REFRESH


def github_value(kind, name, name_metric):
    if name_metric == "commits":
        return _github.repo_commits(name) if kind == "repo" \
            else _github.user_commits(name)
    if name_metric in ("followers", "following"):
        stats = _github.user_stats(name.split("/")[0])
        return stats[name_metric]
    if name_metric == "stars":
        return _github.repo_stats(name)["stars"] if kind == "repo" \
            else _github.user_stars(name)
    return 0


def youtube_url(raw):
    raw = str(raw).strip()
    raw = re.sub(r"^https?://", "", raw, flags=re.I)
    raw = re.sub(r"^www\.", "", raw, flags=re.I)
    raw = re.sub(r"^youtube\.com/", "", raw, flags=re.I)
    raw = re.split(r"[?#]", raw)[0].strip("/")
    if raw.startswith("channel/"):
        channel = raw.split("/", 1)[1].split("/")[0]
        return "https://www.youtube.com/channel/%s/about" % (
            urllib.parse.quote(channel))
    if raw.startswith("c/") or raw.startswith("user/"):
        kind, name = raw.split("/", 1)
        return "https://www.youtube.com/%s/%s/about" % (
            kind, urllib.parse.quote(name.split("/")[0]))
    if raw.startswith("UC") and len(raw) >= 20 and "/" not in raw:
        return "https://www.youtube.com/channel/%s/about" % (
            urllib.parse.quote(raw))
    handle = raw.split("/")[0]
    if not handle.startswith("@"):
        handle = "@" + handle
    return "https://www.youtube.com/%s/about" % (
        urllib.parse.quote(handle, safe="@"))


def number_from_text(text):
    match = re.search(r"([\d,.]+)\s*([KMB]?)", text, re.I)
    if not match:
        return 0
    value = float(match.group(1).replace(",", ""))
    return int(round(value * {"K": 1000, "M": 1000000,
                              "B": 1000000000}.get(match.group(2).upper(), 1)))


def youtube_value(name, name_metric):
    request = urllib.request.Request(youtube_url(name), headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "CONSENT=YES+1"})
    with urllib.request.urlopen(request, timeout=15) as response:
        html = response.read().decode("utf-8", "replace")
    if name_metric == "subscribers":
        match = re.search(r'"subscriberCountText":"([^"]+)"', html)
    elif name_metric == "views":
        match = re.search(r'"viewCountText":"([^"]+)"', html)
    else:
        match = re.search(r'"videoCountText":"([^"]+)"', html)
    if not match:
        raise ValueError("no %s on the page" % name_metric)
    return number_from_text(match.group(1))


def fetch(previous):
    current_site = site()
    current_metric = metric()
    name = target_text()
    try:
        if current_site == "github":
            kind, repo_or_user = _github.target(name)
            count = github_value(kind, repo_or_user, current_metric)
        else:
            count = youtube_value(name, current_metric)
        print("social-stats.py: %s %s %s = %d"
              % (current_site, name, current_metric, count))
        return count
    except Exception as exc:
        print("social-stats.py: fetch failed for %s %s %s: %s"
              % (current_site, name, current_metric, exc))
        return previous


def draw_microdot(number):
    import microdotphat

    microdotphat.clear()
    _dot.big_text(_display.format_count(number))
    microdotphat.show()


def run_microdot():
    count = 0
    last = 0.0
    print("social-stats.py: microdot-phat, %s %s %s"
          % (site(), target_text(), metric()))

    while True:
        if time.time() - last >= refresh_seconds():
            count = fetch(count)
            last = time.time()
        draw_microdot(count)
        time.sleep(0.5)


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
    count = 0
    grid = _display.text_bitmap(_display.format_count(count))
    offset = 0
    last = 0.0
    last_revision = _xpi_state.revision()
    print("social-stats.py: unicorn, %s %s %s"
          % (site(), target_text(), metric()))

    while True:
        if time.time() - last >= refresh_seconds():
            count = fetch(count)
            last = time.time()
            grid = _display.text_bitmap(_display.format_count(count))
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
        print("social-stats.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("social-stats.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
