# Boards

xpi drives one of these Pimoroni LED matrix boards at a time.

| Board | Size | Color | How xpi finds it |
|---|---|---|---|
| [Micro Dot pHAT](https://shop.pimoroni.com/products/microdot-phat) | 30x7 visible, 45x7 in the library buffer | red | Exact. Its I2C chips answer at `0x61`, `0x62`, `0x63` |
| [Unicorn HAT](https://shop.pimoroni.com/products/unicorn-hat) | 16x8 | RGB | Exact. The HAT EEPROM carries the product string |
| [Unicorn pHAT](https://shop.pimoroni.com/products/unicorn-phat) | 8x4 | RGB | Inferred, since the pHAT has no EEPROM |

The Micro Dot pHAT pads three columns between its six 5x7 matrices, so the
library reports 45 columns for 30 visible pixels. `microdotphat.WIDTH` and
`HEIGHT` are the numbers a script should use.

The page shows the detected board as the open tab and labels an inferred one as
such in `?action=status`:

```json
{"attached": "unicorn phat (inferred)"}
```

## Script tags

A script is tagged by the folder it sits in, or by what it imports when it sits
at the top of `scripts/`:

- `microdot-phat` when it imports `microdotphat`
- `unicorn-hat` when it imports `unicornhat`
- `both` when it handles either board, like `draw` and `clear`
- `generic` when it imports neither, so the page cannot tell

The folder tags are finer: `unicorn-hat 16x8` for `scripts/unicorn-hat/hat/`,
`unicorn phat 8x4` for `scripts/unicorn-hat/phat/`, and `microdot-phat` for
`scripts/microdot-phat/`. A file sitting directly in `scripts/unicorn-hat/` is
tagged `unicorn-hat`, which the page shows on either Unicorn tab. Each tab lists
what fits that board, so a microdot script never appears on a Unicorn tab and
the other way round.

## What a script may assume

- `unicornhat` is on `sys.path` for Unicorn boards, `microdotphat` for the
  Micro Dot pHAT. Both come from `vendor/`, not from pip.
- The display size is whatever the library reports: `get_shape()` on a Unicorn
  board, `microdotphat.WIDTH` and `HEIGHT` on the Micro Dot pHAT. Do not
  hardcode it if the script can work on more than one board.
- Brightness from `state.json` is applied inside `show()` by both vendored
  libraries. A script can set its own brightness and the slider still scales it.
- `time.sleep` is scaled by `state.json` `speed` for every script, through
  `support/sitecustomize.py`.

The Unicorn boards need root because the driver writes to `/dev/mem`. The
installer runs the service as root for that reason.
