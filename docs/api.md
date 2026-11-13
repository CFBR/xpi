# The xpi API

The control page and the API are the same thing. Every button is a URL, so the
address bar shows what you did. A browser gets the page at `/`, anything else
gets JSON.

```
http://<pi-ip>/?action=switch&script=rainbow
```

Quote the whole URL in a shell, because `?` and `&` are shell metacharacters.

## Actions

| Action | What it does |
|---|---|
| `?action=switch&script=<name>` | Stop the running script and start this one |
| `?action=update&script=message&message=hello` | Change state, then restart the named script |
| `?action=update&message=hi` | Change state only. The running script picks it up without a restart |
| `?action=update&brightness=0.4` | Brightness, 0 to 1, on either board |
| `?action=update&speed=2.0` | Scale `time.sleep` for any script, including the Pimoroni examples |
| `?action=update&color=red` | Text or fill color, by name or `#RRGGBB` |
| `?action=stop` | Kill the script. Its last frame stays on the board |
| `?action=clear` | Kill the script and blank the board |
| `?action=boot&script=<name>` | Set the script that starts with the service. `none` unsets it |
| `?action=playlist&scripts=a,b&seconds=60` | Rotate scripts every N seconds. Empty `scripts` clears it |
| `?action=savegroup&name=<name>&scripts=a,b&seconds=60` | Create or replace a named rotation group |
| `?action=delgroup&name=<name>` | Delete a group |
| `?action=playgroup&name=<name>` | Rotate through a saved group |
| `?action=stopgroup` | Stop group rotation |
| `?action=saventfy&url=<base>&topic=<topic>&token=<token>&start=1` | Save ntfy settings and optionally start the alert listener |
| `?action=status` | Attached board, running script, pid, boot, scripts, boards, ip, revision, log. `?action=scripts` is an alias |
| `?action=state` | The current `state.json` |
| `?action=health` | CPU temperature, load, memory, disk, uptime and throttle |
| `?action=frame` | The last frame the display libraries showed, for the live viewer |
| `?action=getscript&script=<name>` | The script's source, as `{"script": ..., "code": ...}` |
| `?action=savescript&script=<name>` | Write the POST body to that script. Must parse as Python |
| `?action=delscript&script=<name>` | Delete a script from `scripts/`. The `_` helpers are protected |
| `?action=savedrawing&script=<name>` | Save the POSTed pixel list as a script |
| `?action=backup` | JSON of version, config, state and every script |
| `?action=restore` | Write a backup JSON back. POST the body |

Pass positional arguments to a script by repeating the parameter:

```
?action=switch&script=image&arg=/opt/xpi/images/logo.png
?action=switch&script=clock&arg=one&arg=two
```

## Replies and errors

A reply is JSON. Unknown actions and scripts give `404`, missing parameters
`400`, a rejected token `401`, and a handler failure `500`. The body carries an
`error` key:

```json
{"error": "unknown script", "script": "rainbo"}
```

## state.json

```json
{"message": "...", "seconds": 15, "brightness": 0.5, "speed": 1.0, "color": "red", "revision": 17}
```

`update` writes every parameter except `script` and `arg` into the state, so
the set of keys grows with what your scripts need. It also increments
`revision`.

Scripts stay live without a restart by polling `revision()` from
`scripts/_xpi_state.py`, then reading the values they care about through
`value()`.

`brightness` scales whatever the running script sets, on either board.
`speed` divides the delay in `time.sleep`, for any script, including the
untouched Pimoroni examples.

A group is a named script list with its own seconds. `playgroup` sets it
active, and the server rotates through it in order. `stopgroup` clears the
active group and leaves the current script running. A group overrides the
older `playlist` keys until it is stopped.

## ntfy alerts

`saventfy` writes `config.json` `ntfy` with `url`, `topic` and an optional
`token`. The token is not returned by status or stored in `state.json`.
`start=1` also starts `ntfy`, which subscribes to `<url>/<topic>/json`
and clears any active group so the rotation cannot replace it.
High-priority messages flash, then scroll. After `ntfy_hold` seconds
(default 20) the display returns to a clock.

Apprise can publish to the same topic through its ntfy target, so one
subscription covers every service that forwards there.

## Live frame

The vendored `show()` functions publish the last frame to a small file in the
system temp directory. `?action=frame` returns it, so the page can draw the
actual LEDs instead of guessing from `state.json`. Micro Dot frames carry
`rows`, seven strings of 30 ones and zeros. Unicorn frames carry `width`,
`height`, and base64 RGB `data`. `age` is the seconds since the last write.
If no frame has been published, the reply is `{"available": false}`.

The page polls this action about four times a second and pauses while the tab
is hidden. The display libraries throttle writes, so a static frame is not
rewritten on every `show()`.

## Colors

Names: `red`, `green`, `blue`, `white`, `yellow`, `orange`, `purple`,
`magenta`, `cyan`, `pink`. Otherwise `#RRGGBB` or `RRGGBB`, with a three digit
short form allowed.

## Pixel lists

`savedrawing` takes a JSON list of pixels, in the same shape the draw panel
sends:

```json
[[0, 0, "#FF0000"], [1, 0, "#00FF00"]]
```

Each entry is `[x, y, color]` for a Unicorn board, or `[x, y]` for a
microdot-phat, where anything listed is lit. It saves to a script named by
`script=`, which you can then run like any other.

## Token

Set a `token` in `/opt/xpi/config.json` to protect the actions that write or
stop:

```json
{"boot": "clock", "token": "your-secret"}
```

Guarded: `stop`, `boot`, `playlist`, `savegroup`, `delgroup`, `playgroup`,
`stopgroup`, `saventfy`, `savescript`, `delscript`, `savedrawing`, `backup`
and `restore`. Send it as `?token=...` or in an `X-XPI-Token` header.
The page asks once and keeps it in the browser. `status`, `state`, and `frame`
are readable without the token.

## Backup and restore

`?action=backup` returns one JSON object:

```json
{"version": "2.9.1", "config": {}, "state": {}, "scripts": {"rain.py": "..."}}
```

POST it back to `?action=restore` to write the scripts and config in. Useful
before an update, or for copying a setup to a second Pi.
