# xpi

One web page for the LED displays on a Raspberry Pi. Pick a script, send a
message, draw on the grid, set the brightness, and the board follows. xpi
starts on boot and needs no app, no account, and no internet: any browser on
your network will do.

The page runs the bundled scripts and previews what the board shows. It also
draws: drag across the LED grid to light pixels, drag over lit ones to erase,
and send. A brightness slider, a light and dark toggle, and an editor that
loads, saves, uploads and deletes files in `scripts/` sit beside it.

![xpi control page](docs/control-page.png)

It runs with the Pimoroni LED matrix boards:

| Display | Product page | Library |
|---|---|---|
| Micro Dot pHAT, 30x7 red | [shop.pimoroni.com](https://shop.pimoroni.com/products/microdot-phat) | [microdot-phat](https://github.com/pimoroni/microdot-phat) |
| Unicorn HAT, 16x8 RGB | [shop.pimoroni.com](https://shop.pimoroni.com/products/unicorn-hat) | [unicorn-hat](https://github.com/pimoroni/unicorn-hat) |
| Unicorn pHAT, 8x4 RGB | [shop.pimoroni.com](https://shop.pimoroni.com/products/unicorn-phat) | [unicorn-hat](https://github.com/pimoroni/unicorn-hat) |

## Installation

On the Pi:

```sh
git clone https://github.com/CFBR/xpi
cd xpi
sudo ./install.sh
```

The installer prints the page address, usually `http://<hostname>.local/`.
Open it and pick a script.

Copying the folder from a laptop, updating, logs and removal are covered in
[`docs/install.md`](docs/install.md).

## Documentation

| Document | Covers |
|---|---|
| [`docs/install.md`](docs/install.md) | installing from a laptop, updating, uninstall, service and files |
| [`docs/api.md`](docs/api.md) | every action URL, `state.json`, the token, backup and restore |
| [`docs/boards.md`](docs/boards.md) | the three boards, how detection works, script tags |
| [`scripts/README.md`](scripts/README.md) | bundled scripts, adding your own, optional dependencies |
| [`vendor/README.md`](vendor/README.md) | where the display libraries came from and what xpi changed |

## Credits

The display libraries and the bundled example scripts come from Pimoroni Ltd
under the MIT license:
[microdot-phat](https://github.com/pimoroni/microdot-phat) and
[unicorn-hat](https://github.com/pimoroni/unicorn-hat). See
[`vendor/README.md`](vendor/README.md) for the exact commits, and `LICENSES/`
for the license texts. xpi itself is MIT, see `LICENSE`.
