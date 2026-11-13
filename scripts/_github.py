# _github.py: GitHub target parsing and API reads.
#
# Shared by github-commits.py and social-stats.py. The target accepts a
# username, owner/repo, @name, or a GitHub URL.

import json
import re
import urllib.parse
import urllib.request

DEFAULT_TARGET = "CFBR/xpi"


def clean_target(raw):
    raw = str(raw or DEFAULT_TARGET).strip()
    raw = re.sub(r"^@", "", raw)
    raw = re.sub(r"^https?://", "", raw, flags=re.I)
    raw = re.sub(r"^www\.", "", raw, flags=re.I)
    raw = re.sub(r"^github\.com/", "", raw, flags=re.I)
    raw = re.split(r"[?#]", raw)[0].strip("/")
    if raw.endswith(".git"):
        raw = raw[:-4]
    return raw or DEFAULT_TARGET


def target(raw):
    parts = [part for part in clean_target(raw).split("/") if part]
    if len(parts) >= 2:
        return "repo", "/".join(parts[:2])
    return "user", parts[0]


def get_json(url, token=None):
    headers = {
        "User-Agent": "xpi", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = "Bearer " + str(token)
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response), response.headers


def user_commits(user, since=None):
    query = "author:%s" % user
    if since:
        query += " committer-date:>=%s" % since
    data, _ = get_json(
        "https://api.github.com/search/commits?q=%s&per_page=1"
        % urllib.parse.quote(query, safe=""))
    return int(data.get("total_count") or 0)


def repo_commits(repo, since=None):
    path = urllib.parse.quote(repo, safe="/")
    url = "https://api.github.com/repos/%s/commits?per_page=1" % path
    if since:
        url += "&since=" + urllib.parse.quote(since)
    data, headers = get_json(url)
    link = headers.get("Link", "")
    match = re.search(r'[?&]page=(\d+)>; rel="last"', link)
    if match:
        return int(match.group(1))
    return len(data) if isinstance(data, list) else 0


def user_stats(user):
    data, _ = get_json(
        "https://api.github.com/users/%s" % urllib.parse.quote(user))
    return {
        "followers": int(data.get("followers") or 0),
        "following": int(data.get("following") or 0),
        "repos": int(data.get("public_repos") or 0),
    }


def repo_stats(repo):
    path = urllib.parse.quote(repo, safe="/")
    data, _ = get_json("https://api.github.com/repos/%s" % path)
    return {
        "stars": int(data.get("stargazers_count") or 0),
        "forks": int(data.get("forks_count") or 0),
        "issues": int(data.get("open_issues_count") or 0),
    }


def open_pulls(repo, token=None):
    path = urllib.parse.quote(repo, safe="/")
    data, _ = get_json(
        "https://api.github.com/repos/%s/pulls?state=open&per_page=100"
        % path, token)
    return len(data) if isinstance(data, list) else 0


def review_requests(repo, token=None):
    if not token:
        return None
    query = "is:pr is:open review-requested:@me repo:%s" % repo
    data, _ = get_json(
        "https://api.github.com/search/issues?q=%s&per_page=1"
        % urllib.parse.quote(query, safe=""), token)
    return int(data.get("total_count") or 0)


def latest_ci(repo, branch="main", token=None):
    path = urllib.parse.quote(repo, safe="/")
    try:
        data, _ = get_json(
            "https://api.github.com/repos/%s/actions/runs?branch=%s&per_page=1"
            % (path, urllib.parse.quote(branch)), token)
        runs = data.get("workflow_runs") or []
        if runs:
            run = runs[0]
            return run.get("conclusion") or run.get("status") or "unknown"
    except Exception:
        pass
    try:
        data, _ = get_json(
            "https://api.github.com/repos/%s/commits/%s/status"
            % (path, urllib.parse.quote(branch)), token)
        return data.get("state") or "unknown"
    except Exception:
        return "unknown"


def user_stars(user):
    url = "https://api.github.com/users/%s/repos?per_page=100&page=1" % (
        urllib.parse.quote(user))
    data, _ = get_json(url)
    if not isinstance(data, list):
        return 0
    return sum(int(repo.get("stargazers_count") or 0) for repo in data)
