# Installing xpi

## What you need

- A Raspberry Pi with a 40 pin header, any model. A Pi Zero is enough.
- Raspberry Pi OS, bullseye or newer.
- One of the [supported displays](boards.md), fitted on the header.

## On the Pi

```sh
git clone https://github.com/CFBR/xpi
cd xpi
sudo ./install.sh
```

The installer:

- copies the server, page, scripts, vendored libraries, icons and docs to `/opt/xpi`
- enables I2C in `config.txt` (under `/boot/firmware/`, or `/boot/` on older
  images) and in `/etc/modules`, which the Micro Dot pHAT needs and the Unicorn
  boards ignore
- installs `python3-rpi.gpio`, `python3-smbus`, `python3-smbus2`,
  `python3-pil`, and `rpi_ws281x` plus `smbus2` from PyPI, best effort
- writes `/etc/systemd/system/xpi.service`, enables it, and starts it
- prints the page address, usually `http://<hostname>.local/` and
  `http://<pi-ip>/`

Open that address and pick a script.

## From a laptop

Copy the checkout over and run the installer on the Pi:

```sh
rsync -av --exclude .git xpi/ pi@raspberrypi.local:/tmp/xpi/
ssh pi@raspberrypi.local 'sudo /tmp/xpi/install.sh'
```

## Updating

On the Pi, from the clone:

```sh
./update.sh
```

That pulls `main` and runs the installer again. An existing
`/opt/xpi/config.json` is kept, and scripts are copied over the top rather than
wiped, so anything saved from the page survives.

## Uninstalling

```sh
sudo ./uninstall.sh            # stops and removes the service, keeps /opt/xpi
sudo ./uninstall.sh --purge    # also deletes /opt/xpi
```

## The service

```sh
systemctl status xpi
sudo systemctl restart xpi
journalctl -fu xpi
```

The service runs as root because the Unicorn driver writes to `/dev/mem`. It
listens on port 80 by default.

For a foreground run while debugging:

```sh
sudo python3 /opt/xpi/server.py --port 8080
```

`--bind` sets the address it listens on, default `0.0.0.0`.

## Files on the Pi

| Path | What it is |
|---|---|
| `/opt/xpi/server.py`, `index.html` | the server and the control page |
| `/opt/xpi/scripts/` | every runnable script, including ones saved from the page |
| `/opt/xpi/vendor/`, `support/`, `LICENSES/`, `docs/` | libraries, helpers, licenses, these notes |
| `/opt/xpi/assets/` | favicon and app icons |
| `/opt/xpi/config.json` | boot script, playlist, groups, ntfy and token |
| `/opt/xpi/state.json` | message, countdown, brightness, speed, revision |

`config.json` is created on install and never overwritten. `state.json` is
written by the server at runtime.
