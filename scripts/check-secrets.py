#!/usr/bin/env python3
"""Block likely secrets in staged changes and outgoing commits."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys

SELF_SKIP = {
    "scripts/check-secrets.py",
    ".githooks/pre-commit",
    ".githooks/pre-push",
}

ALLOWED_FILE_RE = re.compile(
    r"(?:^|/)\.env\.(?:example|sample|template|dist)$"
    r"|(?:^|/)id_(?:rsa|ed25519|ecdsa|dsa)\.pub$",
    re.I,
)
SENSITIVE_FILE_RE = re.compile(
    r"(?:^|/)(?:\.env(?:\.[^/]*)?|\.envrc|id_rsa(?:\.[^/]*)?|id_ed25519(?:\.[^/]*)?|"
    r"id_ecdsa(?:\.[^/]*)?|id_dsa(?:\.[^/]*)?)$"
    r"|\.(?:env|pem|key|p12|pfx|jks|keystore|kdbx|ovpn|mobileconfig)$",
    re.I,
)

PLACEHOLDER_RE = re.compile(
    r"^(?:"
    r"\$\{\{.*\}\}|"
    r"\$\{[^}]+\}|"
    r"\$[A-Za-z_][A-Za-z0-9_]*|"
    r"\{\{.*\}\}|"
    r"<[^>]*>|"
    r"x{3,}|\*{3,}|\.{3,}|-|"
    r"changeme|change[-_]?me|replace[-_]?me|example|sample|dummy|test|fake|"
    r"redacted|placeholder|none|null|true|false|0|1|"
    r"your[_-].*"
    r")$",
    re.I,
)

SECRET_NAME = (
    r"(?:PASSWORD|PASSWD|PWD|SECRET|TOKEN|API[_-]?KEY|APIKEY|ACCESS[_-]?KEY|"
    r"PRIVATE[_-]?KEY|CLIENT[_-]?SECRET|JWT[_-]?SECRET|COOKIE[_-]?SECRET|"
    r"AUTH[_-]?KEY|APP[_-]?KEY|ENCRYPTION[_-]?KEY|SIGNING[_-]?KEY|"
    r"WEBHOOK[_-]?(?:URL|SECRET)|MULLVAD[_-]?PRIVATE[_-]?KEY|"
    r"TMDB[_-]?API[_-]?KEY|ADSBHUB[_-]?KEY|ACTIVATION[_-]?CODE|"
    r"LICENSE[_-]?CODE|NESSUS[_-]?CODE|HOMEPAGE_VAR_[A-Z0-9_]+)"
)
ASSIGN_RE = re.compile(
    rf"(?i)\b([A-Z0-9_]*{SECRET_NAME}(?:_[A-Z0-9]+)*)\b\s*[:=]\s*[\"']?([^\"'\s#]+)"
)
HEADER_RE = re.compile(
    r"(?i)^\s*[-]?\s*(?:X-)?(?:Api-Key|API-Key|Authorization)\s*:\s*"
    r"[\"']?(?:Bearer|Basic)?\s*[\"']?([^\"'\s#]+)"
)
URL_CREDS_RE = re.compile(
    r"(?i)\b(?:postgres(?:ql)?|mysql|mariadb|redis(?:s)?|mongodb(?:\+srv)?|"
    r"amqp(?:s)?|https?)://[^/\s:@]*:([^@\s/]+)@"
)
TOKEN_RES = [
    (re.compile(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})\b"), "GitHub token"),
    (re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "Google API key"),
    (re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b"), "Slack token"),
    (re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+"), "Slack webhook"),
    (re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{20,}\b"), "Stripe key"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "API key"),
    (re.compile(r"\bSG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}\b"), "SendGrid key"),
    (re.compile(r"\bSK[0-9a-fA-F]{32}\b"), "Twilio key"),
    (re.compile(r"https://(?:discord|discordapp)\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+"), "Discord webhook"),
    (re.compile(r"\b[0-9]{8,10}:[A-Za-z0-9_-]{35}\b"), "Telegram bot token"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), "JWT"),
]


def run_git(args: list[str]) -> bytes:
    proc = subprocess.run(["git", *args], capture_output=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode("utf-8", "replace"))
        raise SystemExit(1)
    return proc.stdout


def changed_files(staged: bool, rev_range: str | None) -> list[str]:
    args = ["diff", "--name-only", "-z", "--diff-filter=ACMR"]
    args.append("--cached" if staged else rev_range)
    data = run_git(args)
    return [item.decode("utf-8", "replace") for item in data.split(b"\0") if item]


def diff_text(staged: bool, rev_range: str | None) -> str:
    args = ["diff", "--unified=0", "--no-color", "--no-prefix", "--diff-filter=ACMR"]
    args.append("--cached" if staged else rev_range)
    return run_git(args).decode("utf-8", "replace")


def redact(value: str) -> str:
    value = value.strip()
    if len(value) <= 8:
        return "***"
    return value[:4] + "..." + value[-4:]


def is_placeholder(value: str) -> bool:
    value = value.strip().strip("\"'").strip()
    return not value or bool(PLACEHOLDER_RE.match(value))


def line_findings(path: str, line_no: int, line: str) -> list[tuple[str, int, str, str]]:
    if "secret-scan: allow" in line.lower():
        return []
    normalized = re.sub(r"\$\{\{.*?\}\}", "{{GITHUB_EXPR}}", line)
    findings: list[tuple[str, int, str, str]] = []
    for match in ASSIGN_RE.finditer(normalized):
        name, value = match.group(1), match.group(2)
        if not is_placeholder(value):
            findings.append((path, line_no, f"secret assignment ({name})", value))
    match = HEADER_RE.search(normalized)
    if match and not is_placeholder(match.group(1)):
        findings.append((path, line_no, "authorization header", match.group(1)))
    for match in URL_CREDS_RE.finditer(normalized):
        if not is_placeholder(match.group(1)):
            findings.append((path, line_no, "URL credentials", match.group(1)))
    for regex, label in TOKEN_RES:
        for match in regex.finditer(normalized):
            findings.append((path, line_no, label, match.group(0)))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--staged", action="store_true", help="scan staged changes")
    group.add_argument("--range", metavar="REV", help="scan a git revision range")
    args = parser.parse_args()

    findings: list[tuple[str, int, str, str]] = []
    for path in changed_files(args.staged, args.range):
        if path in SELF_SKIP:
            continue
        if SENSITIVE_FILE_RE.search(path) and not ALLOWED_FILE_RE.search(path):
            findings.append((path, 0, "sensitive file", ""))

    current = None
    new_line = 0
    in_hunk = False
    for raw in diff_text(args.staged, args.range).splitlines():
        if raw.startswith("diff --git "):
            current = None
            in_hunk = False
            continue
        if not in_hunk and raw.startswith("+++ "):
            current = raw[4:].strip()
            if current.startswith('"') and current.endswith('"'):
                current = current[1:-1]
            if current == "/dev/null":
                current = None
            continue
        if raw.startswith("@@"):
            match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", raw)
            if match:
                new_line = int(match.group(1))
                in_hunk = True
            continue
        if not in_hunk or not current:
            continue
        if raw.startswith("+"):
            if current not in SELF_SKIP:
                findings.extend(line_findings(current, new_line, raw[1:]))
            new_line += 1
        elif raw.startswith(" "):
            new_line += 1

    unique: list[tuple[str, int, str, str]] = []
    seen: set[tuple[str, int, str]] = set()
    for finding in findings:
        key = (finding[0], finding[1], finding[2])
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)

    if not unique:
        print("No obvious secrets found.")
        return 0

    action = "commit" if args.staged else "push"
    print(f"Secret scan blocked the {action}.", file=sys.stderr)
    for path, line_no, rule, value in unique:
        location = f"{path}:{line_no}" if line_no else path
        detail = f"  {location}  {rule}"
        if value:
            detail += f" [{redact(value)}]"
        print(detail, file=sys.stderr)
    print(
        "Remove the secret or use an environment variable. "
        "Add '# secret-scan: allow' to a line if it is a false positive.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
