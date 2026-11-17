#!/bin/sh
set -eu
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required for the secret scanner." >&2
    exit 1
fi
repo_root=$(git rev-parse --show-toplevel)
git config core.hooksPath .githooks
chmod +x "$repo_root/.githooks/pre-commit" "$repo_root/.githooks/pre-push" "$repo_root/tools/check-secrets.py"
echo "Git hooks installed. Secret scanning runs on commit and push."
