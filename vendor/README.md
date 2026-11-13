# Vendored display libraries

xpi ships both Pimoroni display libraries in this folder so a fresh Pi needs
nothing else. Each is a straight copy plus local patches, described below.

| Board | Files | Upstream | Copied from |
|---|---|---|---|
| Micro Dot pHAT | `microdot-phat/microdotphat/` | [pimoroni/microdot-phat](https://github.com/pimoroni/microdot-phat) | `47f9cc35e6ed3523d02b9d5c6453cd7ad3eb73fc`, "Prep for v0.2.2", 2022-02-02 |
| Unicorn HAT/pHAT | `unicorn-hat/unicornhat.py` | [pimoroni/unicorn-hat](https://github.com/pimoroni/unicorn-hat) | `9cb7d9ecadd76715091878ab13467145aebdb0b4`, "Merge pull request #137 from pimoroni/gpl-mit-relicense", 2022-02-09 |

The example sets in `../scripts/microdot-phat/` and `../scripts/unicorn-hat/`
come from the same two commits. Each example has a header naming its upstream
path, and `../scripts/README.md` covers them.

## License

MIT, Copyright (c) 2017 Pimoroni Ltd. The full texts are in `../LICENSES/`:

- `pimoroni-microdot-phat.txt`
- `pimoroni-unicorn-hat.txt`

The disclaimer and warranty terms apply as written. xpi's own license is in
`../LICENSE`.

## Where upstream sends the credit

Pimoroni owns both libraries. The upstream unicorn-hat README credits the LED
driver lineage underneath it:

- [rpi_ws281x](https://github.com/jgarff/rpi_ws281x) by Jeremy Garff
- the modified, Pi 2/3 compatible version of it by Richard Hirst,
  [richardghirst/rpi_ws281x](https://github.com/richardghirst/rpi_ws281x)
- earlier lineage from the ws2812 C driver by 626Pilot,
  [RaspberryPi-NeoPixel-WS2812](https://github.com/626Pilot/RaspberryPi-NeoPixel-WS2812),
  which upstream keeps for posterity only

At runtime `unicornhat.py` imports `rpi_ws281x` from PyPI, the Python binding to
that same library. `install.sh` installs it with pip.

`microdotphat` drives the board over I2C through `smbus2` and carries no third
party display code. Its upstream README lists one unofficial third party
library, a Java client by Jim Darby
([PiJava](https://github.com/hackerjimbo/PiJava)), which xpi does not use.

## The xpi patch

Both libraries carry the same brightness change, marked with `# --- xpi:`:

- `microdotphat/__init__.py` reads `state.json` and scales the brightness of
  every matrix inside `show()`, through `_state_scale()` and `_apply_scale()`.
- `unicornhat.py` does the same through `_state_scale()` and
  `_apply_brightness()`, multiplying the value passed to `set_brightness()`.

That makes the brightness slider work for any script, including the untouched
Pimoroni examples. Scripts can still set their own brightness; `state.json`
scales whatever they set. `_xpi_state.brightness()` gives a script the value
directly when it wants to do its own scaling.

Both `show()` functions also publish the frame they just drew through
`support/_xpi_frame.py`. That block is marked
`# --- xpi: publish the frame for the live viewer`. The server serves it at
`?action=frame`, which is how the page's live viewer follows the real LEDs.
If the helper is missing, the call is ignored and the display still runs.

## Re-syncing with upstream

1. Copy the files from a fresh clone of the upstream repo at the new commit,
   keeping `font.py`, `matrix.py` and `__init__.py` together.
2. Re-apply the blocks marked `# --- xpi:` at the top of `__init__.py` or
   `unicornhat.py`, plus the brightness check and the frame publisher inside
   `show()`.
3. Update the commit column above.
4. Re-copy any changed examples into `../scripts/`. The copies carry a two line
   header, so diff with that in mind.
