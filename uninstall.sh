#!/bin/sh
# Remove the xpi service from a Pi. Run with sudo:
#   sudo ./uninstall.sh            keeps /opt/xpi
#   sudo ./uninstall.sh --purge    also deletes /opt/xpi
set -e

systemctl disable --now xpi 2>/dev/null || true
rm -f /etc/systemd/system/xpi.service
systemctl daemon-reload

echo "xpi.service removed."

if [ "$1" = "--purge" ]; then
  rm -rf /opt/xpi
  echo "/opt/xpi deleted."
else
  echo "/opt/xpi is still there. Remove it with: sudo rm -rf /opt/xpi"
fi
