# xpi — Raspberry Pi display webserver

LAN web server driving the Pimoroni microdot-phat / Unicorn HAT scripts. Switch
which script runs from a browser (`http://<pi-ip>/`), set the boot script, and
push messages/timers to the display from other machines via curl. Python 3
stdlib only — no pip installs.

## Deploy to the Pi

1. `git clone --depth 1 https://github.com/CFBR/xpi .`  (anywhere on the Pi)
2. Run both display libraries' own `install.sh` **once** to pull system deps
   (RPi.GPIO, rpi_ws281x, smbus):
   `sudo repos/microdot-phat/install.sh && sudo repos/unicorn-hat/install.sh`
3. `sudo ./install.sh` — copies this tree to `/opt/xpi`, clones the display
   repos there, installs and starts the `xpi` systemd service (runs as root so
   GPIO/SPI/I2C/WS281X access is unconditional).

Paper-trail: full build plan lives in [PLAN.md](PLAN.md); the working backlog
is [issues](https://github.com/CFBR/xpi/issues).

## Controlling

Open `http://<pi-ip>/` — lists every script (from `scripts/` plus
`repos/*/examples`), Run / stop / clear buttons, boot picker, message+timer
sender, live log tail.

### HTTP API (all responses JSON)

| Required | Action |
|---|---|
| `http://<pi-ip>/?action=update&script=message&message=ok` | push text, restart `message` script |
| `http://<pi-ip>/?action=update&seconds=15&script=timer` | push a 15 s countdown, restart `timer` |
| `http://<pi-ip>/?action=update&message=hi` | no script given: just bump the state so a running script picks it up live |
| `http://<pi-ip>/?action=switch&script=clock` | stop current, run `clock` |
| `http://<pi-ip>/?action=switch&script=scrolling-text&arg=%22hello%22` | stop current, run a repo example with positional args |
| `http://<pi-ip>/?action=stop` | kill current script, leave last frame |
| `http://<pi-ip>/?action=clear` | kill current script **and blank the board** |
| `http://<pi-ip>/?action=boot&script=message` | set boot script (omit/`none` = nothing at boot) |
| `http://<pi-ip>/?action=status` | JSON: `running`, `pid`, `started`, `boot`, `scripts`, `revision`, `log` |

```sh
# quote the whole URL; ? and & are shell metacharacters
curl "http://<pi-ip>/?action=update&script=message&message=hello from the lab"
# lenient form (missing '?', no quote-safe ? in pathname) also parses:
curl "http://<pi-ip>/action=update&script=message&message=ok"
```

### State file contract (`state.json`)

```json
{"message": "...", "seconds": 15, "revision": 17}
```

- Every `/action=update` bumps `revision`.
- Scripts that poll `scripts/xpi_state.revision()` pick up new
  `message`/`seconds` **without restarting** (the shipped scripts do).
- Those that never read state need a restart — pass `script=<name>` (the
  server kills and re-launches the child with your extra `arg=` params as
  argv).

### Adding a script

Drop `myscript.py` into `scripts/` — it shows up in the UI / `status` on the
next request. Skip a file by naming it `_something.py`. Same for any
microdot-phat / unicorn-hat repo example: is already scanned from
`repos/*/examples/**`.

## Brittle bits / notes

- `switch` (and `update&script=...`) stops the previous child and **blanks
  the board first**, so a running animation's last frame no longer shows
  through under the new script.
- One child at a time. Switching stops the previous child (SIGINT → 2 s
  → SIGTERM → 2 s → SIGKILL) — the boards share hardware so scripts are never
  co-resident.
- MEMORY: ~15 MB RSS (stdlib interpreter + one child script); fine on a Pi
  Zero (512 MB).
- No HTTPS, no auth: LAN-trusted device by design.
- Logs go to stdout/stderr: `journalctl -fu xpi` on the Pi.
- Every script carries a board tag (`microdot-phat`, `unicorn-hat`,
  `unicorn phat 8x8`, `generic`) derived from what it imports / which repo
  dir it came from; the UI filters by board tab, since the two boards have
  different pixel layouts and animations are not interchangeable between
  microdot phat and unicorn phat.
- UI actions update the address bar (e.g. Run on `snow` →
  `/?action=switch&script=snow`); reloading that URL in a browser re-applies
  the action and re-serves the page (browsers get the control page,
  curl-style `Accept: */*` clients still get the JSON API).
- A `stop` leaves the last frame on the board; `clear` blanks it.
- Boot script mismatch (e.g. deleted after being set) logs a warning and
  boots with no script — the service never crashes because of that.

## Design documents / building on

The plan lives in `PLAN.md`. Issues track what's still open.
