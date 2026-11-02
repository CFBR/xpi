# Pimoroni examples

Every script from the archived Pimoroni example sets, copied into this repo so
the control page works without cloning anything else. Each file starts with a
comment giving its original path and license.

- `microdot-phat/`: 13 scripts for the 45x7 monochrome matrix.
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

Source: [CFBR/microdot-phat](https://github.com/CFBR/microdot-phat) and
[CFBR/unicorn-hat](https://github.com/CFBR/unicorn-hat), forks of Pimoroni's
repos. Copyright (c) 2017 Pimoroni Ltd, MIT License. The full texts are in
`LICENSES/`.
