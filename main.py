"""
Raspberry Pi Pico Web Server with Microdot and Switch Sample Code.

Pin 14 is used for switch input.
"""
import machine
import urequests
import network_utils
import uasyncio
import settings
from display_adapter import DisplayAdapterBase, DisplayAdapterEPaper213


async def main_loop(da: DisplayAdapterBase):
    led_pin = machine.Pin('LED', machine.Pin.OUT)
    while True:
        led_pin.on()
        # print('Request start: {}'.format(settings.REQUEST_URL))
        response = urequests.get(
            settings.REQUEST_URL,
            headers={
                'User-Agent': settings.REQUEST_HEADER_USER_AGENT,
                'Authorization': settings.REQUEST_HEADER_AUTHORIZATION,
            })
        led_pin.off()
        # print(response.content)
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

        await uasyncio.sleep(15)


async def blink_led(count=3):
    """
    LED を3回点灯させる。
    起動サインに使う
    """
    led_pin = machine.Pin('LED', machine.Pin.OUT)
    for i in range(count):
        led_pin.on()
        await uasyncio.sleep(0.2)
        led_pin.off()
        await uasyncio.sleep(0.2)


async def main():
    da = DisplayAdapterEPaper213()
    print('Booting...')
    wlan = await network_utils.prepare_wifi()
    print('Wifi ready.\n{}'.format(wlan.ifconfig()[0]))
    await blink_led()
    await main_loop(da)


if __name__ == '__main__':
    uasyncio.run(main())
