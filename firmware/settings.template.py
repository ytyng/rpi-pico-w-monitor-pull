"""
Copy this file to settings.py and edit. Secrets go in secrets.py
(copy secrets.template.py).
"""

from secrets import WIFI_PASSWORD, REQUEST_HEADER_AUTHORIZATION  # noqa: F401

# 2.4GHz Wi-fi only
WIFI_SSID = 'YOUR_WIFI_SSID'
COUNTRY = 'YOUR_COUNTRY_CODE'  # JP, US, etc.

REQUEST_URL = 'https://example.com/api/monitor/'
REQUEST_HEADER_USER_AGENT = 'Raspberry Pi Pico W'

DISPLAY_DEVICE = 'SSD1306'  # or 'EPAPER213'
BOOT_DISPLAY = True

# 'polling' | 'deepsleep' | 'tpl5110'  (see power.py)
POWER_MODE = 'polling'
POLLING_TIME_SECONDS = 30
DEEP_SLEEP_SECONDS = 1800
TPL5110_DONE_PIN = 16
