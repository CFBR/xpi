# xpi-webserver — plan

## Context

Pi Zero (armv6, 512 MB) running Pimoroni microdot-phat and/or Unicorn HAT. The two repos
(https://github.com/CFBR/microdot-phat, https://github.com/CFBR/unicorn-hat — forks of Pimoroni's)
contain `examples/*.py` display scripts that run as infinite Python loops. User wants:

1. A LAN web server on the Pi (site hosted at `http://<pi-ip>/`) to switch which script is running.
2. Ability to set which script launches at boot.
3. An HTTP API like `curl "http://<pi-ip>/?action=update&script=message&message=ok"` so other
   scripts/machines can push a message (or timer countdown, etc.) to the display.

Decisions (user-approved this session): **Python 3 stdlib only server** (no pip deps, no cross-compile —
display scripts must run under Python anyway, so `python3` is already required), **state-file +
restart** update model (running scripts that opt in poll `state.json` for live updates; otherwise the
server restarts the script with new args). User's example URL `.../action=update&...` is missing the
`?` — the server accepts that lenient form too so the raw URL works as sent.

Deployment target directory on Pi: `/opt/xpi`. Source tree built in `/home/fire/working/xpi`.

## Facts (verified this session)

- microdot-phat: package dir `repos/microdot-phat/library/microdotphat/`; examples at
  `repos/microdot-phat/examples/*.py` (exact names: `advanced-scrolling.py clock.py fading-text.py
  flash.py graph.py scrolling-text.py scrolling-text_jp.py scrolling-word.py sine-wave.py thermal.py
  tiny-font.py vertical-text.py`); examples take positional argv
  (`scrolling-text.py` reads `sys.argv[1]`) and loop forever; import `microdotphat`
  (`write_string/scroll/show/clear/fill`).
- unicorn-hat: single module `repos/unicorn-hat/library/UnicornHat/unicornhat.py`
  (`setup.py` declares `py_modules=['unicornhat']`); examples at
  `repos/unicorn-hat/examples/*.py` plus subdirs `examples/hat/` and `examples/phat/`
  (exact names incl. `rainbow.py binary_clock.py game_of_life.py clean.py demo.py figlet.py ... `);
  import `unicornhat` (`set_layout(AUTO), rotation, brightness, get_shape, set_pixel, show, clear`).
- Both repos have their own `install.sh` that installs system deps (RPi.GPIO, rpi_ws281x, smbus) —
  running those on the Pi is a user-side prerequisite documented in README; our code adds only
  PYTHONPATH bridging so plain clones work without pip installs.

## Layout

```
xpi/
  server.py          # the webserver + script supervisor (single file, stdlib only)
  index.html         # control page (vanilla JS, no framework)
  install.sh         # Pi-side deployer: copies to /opt/xpi, clones repos, installs systemd unit
  README.md          # API reference + deployment steps
  config.json        # {"boot": null}            # which script auto-starts at boot
  state.json         # runtime state, revision-patched (not created in source tree)
  scripts/
    xpi_state.py     # helper imported by shipped scripts
    message.py       # microdotphat: scrolling text from state/argv, live-update
    timer.py         # microdotphat: mm:ss countdown from state/argv
    unicorn_message.py  # unicornhat: scrolling text, tiny built-in 3x5 pixel font
    clear.py         # clears whichever board answers (try both libs)
  repos/
    microdot-phat/   # shallow clone (git)
    unicorn-hat/     # shallow clone (git)
```

## Approach (build order)

### Step 1 — clone repos
```
git clone --depth 1 https://github.com/CFBR/microdot-phat /home/fire/working/xpi/repos/microdot-phat
git clone --depth 1 https://github.com/CFBR/unicorn-hat /home/fire/working/xpi/repos/unicorn-hat
```

### Step 2 — `scripts/xpi_state.py`
- `ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` (project root).
- `read_state() -> dict` (parses `ROOT/state.json`; missing or invalid JSON → `{}`).
- `revision() -> int` (`read_state().get("revision", 0)`).
- `value(key, default=None)` — convenience accessor.

### Step 3 — shipped display scripts
Common behavior for all five: `import xpi_state` works because server passes `scripts/` on
`PYTHONPATH` (server responsibility below). Each script: read `sys.argv[1:]` for a positional
fallback, then prefer `state.json` values, loop polling `xpi_state.revision()` once per frame so an
`/update` call revises content **without restarting** the script (user-selected semantics). No error
handling beyond clean KeyboardInterrupt exit.

- `message.py` (microdotphat): text from `state["message"]` (fallback argv, then `"hi"`);
  `write_string(text)`, then loop `scroll()/show()/time.sleep(0.05)`; re-writes string when revision
  changes (live-update). ~30 lines; pattern of `repos/microdot-phat/examples/scrolling-text.py`.
- `timer.py` (microdotphat): seconds from `state["seconds"]` (int fallback argv, default 60);
  displays “m:ss” via `write_string`, refreshes revision + text each second; holds at `0:00`
  blinking (no restart, no shutdown of itself).
- `unicorn_message.py` (unicornhat): same state/argv source (`message`), scrolls text using an
  inline ~40-char-glyph 3x8 bitmap font (only printable ASCII subset needed), brightness 0.5,
  `set_layout(AUTO)`. Poll revision each scroll frame. ~70 lines. Does not depend on pyfiglet or
  `figlet` example (avoids extra pip dep — that example is separate under repos/examples anyway).
- `clear.py`: `try: import microdotphat; microdotphat.fill(0); microdotphat.show()` then
  `try: import unicornhat; unicornhat.clear(); unicornhat.show()`, then `sys.exit(0)`. Used by the
  UI stop handler to blank the board after killing a script (server behavior below).

### Step 4 — `server.py` (the supervisor)

Imports strictly stdlib: `argparse, json, os, subprocess, sys, threading, time, signal,
urllib.parse, http.server`.

Constants (all paths relative to `ROOT = os.path.dirname(os.path.abspath(__file__))`):
```
STATE_FILE       = ROOT/state.json
CONFIG_FILE      = ROOT/config.json
SCRIPTS_DIR      = ROOT/scripts
SCAN_DIRS        = ["scripts",
                    "repos/microdot-phat/examples",
                    "repos/unicorn-hat/examples",
                    "repos/unicorn-hat/examples/hat",
                    "repos/unicorn-hat/examples/phat"]
REPO_LIBPATHS    = ["repos/microdot-phat/library",
                    "repos/unicorn-hat/library/UnicornHat"]
```

`scan_scripts()`: for each dir in `SCAN_DIRS`, if it exists, list `*.py`, skip names starting with
`_`, registry keyed by filename stem; on a duplicate stem keep the first hit in listed order and
log a warning. Called on every `/status` and `/switch` request (rel causes ~10 stat/print calls on
a Pi Zero — negligible). Re-scans pick up newly dropped scripts with no reload action.

Child process (only one runs at a time — both boards address the same hardware):
- `subprocess.Popen([sys.executable, script_path, *positional_args], cwd=repo_dir_of_script,
  env=child_env)` where `positional_args` come from repeated `arg=` query params.
- `child_env = os.environ.copy()` then `child_env["PYTHONPATH"] = inherited_parent_pythonpath +
  ":" + SCRIPTS_DIR + ":" + ":".join(each existing dir in REPO_LIBPATHS)` — keeps `xpi_state.py`
  importable and lets a dev/test stub shadow display libs by being first in the inherited var.
- Track pid, start time, last ~4 KiB of combined stdout+stderr (ring buffer via
  `collections.deques(maxlen=...)`, drained by a thread).

State/config helpers (single `threading.Lock` around all):
- `_read_state/_write_state` — read returns dict or `{}` on error; write uses
  `tempfile.NamedTemporaryFile(dir=ROOT, delete=False)` then `os.replace` (atomic on POSIX).
- `bump_state(patch)` — merge patch into current dict, increment `revision`, write, return revision.
- `_read_config/_write_config` writes `{"boot": name_or_null}`.

HTTP handling — subclass `http.server.BaseHTTPRequestHandler`, served by
`http.server.ThreadingHTTPServer`. GET and POST share one `do_GET`/`do_POST` shim that calls one
`handle_request()`.

Parsing (supports both URL forms — `curl` needs the string quoted either way; documented):
```python
parsed = urllib.parse.urlsplit(self.path)
qs = parsed.query
if not qs and parsed.path.lstrip("/").startswith("action="):
    qs = parsed.path.lstrip("/")   # tolerate .../action=update&script=... (the user's literal form)
params = urllib.parse.parse_qs(qs)
```
Reserved keys: `action`, `script`. Repeated `arg` entries → positional argv list. Every remaining
key (e.g. `message=ok`, `seconds=15`) becomes a state patch entry (first value). Missing `action`
(or unknown action) → 404 with `{"error": "..."}` JSON. Unknown script name → 404. Empty script on
switch → 400.

Actions (all respond JSON `application/json`, default 200):
| endpoint | behavior |
|---|---|
| `/action=update&script=NAME&message=ok` | bump_state(optional patch), switch to script (kill current, start new) if given; respond `{"ok":true,"revision":N}` |
| `/action=update&message=ok` (no script) | same state bump but no restart — running script picks up via its own revision poll |
| `/action=switch&script=NAME&arg=x` | kill current, start `NAME` with `arg` values as positional argv; no state bump |
| `/action=stop` | SIGINT child; if alive after 2 s, SIGTERM; if still alive after 2 more s, SIGKILL; set running null (board keeps last frame) |
| `/action=clear` | kill current, then run scripts/clear.py as a short-lived child to blank board |
| `/action=boot&script=NAME` or `&script=none` | `_write_config({"boot": NAME or None})`, respond `{"ok":true,"boot": ...}` |
| `/action=status` (or `/action=scripts`) | see shape below |
| `/` (no action) | serve `index.html` bytes (text/html) or 404 if missing |

`/status` shape (all values from configured files/registry, nothing invented):
```
{"running": "message" | null, "pid": 1234|null, "started": ISO8601|null,
 "boot": "message"|null, "scripts": ["message","timer","unicorn_message",
 "clock", "rainbow", ...sorted], "revision": 7, "log": "..."}
```

`main()`: argparse `--port` (default 80), `--bind` (default 0.0.0.0). On startup: read config
`boot`; if set and present in `scan_scripts()`, start it; if missing/unknown, log warning and
continue (matching every-considered fallback in the plan) — service never exits on a bad boot
script. Serve until SIGTERM (systemd default). No HTTPS, no auth — LAN-only device, per request.

### Step 5 — `index.html`
Single file, no external assets, no build step. Vanilla JS:
- fetches `/action=status` every 5 s and re-renders;
- one running row per script: `Run` button → `fetch('/action=switch?script='+encodeURIComponent(name))`;
- global `Stop` button → `/action=stop`;
- `Clear board` button → `/action=clear`;
- boot picker `<select>` (populated from `scripts` list) + `Save boot` → `/action=boot&script=...`;
- "Send message" `<form>`: text input + number input (seconds, optional), posts
  `/action=update&script=message&message=<text>` (and `&seconds=<n>` → `timer` script) so the curl
  example in README matches what the UI does.
- Small note of current script name, pid, uptime, last log tail in a `<pre>` — keeps the page
  informative without adding a second endpoint.

### Step 6 — `install.sh` (Pi-side, run with sudo)
```sh
#!/bin/sh
set -e
DEST=/opt/xpi
mkdir -p "$DEST"
cp -r server.py index.html scripts "$DEST/"
[ -d "$DEST/repos/microdot-phat" ] || \
  git clone --depth 1 https://github.com/CFBR/microdot-phat "$DEST/repos/microdot-phat"
[ -d "$DEST/repos/unicorn-hat" ] || \
  git clone --depth 1 https://github.com/CFBR/unicorn-hat "$DEST/repos/unicorn-hat"

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
```
User chooses to `User=root` to keep GPIO/SPI/I2C/WS281X access unconditional; otherwise rely on
correct `gpio`/`i2c` group membership. On Pi Zero boot, systemd starts the server, which in turn
starts the saved boot script.

### Step 7 — `README.md`
API table (exact curl commands, note about shell-quoting `?`/`&`), how to add a new script (drop
`myscript.py` in `scripts/`, it appears in the UI on next `/status`), state-file contract
(`{"message": "...", "seconds": 15, "revision": N}`), running the repos' own `install.sh` once on
the Pi to install system deps, memory note (stdlib only, no pip, ~15 MB RSS typical), the exact
example call the user requested:
```
curl "http://<pi-ip>/?action=update&script=message&message=ok"
```
plus a reminder that, without a shell-quoting escape (or use of `-S '--update' style), a leading
`?` syntax can break; the server accepts the lenient `?`-less form too but quoting is safest.

## Verification (dev machine)

Throwaway stub `microdotphat`/`unicornhat` packages (global search-first hit in `PYTHONPATH` because
the child runs with it first). Concrete runnable proof set — write to `/tmp` only:
```python
# /tmp/xfake/microdotphat.py
def write_string(a, **kw): print("M:write_string", a, kw)
def scroll(a=None): print("M:scroll")
def show(): print("M:show")
def clear(): print("M:clear")
def fill(a): print("M:fill", a)

# /tmp/xfake/unicornhat.py
def set_layout(x): print("U:set_layout", x)
def rotation(x): pass
def brightness(x): pass
def get_shape(): return (8, 8)
def set_pixel(x, y, r, g, b): pass
def show(): print("U:show")
def clear(): print("U:clear")
def putpixel(*a, **kw): pass
```
Set `import os; os.environ["AUTO"] = ...` no — simply name the stub module `microdotphat` and the
import-time pattern used in step 3&4 (never imports the real libs; there is no real-lib call site
to shadow).

1. Scaffold: repos cloned (step 1), all listed files present.
2. Raw example URL exactly as user typed it: `curl 'http://127.0.0.1:80/action=update&script=message&message=ok'`
   → JSON `{"ok":true,"revision":1}` and `message.py`'s stdout shows new text (proves both the
   lenient no-`?` form and the restart pipeline).
   Also the conventional form `curl 'http://127.0.0.1:80/?action=update&script=message&message=ok'`
   behaves identically (proven same code path).
3. Fault first: run server with repos dirs temporarily renamed to `_ …` → startup and /status still
   work with ONLY the five shipped scripts; renamed back. Proves no path assumes repos present.
4. Boot persistence: `/action=boot&script=message` → server restarted (`kill` + relaunch) →
   `/status` shows `running":"message"` from the saved config file alone.
5. Unknown script `/action=switch&script=doesnotexist` → HTTP 404 with JSON error.
6. Static page: `curl http://127.0.0.1:80/` includes both "Run" button markup and the stop/clear
   controls; `Content-Type: text/html`.
7. On-Pi manual validation (documented in README, not implementer's job): install.sh, then from
   another machine `curl "http://<pi-ip>/?action=update&script=message&message=ok"`; confirm text
   appears on thousands of pixels / board addressable by the board in question; confirm memory
   `ps -o rss,cmd -p $(pgrep -f 'server.py')` ≤ ~15 MB RSS with page open; confirm logs at
   /var/log/buslog (systemd journal) show no restart loops.

## Assumptions (user can override)
- Boards: server must support BOTH microdot-phat and unicorn-hat scripts simultaneously on the
  filesystem; only one board is physically attached at any given time (auto-retries).
- systemd used for boot (Raspberry Pi OS default). No auth/HTTPS — LAN-trusted.
- User accepts ~15 MB RSS from Python stdlib server, per chosen mechanism; no daemon help.
