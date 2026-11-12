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
| `image` | Shows an image file, or cycles a folder of them, on a Unicorn board |
| `solid` | Fills the board with `color`, useful as a lamp or pixel test |
| `snake` | Lit snakes crawl down and up the Micro Dot pHAT columns with dark gaps between them |
| `clear` | Blanks the attached board |

`_display.py`, `_net.py` and `_xpi_state.py` are helpers imported by those
scripts. The leading `_` keeps them out of the run list.

`snake` follows the page speed slider like every script. `LENGTH`, `GAP` and
`FRAME` at the top of `snake.py` change the snake size, the space between them
and the default pace.

## Adding a script

Drop a `.py` file onto the page, or use the editor in it. Files land in
`/opt/xpi/scripts/` and show up in the list on the next load. The page tags the
script by what it imports, so it lands on the right board tab; see
[`../docs/boards.md`](../docs/boards.md).

A script just has to drive the board and stop when the server kills it. For
state, `_xpi_state.py` reads `state.json`. For text, `_display.py` has the
shared 3x5 renderer and color parser.

## Pimoroni examples

Every script from the archived Pimoroni example sets, copied so the page works
without cloning anything else. Each file starts with a comment giving its
original path and license. `show_png.py` is the one exception, see the end of
this file.

- `microdot-phat/`: 12 scripts for the Micro Dot pHAT.
- `unicorn-hat/`: scripts for the 16x8 HAT and the 8x4 pHAT.
- `unicorn-hat/hat/`: HAT-only examples plus the `graphics` helper and the
  `weather-icons/` assets they need.
- `unicorn-hat/phat/`: pHAT-only examples.

Two files are renamed because the board folders reused a name that already
exists at the top level: `hat/hat-clock.py` and `phat/phat-rainbow.py`.

Optional dependencies:

- `figlet.py` needs pyfiglet.
- `image` needs Pillow. `install.sh` installs `python3-pil`, so the Pi has it.

Both exit with a message when the module is missing. `weather-icons.py` needs
the `weather-icons/` folder beside it, which it has.

Source: [pimoroni/microdot-phat](https://github.com/pimoroni/microdot-phat)
and [pimoroni/unicorn-hat](https://github.com/pimoroni/unicorn-hat).
Copyright (c) 2017 Pimoroni Ltd, MIT License. The full texts are in
`LICENSES/`. The commit each copy came from is listed in `vendor/README.md`.

The weather icons in `unicorn-hat/hat/weather-icons/` are by LoveBootCaptain,
MIT License. Their `LICENSE` and `README.md` are in that folder.

`image` is xpi's own. It replaces Pimoroni's `show_png.py` example, whose
`lofi.png` sprite is CC BY-NC-SA 3.0 and so cannot ship in an MIT repo.
