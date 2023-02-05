"""
Raspberry Pi Pico W E-Paper web client

Polling request to web server that response PNG image.
Display the image on e-paper display.
"""
import machine
import urequests
import network_utils
import settings
from display_adapter import DisplayAdapterBase, get_adapter_by_name
import utime

def main_loop(da: DisplayAdapterBase):
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

        utime.sleep(settings.POLLING_TIME_SECONDS)


def _one_request(da: DisplayAdapterBase):
    response = urequests.get(
        settings.REQUEST_URL,
        headers={
            'User-Agent': settings.REQUEST_HEADER_USER_AGENT,
            'Authorization': settings.REQUEST_HEADER_AUTHORIZATION,
        })
    if response.status_code == 200:
        data = response.json()
        if (
            'image' in data and
            data['image']['content_type'] == 'image/png'
        ):
            try:
                da.display_png_image(data['image']['data'])
                print('Image shown.')
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
    blink_led(1)
    print('Booting...')
    da = get_adapter_by_name(settings.DISPLAY_DEVICE)
    da.display_text('Booting...')
    wlan = network_utils.prepare_wifi(log=da.display_text)
    da.display_text('Wifi ready.\n{}'.format(wlan.ifconfig()[0]))
    blink_led()
    main_loop(da)


if __name__ == '__main__':
    main()
