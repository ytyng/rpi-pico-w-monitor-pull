"""
Copy this file to settings.py and fill in your Wi-Fi credentials.
"""

# 2.4GHz Wi-fi only
WIFI_SSID = 'YOUR_WIFI_SSID'
WIFI_PASSWORD = 'YOUR_WIFI_PASSWORD'
COUNTRY = 'YOUR_COUNTRY_CODE'  # JP, US, etc.

REQUEST_URL = 'https://example.com/api/monitor/'
REQUEST_HEADER_AUTHORIZATION = 'Token YOUR_TOKEN'
REQUEST_HEADER_USER_AGENT = 'Raspberry Pi Pico W'

DISPLAY_DEVICE = 'SSD1306'  # or 'EPAPER213'
BOOT_DISPLAY = True

# 'polling' | 'deepsleep' | 'tpl5110'  (see power.py)
POWER_MODE = 'polling'
POLLING_TIME_SECONDS = 30
DEEP_SLEEP_SECONDS = 1800
TPL5110_DONE_PIN = 16
