# AGENTS.md

MicroPython firmware for a Raspberry Pi Pico W that polls a web server and draws
the response on an e-paper (Waveshare 2.13 V3) or OLED (SSD1306) display.

## Layout

- `firmware/` — everything copied to the Pico. No Mac-side code here.
- `tools/deploy.py` — copies `firmware/` to the board with `mpremote`.
- `tools/connect-tty.sh` — `screen` serial console.
- `pyproject.toml` / `uv.lock` — Mac-side tools only (Python 3.14, uv). The firmware
  has no dependency management; third-party modules are dropped into `firmware/`.

## Git-ignored local files

`firmware/settings.py`, `firmware/png.py`, `firmware/pico_e_paper.py` exist only
locally. Move them with `mv`, not `git mv`. Never print `settings.py` in full; it
holds the Wi-Fi password and API token.

## settings.py

Branches on `DEVICE_ID` (`machine.unique_id()`), so one file serves every unit.
Known units are listed as comments in `settings.py`. `settings.template.py` is the
committed reference; keep both in sync when adding a setting.

## Power modes

`POWER_MODE` selects what `firmware/power.py` does between requests:
`polling`, `deepsleep`, `tpl5110` (DONE pulse on GP16). Details in README.

## Deploying

```
uv run tools/deploy.py          # core files, then reset
uv run tools/deploy.py --libs   # also png.py / pico_e_paper.py
```

Gotchas:

- In `deepsleep` mode the board shows up on USB but ignores the REPL, so any
  `mpremote` / `ampy` call hangs forever. `deploy.py` detects this, asks for a USB
  replug, and interrupts `main.py` during its 3 s startup grace window. Do not
  remove `STARTUP_GRACE_SECONDS` from `main.py`.
- Only one process can hold `/dev/cu.usbmodem*`. If a command hangs, `lsof` the
  port before retrying.
- Board firmware is MicroPython v1.19.1 (2023). Avoid APIs newer than that.
- On RP2040 `machine.deepsleep()` resets the board on wake; code after it never runs.
- GPIO in use: e-paper 8–13 (SPI1), OLED 20/21 (I2C0), TPL5110 DONE 16, CYW43 power 23.

## Verifying on hardware

After a deploy, read the serial port (pyserial, 115200) for ~40 s. A healthy boot
prints `Wi-fi ready`, then `Image by ... shown.`. `deepsleep` then prints
`Deep sleep for N seconds.`; `tpl5110` prints `TPL5110 DONE on GP16.` and, with USB
attached, `Still powered after DONE; falling back to polling.`; `polling` prints nothing.
