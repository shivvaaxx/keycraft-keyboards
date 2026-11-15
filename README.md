# Keycraft Keyboards

The keyboard layout library used by [Keycraft](https://github.com/shivvaaxx), a free, open-source Mac app
for changing what the keys on your keyboard do.

Each file in `keyboards/<maker>/` describes one keyboard: its name, USB vendor and product ID, key
matrix, and physical layout, in the [VIA definition format](https://www.caniusevia.com/docs/specification).
Keycraft downloads the built library automatically, so keyboards added here reach every user
without an app update.

## Adding a keyboard

**From Keycraft:** connect the keyboard, load its VIA layout file, and choose **Share**. Keycraft
opens a pull request here for you.

**By hand:** add `keyboards/<maker>/<keyboard-name>.json` and open a pull request. A check runs
`python3 scripts/build.py --check` and tells you exactly what to fix.

A layout file must have a `name`, `vendorId` and `productId` (hex strings like `"0x3434"`), a
`matrix` with `rows` and `cols`, and `layouts.keymap` whose keys use `"row,col"` positions inside
that matrix. One file per vendor/product ID pair.

Every pull request is reviewed before it is merged, because a wrong layout affects everyone with
that keyboard.

## How the library is built

On every merge to `main`, GitHub Actions runs `scripts/build.py` and publishes two files to the
[`db-latest` release](../../releases/tag/db-latest):

- `via-keyboards.zlib`: all layouts as one raw-deflate compressed JSON file
- `manifest.json`: build date, keyboard count, download URL and SHA-256 checksum

Keycraft checks the manifest at most once a day and verifies the checksum before using a download.

## Credits and license

The initial 2,032 layouts were imported from [the-via/keyboards](https://github.com/the-via/keyboards)
(commit `9e3e9f4aa9f5`) with `scripts/import-via.py`, unchanged. Thank you to the VIA team and every
keyboard maker who contributed there.

This repository is licensed under the GNU General Public License v3.0, the same license as
the-via/keyboards. See [LICENSE](LICENSE).
