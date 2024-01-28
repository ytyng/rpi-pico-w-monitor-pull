"""
Raspberry Pi Pico W E-Paper web client

Polling request to web server that response PNG image.
Display the image on e-paper display.
"""
import machine
import urequests
import network_utils
import network
import settings
from display_adapter import DisplayAdapterBase, get_adapter_by_name
import utime


def main_loop(da: DisplayAdapterBase, wlan: network.WLAN):
    led_pin = machine.Pin('LED', machine.Pin.OUT)
    while True:
        led_pin.on()
        try:
            _one_request(da)
        except Exception as e:
            error_message = f'{e.__class__.__name__}: {e}'
            print(error_message)
            da.error('{}'.format(e))
        led_pin.off()

        if getattr(settings, 'DEEP_SLEEP_SECONDS', None):
            print('Deep sleep for {} seconds.'.format(
                settings.DEEP_SLEEP_SECONDS))
            utime.sleep(1)
            # Disconnect Wi-fi
            wlan.disconnect()
            wlan.active(False)
            # Deactivate Wi-fi
            machine.Pin(23, machine.Pin.OUT).low()
            machine.deepsleep(settings.DEEP_SLEEP_SECONDS * 1000)
            return

        utime.sleep(settings.POLLING_TIME_SECONDS)


def _one_request(da: DisplayAdapterBase):
    response = urequests.get(
        settings.REQUEST_URL,
        headers={
            'User-Agent': settings.REQUEST_HEADER_USER_AGENT,
            'Authorization': settings.REQUEST_HEADER_AUTHORIZATION,
        })
    if response.status_code == 200:
        if response.headers.get('Content-Type') == 'image/png':
            # PNG response
            da.display_png_image(response.content)
            print('Image by binary shown.')
        else:
            # JSON response
            data = response.json()
            if (
                'image' in data and
                data['image']['content_type'] == 'image/png'
            ):
                try:
                    da.display_base64_png_image(data['image']['data'])
                    print('Image by test shown.')
                except Exception as e:
                    print(f'{e.__class__.__name__}: {e}')
            elif 'message' in data:
                da.display_text(data['message'])
                print('Message: {}'.format(data['message']))
    else:
        da.error('{}'.format(response.status_code))
        print('Request failed: {}'.format(response.status_code))


def blink_led(count=3):
    """
    Brink LED 3 times for debugging.
    """
    led_pin = machine.Pin('LED', machine.Pin.OUT)
    for i in range(count):
        led_pin.on()
        utime.sleep(0.2)
        led_pin.off()
        utime.sleep(0.2)


def main():
    machine.Pin(23, machine.Pin.OUT).high()  # Wake up Wi-fy
    blink_led(1)
    print('Booting...')
    da = get_adapter_by_name(settings.DISPLAY_DEVICE)
    da.display_text('Booting...')
    try:
        # wlan = network_utils.prepare_wifi(log=da.display_text)
        wlan = network_utils.prepare_wifi()
    except Exception as e:
        print(f'{e.__class__.__name__}: {e}')
        da.display_text(f'{e.__class__.__name__}: {e}')
        # 10秒がタイムアウトになる場合がある。
        # リセットしたほうが確実
        machine.reset()
        return

    da.display_text('Wifi ready.\n{}'.format(wlan.ifconfig()[0]))
    blink_led()
    main_loop(da, wlan)


if __name__ == '__main__':
    main()
