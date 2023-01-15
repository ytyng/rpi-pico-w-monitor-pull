"""
OLED ディスプレイ

ドライバ: micropython-ssd1306 を thonny でインストールする
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
    RGB Color is dark or not.
    https://stackoverflow.com/a/14331/4617297
    """
    mono = (0.2125 * r) + (0.7154 * g) + (0.0721 * b)
    return 127 < mono


def png_image_to_monochrome_bits(png_image_binary):
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

    def __init__(self):
        i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
        # i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
        self.oled = ssd1306.SSD1306_I2C(128, 64, i2c)

    def show_demo_text(self):
        self.oled.text("RP2 HC-SR04 TEST", 0, 8)
        self.oled.text("TEMP:      C", 18, 24)
        self.oled.text("L(cm):", 18, 40)
        self.oled.show()
        self.oled.fill_rect(72, 24, 32, 8, 0)
        self.oled.show()
        self.oled.text('1111', 72, 24)
        self.oled.show()
        self.oled.fill_rect(72, 40, 56, 8, 0)
        self.oled.show()
        self.oled.text(str('2222'), 72, 40, )
        self.oled.show()

    def show_png_image(self, png_image_base64):
        png_width, png_height, png_monochrome_bits, png_meta = \
            png_image_base64_to_monochrome_bits(png_image_base64)
        self.oled.fill(0)
        for y, png_monochrome_bits_row in enumerate(png_monochrome_bits):
            for x, png_monochrome_bit in enumerate(png_monochrome_bits_row):
                if png_monochrome_bit:
                    self.oled.pixel(x, y, 1)

        self.oled.show()


png_image_base64 = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAASUExURbZNTd+ysv+Kiv///5YAAP///6XEBjAAAAAGdFJOU///////ALO/pL8AAAB5SURBVHjaYmBlZWWBAyAHIIAY0AUAAggiwAwGYAGAAIIIMIEBWAAggDAEAAIIQwAggDDMAAggDAGAAMIQAAggDAGAAMIQAAggmAAjI1QAIICgAowsLIwQAYAAgggwgjzCCBYACCCY5xgYoJ4DCCCIAIhkZQALAAQYAB2YA/Vl3FceAAAAAElFTkSuQmCC"


if __name__ == '__main__':
    print('start oled main.')
    oled = Oled()
    oled.show_png_image(png_image_base64)
