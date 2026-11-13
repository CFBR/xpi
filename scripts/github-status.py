# github-status.py — open PRs, review requests and the latest CI result.
#
# State:
#   gh_repo     owner/repo, default CFBR/xpi
#   gh_branch   branch for the latest CI run, default main
#   gh_refresh  seconds between API reads, minimum 60
#   gh_seconds  seconds per page on the Micro Dot, default 3
#
# Put a GitHub token in config.json as "github_token" to include review
# requests. Public repositories work without one.

import time

import _display
import _dot
import _github
import _xpi_config
import _xpi_state

DEFAULT_REFRESH = 60
DEFAULT_COLOR = (0, 255, 0)


def target_text():
    raw = _xpi_state.value("gh_repo") or _xpi_state.value("gh_target")
    if raw:
        kind, name = _github.target(raw)
        if kind == "repo":
            return name
    return _github.DEFAULT_TARGET


def branch():
    return str(_xpi_state.value("gh_branch") or "main").strip() or "main"


def refresh_seconds():
    try:
        return max(60, int(_xpi_state.value("gh_refresh") or DEFAULT_REFRESH))
    except (TypeError, ValueError):
        return DEFAULT_REFRESH


def page_seconds():
    try:
        return max(1.0, min(30.0, float(_xpi_state.value("gh_seconds") or 3)))
    except (TypeError, ValueError):
        return 3.0


def token():
    return _xpi_config.value("github_token")


def ci_label(value):
    if value == "success":
        return "OK"
    if value in ("failure", "timed_out", "action_required"):
        return "ERR"
    if value in ("pending", "queued", "in_progress", "waiting"):
        return ".."
    return "?"


def fetch(previous):
    kind, name = _github.target(target_text())
    if kind != "repo":
        print("github-status.py: target must be owner/repo, got", name)
        return previous
    try:
        data = {
            "prs": _github.open_pulls(name, token()),
            "reviews": _github.review_requests(name, token()),
            "ci": _github.latest_ci(name, branch(), token()),
        }
        print("github-status.py: %s PR %s review %s CI %s"
              % (name, data["prs"], data["reviews"], data["ci"]))
        return data
    except Exception as exc:
        print("github-status.py: fetch failed for %s: %s" % (name, exc))
        return previous


def pages(data):
    reviews = data.get("reviews")
    return [
        "PR%s" % data.get("prs", "?"),
        "RV%s" % ("?" if reviews is None else reviews),
        "CI %s" % ci_label(data.get("ci")),
    ]


def summary(data):
    reviews = data.get("reviews")
    return "PR %s RV %s CI %s" % (
        data.get("prs", "?"),
        "?" if reviews is None else reviews,
        ci_label(data.get("ci")))


def run_microdot():
    import microdotphat

    data = {"prs": "?", "reviews": None, "ci": "unknown"}
    last = 0.0
    print("github-status.py: microdot-phat, target", target_text())
    while True:
        if time.time() - last >= refresh_seconds():
            data = fetch(data)
            last = time.time()
        for text in pages(data):
            microdotphat.clear()
            _dot.big_text(text)
            microdotphat.show()
            time.sleep(page_seconds())


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    data = {"prs": "?", "reviews": None, "ci": "unknown"}
    last = 0.0
    offset = 0
    grid = _display.text_bitmap(summary(data))
    print("github-status.py: unicorn, target", target_text())
    while True:
        if time.time() - last >= refresh_seconds():
            data = fetch(data)
            grid = _display.text_bitmap(summary(data))
            offset = 0
            last = time.time()
        color = _display.parse_color(_xpi_state.value("color"), DEFAULT_COLOR)
        if data.get("ci") in ("failure", "timed_out", "action_required"):
            color = (255, 64, 64)
        elif ci_label(data.get("ci")) == "..":
            color = (255, 180, 0)
        _display.draw_unicorn(grid, offset, shape, color)
        offset += 1
        time.sleep(0.05)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("github-status.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("github-status.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
