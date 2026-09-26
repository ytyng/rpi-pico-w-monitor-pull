# rpi-pico-w-monitor-pull

![画像](https://media.ytyng.com/20230121/0a9b08a399784778a8ecc7658325dd25.jpg)

Raspberry Pi Pico W polls a web server and shows the returned PNG / text on an
e-paper or OLED display.

## Layout

| Path | What |
|---|---|
| `firmware/` | MicroPython code copied to the Pico |
| `tools/` | Mac-side helpers (deploy, serial console) |
| `pyproject.toml` | uv project for the Mac-side tools (Python 3.14) |

## Firmware setup

```
cp firmware/settings.template.py firmware/settings.py   # then edit
```

Third-party modules to drop into `firmware/` (git-ignored):

- `png.py` from https://github.com/Ratfink/micropython-png
- `pico_e_paper.py` = `Pico_ePaper-2.13_V3.py` from
  https://github.com/waveshare/Pico_ePaper_Code/tree/main/python (e-paper only)

Installed on the board with `upip` (the board runs MicroPython v1.19.1, which has no `mip`): `urequests`, `micropython_itertools`,
`micropython_ssd1306` (OLED only).

## Power modes (`POWER_MODE` in settings.py)

| Mode | Between requests | Notes |
|---|---|---|
| `polling` | `utime.sleep(POLLING_TIME_SECONDS)` | Wi-Fi stays up |
| `deepsleep` | `machine.deepsleep(DEEP_SLEEP_SECONDS * 1000)` | REPL is dead while asleep; deploy needs a USB replug. Board resets on wake |
| `tpl5110` | pulse DONE on `TPL5110_DONE_PIN` (GP16) | TPL5110 cuts power; its resistor sets the interval. If power is not cut (USB attached) it falls back to `polling` |

An unknown `POWER_MODE` stops `main.py` at boot with a `ValueError`. If Wi-Fi setup
fails, `tpl5110` mode pulses DONE before resetting, so the TPL5110 retries next period
instead of the board reboot-looping with Wi-Fi on.

TPL5110 wiring: TPL5110 `DRV` → Pico `VSYS`, `GND` → `GND`, `DONE` ← Pico `GP16`.
`POLLING_TIME_SECONDS` in this mode is only the USB fallback interval.

## Deploy

```
uv sync
uv run tools/deploy.py          # main.py settings.py network_utils.py display_adapter.py power.py
uv run tools/deploy.py --libs   # + png.py, pico_e_paper.py (those present)
```

`main.py` waits `STARTUP_GRACE_SECONDS` (3 s) after boot. `deploy.py` sends
Ctrl-C to take the REPL; if the board does not answer (deep sleep), it asks you to
replug the USB cable and catches the board in that window.

Serial console: `tools/connect-tty.sh` (`screen`, quit with `C-a k y`).
