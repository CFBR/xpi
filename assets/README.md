# Icons

`icon.svg` is the source. The raster files are rendered from it.

- `favicon.svg`, `favicon.ico`: browser tab
- `apple-touch-icon.png`: iOS home screen
- `icon-192.png`, `icon-512.png`: app icons

Run `./make-icons.sh` after editing `icon.svg`. It needs `rsvg-convert` and
ImageMagick.
