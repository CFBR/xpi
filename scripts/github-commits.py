# github-commits.py: commits for a GitHub user or repo.
#
# Target comes from state.json "gh_target": a username, owner/repo, or a
# GitHub URL. It falls back to "repo", then CFBR/xpi.
#
# gh_period is today, week, month, or total. It defaults to today so the
# number resets at local midnight. The number refreshes every minute
# (gh_refresh, minimum 60). A user target uses the commit search API; a repo
# target reads the last page of the commits API.
#
# The search API allows 10 requests a minute without a token. The commits API
# allows 60 an hour, so one repo request a minute is the limit.

import datetime
import time

import _display
import _dot
import _github
import _xpi_state

DEFAULT_REFRESH = 60
DEFAULT_COLOR = (0, 255, 255)


def target_text():
    return _github.clean_target(
        _xpi_state.value("gh_target")
        or _xpi_state.value("social_target")
        or _xpi_state.value("repo")
        or _github.DEFAULT_TARGET)


def refresh_seconds():
    try:
        return max(60, int(_xpi_state.value("gh_refresh") or DEFAULT_REFRESH))
    except (TypeError, ValueError):
        return DEFAULT_REFRESH


def period():
    value = str(_xpi_state.value("gh_period") or "today").strip().lower()
    return value if value in ("today", "week", "month", "total") else "today"


def period_start():
    current = period()
    if current == "total":
        return None
    now = datetime.datetime.now()
    if current == "week":
        now -= datetime.timedelta(days=now.weekday())
    elif current == "month":
        now = now.replace(day=1)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def fetch(previous):
    kind, name = _github.target(target_text())
    start = period_start()
    try:
        if start is None:
            count = _github.repo_commits(name) if kind == "repo" \
                else _github.user_commits(name)
        else:
            since = start.astimezone(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ")
            day = start.strftime("%Y-%m-%d")
            count = _github.repo_commits(name, since) if kind == "repo" \
                else _github.user_commits(name, day)
        print("github-commits.py: %s %s %s has %d commits"
              % (kind, name, period(), count))
        return count
    except Exception as exc:
        print("github-commits.py: fetch failed for %s %s: %s"
              % (kind, name, exc))
        return previous


def draw_microdot(number):
    import microdotphat

    microdotphat.clear()
    _dot.big_text(_display.format_count(number))
    microdotphat.show()


def run_microdot():
    count = 0
    last = 0.0
    print("github-commits.py: microdot-phat, target", target_text() or _github.DEFAULT_TARGET)

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
    print("github-commits.py: unicorn, target", target_text() or _github.DEFAULT_TARGET)

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
        print("github-commits.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("github-commits.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
