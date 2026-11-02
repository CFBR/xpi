#!/bin/sh
# xpi Pi-side deployer. Run with sudo on the Raspberry Pi:
#   sudo ./install.sh            (after copying this tree to the Pi)
set -e

DEST=/opt/xpi
SRC="$(cd "$(dirname "$0")" && pwd)"

echo "deploying from $SRC to $DEST"
mkdir -p "$DEST"
cp "$SRC/server.py" "$SRC/index.html" "$SRC/config.json" "$DEST/"
cp -r "$SRC/scripts" "$DEST/"

# display library libs: shallow clone only if absent
[ -d "$DEST/repos/microdot-phat" ] || \
  git clone --depth 1 https://github.com/CFBR/microdot-phat "$DEST/repos/microdot-phat"
[ -d "$DEST/repos/unicorn-hat" ] || \
  git clone --depth 1 https://github.com/CFBR/unicorn-hat "$DEST/repos/unicorn-hat"

# display library deps
apt -y install python3-rpi.gpio python3-smbus python3-dev 2>/dev/null || apt-get -y install python3-rpi.gpio python3-smbus python3-dev
pip3 install rpi_ws281x 2>/dev/null || true   # needed to drive/clear Unicorn HAT/pHAT LEDs

cat > /etc/systemd/system/xpi.service <<'EOF'
[Unit]
Description=xpi display control webserver
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/xpi/server.py
WorkingDirectory=/opt/xpi
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now xpi
echo "deployed. serves on http://$(hostname -I | awk '{print $1}')/ (port 80)"
