# pi-wireless-dashboard

A Tkinter-based wireless dashboard for Raspberry Pi displaying Wi-Fi, Bluetooth, GPS, and battery status on an 800×480 screen.

## Requirements

- Raspberry Pi with Raspberry Pi OS (desktop)
- Python 3 with `tkinter` and `Pillow` (`pip3 install pillow`)
- A CSV data source writing to `/tmp/display_data.csv`

## Running manually

```bash
python3 fancy_monitor.py
```

## Auto-start on boot

The dashboard can be set up as a systemd service so it starts automatically after every reboot.

### Install

```bash
cd ~/pi-wireless-dashboard
chmod +x install.sh
./install.sh
```

The script copies `wireless-dashboard.service` to `/etc/systemd/system/`, enables it, and starts it immediately.

> **Note:** The service file assumes the user is `pi` and the display is `:0`.  
> If your username or display differs, edit `wireless-dashboard.service` before running the install script:
> ```ini
> User=youruser
> Environment=DISPLAY=:0
> Environment=XAUTHORITY=/home/youruser/.Xauthority
> ```

### Managing the service

```bash
sudo systemctl status wireless-dashboard   # check status / view logs
sudo systemctl stop wireless-dashboard     # stop the dashboard
sudo systemctl start wireless-dashboard    # start the dashboard
sudo systemctl restart wireless-dashboard  # restart the dashboard
sudo systemctl disable wireless-dashboard  # remove from autostart
```