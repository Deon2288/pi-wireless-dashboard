#!/bin/bash
# install.sh — Install and enable the Wireless Dashboard autostart service

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_SRC="$REPO_DIR/wireless-dashboard.service"
SERVICE_DEST="/etc/systemd/system/wireless-dashboard.service"
SCRIPT_PATH="$REPO_DIR/fancy_monitor.py"

# Update the ExecStart path in the service file to match this repo's location
sed "s|/home/pi/pi-wireless-dashboard/fancy_monitor.py|$SCRIPT_PATH|g" \
    "$SERVICE_SRC" | sudo tee "$SERVICE_DEST" > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable wireless-dashboard.service
sudo systemctl start wireless-dashboard.service

echo "Wireless Dashboard service installed and enabled."
echo "It will now start automatically after every reboot."
echo ""
echo "Useful commands:"
echo "  sudo systemctl status wireless-dashboard   # check status"
echo "  sudo systemctl stop wireless-dashboard     # stop the dashboard"
echo "  sudo systemctl restart wireless-dashboard  # restart the dashboard"
