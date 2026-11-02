# xpi — display webserver for the Pi

Runs Pimoroni microdot-phat / Unicorn pHAT + HAT display scripts behind a web
page. One script runs at a time; switching stops the old one and clears both
boards first.

Deploy target: a Raspberry Pi with `python3`, `git`, and the two display
libraries (`RPi.GPIO`, `smbus`, `rpi_ws281x` via `pip3 install rpi_ws281x` on
Unicorn boards).

## Install

```sh
git clone https://github.com/CFBR/xpi.git
cd xpi
sudo ./install.sh          # copies to /opt/xpi, installs the xpi systemd service
```

Service runs as root because the Unicorn LED driver needs `/dev/mem`.
Logs: `journalctl -fu xpi`.

Browsers hitting `/?action=...` URLs get the control page (the action is
re-applied client-side); curl-style clients get JSON.

## Controlling

Open `http://<pi-ip>/`. Every click is also a URL:

```
http://<pi-ip>/?action=switch&script=snow     # Run/reset a script
```

### API

| |
|---|
| `?action=update&script=message&message=hello` | push text; restarts `message` |
| `?action=update&seconds=15&script=timer` | start a countdown |
| `?action=update&message=hi` | no script: running script picks it up live, no restart |
| `?action=switch&script=clock&arg=x` | stop current, run `clock` with positional args |
| `?action=stop` | kill the current script; its last frame stays |
| `?action=clear` | kill it and blank both boards |
| `?action=boot&script=clock` | set the boot script (omit or `none` to unset) |
| `?action=status` | running/pid/boot/scripts/boards/revision/log |

Quote the URL — `?` and `&` are shell metacharacters. Repeating `arg=` passes
multiple positional arguments.

### state.json

```json
{"message": "...", "seconds": 15, "revision": 17}
```

`/action=update` bumps `revision`. Scripts that poll
`scripts/_xpi_state.py`'s `revision()` pick up new `message`/`seconds` live
without restarting.

### Boards

Scripts are tagged by what they import (`microdot-phat`, `unicorn-hat`,
`unicorn phat 8x8`, `generic`). The two boards have different pixel layouts —
a microdot animation is not interchangeable with a Unicorn pHAT one, so the
UI filters scripts by board tab. Scripts marked `generic`/`both` were not
written for either layout; run at your own risk.

### Adding a script

Drop `myscript.py` into `/opt/xpi/scripts/` — it shows up on the next
page/status load. Name a file with a leading `_` to keep it out of the list.
