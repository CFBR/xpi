# xpi display webserver

Runs Pimoroni microdot-phat / Unicorn pHAT + HAT display scripts behind a web
page. One script runs at a time; switching stops the old one and clears both
boards first.

Deploy target: a Raspberry Pi with `python3`, `git`, and the display
libraries (`RPi.GPIO`, `smbus`; `pip3 install rpi_ws281x` on Unicorn boards).

## Install

```sh
git clone https://github.com/CFBR/xpi.git
cd xpi
sudo ./install.sh          # copies to /opt/xpi, installs the xpi systemd service
```

The service runs as root because the Unicorn LED driver needs `/dev/mem`.
Logs: `journalctl -fu xpi`.

A browser hitting a `/?action=...` URL gets the control page and re-applies
the action client-side. curl gets JSON.

## Control

Open `http://<pi-ip>/`. Every click maps to a URL:

```
http://<pi-ip>/?action=switch&script=snow     # Run or reset a script
```

### API

| Command | What it does |
|---|---|
| `?action=update&script=message&message=hello` | Push text, restart `message` |
| `?action=update&seconds=15&script=timer` | Start a countdown |
| `?action=update&message=hi` | No script given: the running script picks it up live, no restart |
| `?action=update&brightness=0.4` | Set LED brightness from 0 to 1. Unicorn boards only |
| `?action=switch&script=clock&arg=x` | Stop the current script, run `clock` with positional args |
| `?action=stop` | Kill the current script. Its last frame stays on the board |
| `?action=clear` | Kill it and blank both boards |
| `?action=boot&script=clock` | Set the boot script. Omit it or use `none` to unset |
| `?action=status` | Running, pid, boot, scripts, boards, revision, log |

Quote the whole URL because `?` and `&` are shell metacharacters. Repeating
`arg=` passes multiple positional arguments.

### state.json

```json
{"message": "...", "seconds": 15, "brightness": 0.4, "revision": 17}
```

`/action=update` increments `revision`. Scripts that poll the `revision()`
function in `scripts/_xpi_state.py` pick up new `message`, `seconds` and
`brightness` values without a restart.

`brightness` applies to the unicorn scripts. The microdot-phat is monochrome
and has no dimming, so the slider is disabled when that board is attached.

### Boards

Each script gets a tag from what it imports: `microdot-phat`, `unicorn-hat`,
`unicorn phat 8x8`, or `generic`. The boards have different pixel layouts, so
a microdot animation does not work on a Unicorn pHAT. The UI filters scripts
by board tab. `generic` and `both` tags mean the script was not written for
either layout.

### Adding a script

Drop `myscript.py` into `/opt/xpi/scripts/`; it appears on the next page
load. Name a file with a leading `_` to keep it out of the list.
