"""
OLED Display

Required install driver: micropython-ssd1306 by thonny
https://hellobreak.net/raspberry-pi-pico-oled-i2c-0218/
"""

import ssd1306
from machine import Pin, I2C
from png import Reader
import ubinascii


def png_image_base64_to_monochrome_bits(png_image_base64):
    return png_image_to_monochrome_bits(ubinascii.a2b_base64(png_image_base64))


def is_light(r, g, b):
    """
    :return: RGB Color is dark or not.
    https://stackoverflow.com/a/14331/4617297
    """
    mono = (0.2125 * r) + (0.7154 * g) + (0.0721 * b)
    return 127 < mono


def png_image_to_monochrome_bits(png_image_binary):
    """
    Convert PNG image to monochrome bit list.
    """
    png_reader = Reader(bytes=png_image_binary)
    png_width, png_height, png_rgb_pixels, png_meta = png_reader.asRGB()

    def monochrome_list(rgb_pixels):
        for pixels in rgb_pixels:
            yield [
                is_light(pixels[i], pixels[i + 1], pixels[i + 2])
                for i in range(0, len(pixels), 3)
            ]

    return png_width, png_height, monochrome_list(png_rgb_pixels), png_meta


class Oled:
    """
    SSD1306_I2C OLED Controller Class
    """

    char_height = 8
    char_width = 8

    def __init__(
        self, *, sda_pin=16, scl_pin=17, i2c_freq=400000,
        display_width=128, display_height=64
    ):
        i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=i2c_freq)
        self.oled = ssd1306.SSD1306_I2C(display_width, display_height, i2c)

    def show_text(self, text, *, line_margin=4, auto_return=True):
        self.oled.fill(0)
        if isinstance(text, str):
            text = text.splitlines()
        if auto_return:
            text = self._autoreturn_text(text)
        for i, line in enumerate(text):
            print(line, i, i * (self.char_height + line_margin))
            self.oled.text(line, 0, i * (self.char_height + line_margin))
        self.oled.show()

    def _autoreturn_text(self, text):
        new_text = []
        x_width = self.oled.width // self.char_width
        for line in text:
            new_text += [
                line[i:i + x_width] for i in range(0, len(line), x_width)]
        return new_text

    def show_png_image(self, png_image_base64):
        """
        Show PNG image on center of OLED.
        """
        png_width, png_height, png_monochrome_bits, png_meta = \
            png_image_base64_to_monochrome_bits(png_image_base64)
        self.oled.fill(0)
        for y, png_monochrome_bits_row in enumerate(png_monochrome_bits):
            y_offset = (self.oled.height - png_height) // 2
            for x, png_monochrome_bit in enumerate(png_monochrome_bits_row):
                x_offset = (self.oled.width - png_width) // 2
                fixed_x = x + x_offset
                fixed_y = y + y_offset
                if fixed_x < 0 or self.oled.width <= fixed_x:
                    continue
                if fixed_y < 0 or self.oled.height <= fixed_y:
                    continue
                if png_monochrome_bit:
                    self.oled.pixel(fixed_x, fixed_y, 1)

        self.oled.show()


def _demo():
    """
    Text showing demo code
    """
    import utime
    oled = Oled()
    print('main start')
    oled.show_text('The quick brown \nfox jumps over \nthe lazy dog.')
    utime.sleep(3)
    oled.show_text('The quick brown fox jumps over the lazy dog.',
                   auto_return=True)
    print('main end')


if __name__ == '__main__':
    _demo()
