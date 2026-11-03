#!/bin/sh
# xpi Pi-side deployer. Run with sudo on the Raspberry Pi:
#   sudo ./install.sh
set -e

DEST=/opt/xpi
SRC="$(cd "$(dirname "$0")" && pwd)"

echo "deploying from $SRC to $DEST"
mkdir -p "$DEST/scripts"
cp "$SRC/server.py" "$SRC/index.html" "$DEST/"
# keep an existing config.json: it holds the boot script and any token
if [ ! -f "$DEST/config.json" ]; then cp "$SRC/config.json" "$DEST/"; fi
cp -r "$SRC/scripts/." "$DEST/scripts/"          # keeps scripts saved from the web editor
cp -r "$SRC/support" "$DEST/"
cp -r "$SRC/vendor" "$SRC/LICENSES" "$SRC/docs" "$DEST/"
if [ -f "$SRC/README.md" ]; then cp "$SRC/README.md" "$DEST/"; fi

# microdot-phat needs I2C; harmless on Unicorn boards
CFG=/boot/config.txt
if [ -f /boot/firmware/config.txt ]; then CFG=/boot/firmware/config.txt; fi
if [ -f "$CFG" ]; then
  sed -i 's/^#dtparam=i2c_arm=on/dtparam=i2c_arm=on/' "$CFG" 2>/dev/null || true
  grep -q '^dtparam=i2c_arm=on' "$CFG" 2>/dev/null || echo 'dtparam=i2c_arm=on' >> "$CFG"
fi
grep -q '^i2c-dev' /etc/modules 2>/dev/null || echo 'i2c-dev' >> /etc/modules
modprobe i2c-dev 2>/dev/null || true

# display library dependencies (already present on most Pi images)
apt-get update -qq >/dev/null 2>&1 || true
apt -y install python3-pip python3-dev python3-rpi.gpio python3-smbus >/dev/null 2>&1 || \
  apt-get -y install python3-pip python3-dev python3-rpi.gpio python3-smbus >/dev/null 2>&1 || true
apt -y install python3-smbus2 >/dev/null 2>&1 || true   # bookworm only; pip covers bullseye
pip3 install rpi_ws281x smbus2 >/dev/null 2>&1 || true   # drives and clears Unicorn HAT/pHAT

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
systemctl enable xpi >/dev/null 2>&1 || true
systemctl restart xpi

# Prefer the default-route address; hostname -I can list Tailscale first.
IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{for (i=1;i<=NF;i++) if ($i=="src") {print $(i+1); exit}}')
[ -n "$IP" ] || IP=$(hostname -I 2>/dev/null | awk '{print $1}')
NAME=$(hostname)

echo
echo "xpi is running. Open the control page:"
echo
echo "  http://$NAME.local/"
if [ -n "$IP" ]; then
  echo "  http://$IP/"
fi
echo
echo "  api:  http://${IP:-$NAME.local}/?action=update&script=message&message=hello"
echo "  logs: journalctl -fu xpi"
echo
