# xpi display webserver

Runs Pimoroni microdot-phat and Unicorn HAT/pHAT display scripts behind a web
page on a Raspberry Pi. One script runs at a time; switching stops the old one
and clears the board first. Python 3 standard library only, no build step.

![xpi control page](docs/control-page.png)

## Quick start

On the Pi:

```sh
git clone https://github.com/CFBR/xpi
cd xpi
sudo ./install.sh
```

The installer prints the page address, usually `http://<hostname>.local/` and
`http://<pi-ip>/`. Open it and pick a script.

From your laptop, without cloning on the Pi:

```sh
rsync -av --exclude .git xpi/ pi@raspberrypi.local:/tmp/xpi/
ssh pi@raspberrypi.local 'sudo /tmp/xpi/install.sh'
```

The service runs as root because the Unicorn LED driver needs `/dev/mem`.
Logs: `journalctl -fu xpi`.

## Control page

Everything on the page maps to a URL, so the address bar always shows the
action that was taken. Browsers get the page; curl gets JSON.

```
http://<pi-ip>/?action=switch&script=rainbow     # run or reset a script
```

| Command | What it does |
|---|---|
| `?action=update&script=message&message=hello` | Push text, restart `message` |
| `?action=update&seconds=15&script=timer` | Start a countdown |
| `?action=update&message=hi` | No script given: the running script picks it up live, no restart |
| `?action=update&brightness=0.4` | Set LED brightness from 0 to 1. Unicorn boards only |
| `?action=update&color=red` | Set the text or fill color, by name or `#RRGGBB` |
| `?action=switch&script=clock&arg=x` | Stop the current script, run `clock` with positional args |
| `?action=stop` | Kill the current script. Its last frame stays on the board |
| `?action=clear` | Kill it and blank the attached board |
| `?action=boot&script=clock` | Set the boot script. Omit it or use `none` to unset |
| `?action=status` | Running, pid, boot, scripts, boards, ip, revision, log |

Quote the whole URL because `?` and `&` are shell metacharacters. Repeating
`arg=` passes multiple positional arguments.

The page also draws: drag across the LED grid to light pixels, drag over lit
ones to erase, and Send paints the board. It has a live preview of what the
board shows, a brightness slider, a light/dark toggle, and a script editor that
loads, saves, uploads and deletes files in `scripts/`.

## state.json

```json
{"message": "...", "seconds": 15, "brightness": 0.4, "revision": 17}
```

`/action=update` increments `revision`. Scripts that poll the `revision()`
function in `scripts/_xpi_state.py` pick up new `message`, `seconds`,
`brightness` and `color` values without a restart.

`brightness` applies to the unicorn scripts. The microdot-phat is monochrome
and has no dimming, so the slider is disabled when that board is attached.

## Boards

Each script gets a tag from the folder it lives in, or from what it imports:
`microdot-phat`, `unicorn-hat`, `unicorn phat`, or `both`. The layouts differ,
so a microdot animation does not work on a Unicorn pHAT. The page filters
scripts by board tab and selects the tab for the detected board.

Detection is definitive for the microdot-phat (I2C chips answer) and for a
Unicorn HAT (EEPROM). A Unicorn pHAT has no EEPROM, so it is reported as
`inferred`.

## Scripts included

`scripts/` has the xpi scripts: `message`, `timer`, `unicorn_message`,
`hostname`, `ip`, `draw`, `solid`, `clear`.

`scripts/` also holds every script from the archived Pimoroni example sets,
under `microdot-phat/` and `unicorn-hat/`: 12 microdot-phat examples and 28
Unicorn HAT/pHAT examples. See `scripts/README.md`.

## Adding a script

Drop `myscript.py` into `/opt/xpi/scripts/` and it appears on the next page
load. Name a file with a leading `_` to keep it out of the list. The page's
editor does the same thing over HTTP.

## Credits

The display libraries in `vendor/` and the examples in `scripts/` come from
Pimoroni Ltd, MIT licensed: [microdot-phat](https://github.com/CFBR/microdot-phat)
and [unicorn-hat](https://github.com/CFBR/unicorn-hat). The license texts are
in `LICENSES/`. xpi itself is MIT, see `LICENSE`.
