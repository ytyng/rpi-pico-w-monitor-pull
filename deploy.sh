#!/usr/bin/env zsh

export AMPY_PORT=$(ls -1 /dev/tty.usbmodem* |head -n 1)
killall SCREEN 2>/dev/null

ampy put main.py /main.py
ampy put settings.py /settings.py
ampy put network_utils.py /network_utils.py
ampy put display_adapter.py /display_adapter.py
