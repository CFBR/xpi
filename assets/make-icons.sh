#!/bin/sh
set -e
cd "$(dirname "$0")"
rsvg-convert -w 16 -h 16 icon.svg -o /tmp/xpi-16.png
rsvg-convert -w 32 -h 32 icon.svg -o /tmp/xpi-32.png
rsvg-convert -w 48 -h 48 icon.svg -o /tmp/xpi-48.png
rsvg-convert -w 180 -h 180 icon.svg -o apple-touch-icon.png
rsvg-convert -w 192 -h 192 icon.svg -o icon-192.png
rsvg-convert -w 512 -h 512 icon.svg -o icon-512.png
magick /tmp/xpi-16.png /tmp/xpi-32.png /tmp/xpi-48.png favicon.ico
cp icon.svg favicon.svg
