#!/usr/bin/env zsh

echo "終了するには c-a k y"
echo "開けない場合は一度ケーブルを抜き差しする"
sleep 1

port=$(ls -1 /dev/tty.usbmodem* |head -n 1)
killall SCREEN 2>/dev/null

screen $port
