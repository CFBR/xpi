#!/bin/sh
# Pull the latest xpi and redeploy on the Pi.
#   ./update.sh
set -e
cd "$(dirname "$0")"
git pull --ff-only
sudo ./install.sh
