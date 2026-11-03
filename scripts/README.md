# Scripts

Everything the control page can run lives here. The server scans this folder
and the three board folders below it, so a new file appears on the next page
load.

## xpi scripts

| Script | What it does |
|---|---|
| `message` | Scrolling text from `state.json` `message` |
| `timer` | Countdown from `state.json` `seconds` |
| `hostname` | Scrolls the Pi's hostname on either board |
| `ip` | Scrolls hostname and LAN address on either board |
| `unicorn_message` | Scrolling text in color on a Unicorn board |
| `draw` | Paints a pixel list pushed from the draw panel |
| `solid` | Fills the board with `color`, useful as a lamp or pixel test |
| `clear` | Blanks the attached board |

`_display.py`, `_net.py` and `_xpi_state.py` are helpers imported by those
scripts. The leading `_` keeps them out of the run list.

## Pimoroni examples

Every script from the archived Pimoroni example sets, copied so the page works
without cloning anything else. Each file starts with a comment giving its
original path and license.

- `microdot-phat/`: 12 scripts for the 45x7 monochrome matrix.
- `unicorn-hat/`: scripts for the 16x8 HAT and the 8x4 pHAT.
- `unicorn-hat/hat/`: HAT-only examples plus the `graphics` helper, `lofi.png`
  and the `weather-icons/` assets they need.
- `unicorn-hat/phat/`: pHAT-only examples.

Two files are renamed because the board folders reused a name that already
exists at the top level: `hat/hat-clock.py` and `phat/phat-rainbow.py`.

Optional dependencies:

- `hat/show_png.py` needs Pillow, and `lofi.png` beside it.
- `figlet.py` needs pyfiglet.

Both exit with a message when the module is missing. `weather-icons.py` needs
the `weather-icons/` folder beside it, which it has.

Source: [pimoroni/microdot-phat](https://github.com/pimoroni/microdot-phat)
and [pimoroni/unicorn-hat](https://github.com/pimoroni/unicorn-hat).
Copyright (c) 2017 Pimoroni Ltd, MIT License. The full texts are in
`LICENSES/`.
