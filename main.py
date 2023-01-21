"""
Raspberry Pi Pico Web Server with Microdot and Switch Sample Code.

Pin 14 is used for switch input.
"""
import machine
import urequests
import network_utils
import uasyncio
import settings
from oled import Oled


async def main_loop():
    led_pin = machine.Pin('LED', machine.Pin.OUT)
    oled = Oled()
    while True:
        led_pin.on()
        print('Request start: {}'.format(settings.REQUEST_URL))
        response = urequests.get(
            settings.REQUEST_URL,
            headers={
                'User-Agent': settings.REQUEST_HEADER_USER_AGENT,
                'Authorization': settings.REQUEST_HEADER_AUTHORIZATION,
            })
        led_pin.off()
        print(response.content)
        if response.status_code == 200:
            data = response.json()
            if (
                'image' in data and
                data['image']['content_type'] == 'image/png'
            ):
                try:
                    oled.show_png_image(data['image']['data'])
                    print('Image shown.')
                except Exception as e:
                    print(f'{e.__class__.__name__}: {e}')
            elif 'message' in data:
                oled.show_text(data['message'])
                print('Message: {}'.format(data['message']))

        await uasyncio.sleep(15)


async def blink_led():
    """
    LED を3回点灯させる。
    起動サインに使う
    """
    led_pin = machine.Pin('LED', machine.Pin.OUT)
    for i in range(3):
        led_pin.on()
        await uasyncio.sleep(0.2)
        led_pin.off()
        await uasyncio.sleep(0.2)


async def main():
    wlan = await network_utils.prepare_wifi()
    print('Wifi ready. {}'.format(wlan.ifconfig()[0]))
    await blink_led()
    await main_loop()


if __name__ == '__main__':
    uasyncio.run(main())
