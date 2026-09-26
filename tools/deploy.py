"""
Copy firmware/ to the Pico W over USB.

    uv run tools/deploy.py            # core files
    uv run tools/deploy.py --libs     # also png.py / pico_e_paper.py (those present)
    uv run tools/deploy.py --no-reset # leave the board at the REPL

The board ignores the REPL while in machine.deepsleep, and a TPL5110 may cut
its power at any moment, so before copying we grab the REPL with Ctrl-C.
If that fails we wait for a USB replug and catch the board during
main.py's startup grace window.
"""
import argparse
import glob
import subprocess
import sys
import time
from pathlib import Path

import serial

FIRMWARE_DIR = Path(__file__).resolve().parent.parent / 'firmware'
CORE_FILES = [
    'main.py',
    'settings.py',
    'network_utils.py',
    'display_adapter.py',
    'power.py',
]
LIB_FILES = ['png.py', 'pico_e_paper.py']

PROMPT = b'>>>'


def find_port() -> str | None:
    ports = sorted(glob.glob('/dev/cu.usbmodem*'))
    return ports[0] if ports else None


def grab_repl(port: str, timeout: float) -> bool:
    """Send Ctrl-C until the REPL prompt shows up."""
    deadline = time.monotonic() + timeout
    buf = b''
    while time.monotonic() < deadline:
        try:
            with serial.Serial(port, 115200, timeout=0.1) as s:
                while time.monotonic() < deadline:
                    s.write(b'\x03')
                    buf += s.read(4096)
                    if PROMPT in buf:
                        return True
        except (serial.SerialException, OSError):
            # The port vanishes for a moment right after a replug.
            time.sleep(0.1)
    return False


def wait_for_replug() -> str:
    print('Board is not responding (deep sleep or powered off).')
    print('>>> Unplug the USB cable and plug it back in.')
    while find_port():
        time.sleep(0.1)
    print('Unplugged. Waiting for the board...')
    while not (port := find_port()):
        time.sleep(0.05)
    print(f'Found {port}')
    return port


def mpremote(port: str, *args: str) -> None:
    cmd = [sys.executable, '-m', 'mpremote', 'connect', port, *args]
    print('$', ' '.join(cmd[2:]))
    subprocess.run(cmd, check=True, timeout=120)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    parser.add_argument('--libs', action='store_true',
                        help='also copy png.py / pico_e_paper.py if present')
    parser.add_argument('--no-reset', action='store_true',
                        help='do not reset the board after copying')
    args = parser.parse_args()

    missing = [f for f in CORE_FILES if not (FIRMWARE_DIR / f).exists()]
    if missing:
        print(f'Missing in {FIRMWARE_DIR}: {", ".join(missing)}')
        return 1
    files = list(CORE_FILES)
    if args.libs:
        # An OLED unit has no pico_e_paper.py; copy whichever libs exist.
        for f in LIB_FILES:
            if (FIRMWARE_DIR / f).exists():
                files.append(f)
            else:
                print(f'Skipping {f} (not in {FIRMWARE_DIR})')

    port = find_port()
    if port is None:
        print('No /dev/cu.usbmodem* device. Is the Pico plugged in?')
        return 1

    if not grab_repl(port, timeout=3):
        port = wait_for_replug()
        if not grab_repl(port, timeout=20):
            print('Still no REPL. Hold BOOTSEL while plugging in and '
                  'reflash MicroPython, or check main.py for a hang.')
            return 1
    print('REPL ready.')

    mpremote(port, 'cp', *[str(FIRMWARE_DIR / f) for f in files], ':')
    if not args.no_reset:
        mpremote(port, 'reset')
    print('Done.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
