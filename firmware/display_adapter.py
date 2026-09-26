import framebuf
import utime
from machine import Pin, I2C
import ubinascii

try:
    from png import Reader
except ImportError:
    print('png module not found.\n'
          'Download: https://github.com/Ratfink/micropython-png png.py '
          'to project root directory.')
    raise


class DisplayAdapterBase:
    char_height = 8
    char_width = 8
    bg_color = 0
    fg_color = 1
    text_y_offset = 0

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._framebuf = self._create_framebuf()

    def _create_framebuf(self) -> framebuf.FrameBuffer:
        raise NotImplementedError()

    def _refresh(self):
        # not implemented.
        pass

    @property
    def width(self) -> int:
        """
        Device width pixels.
        """
        return self._framebuf.width

    @property
    def height(self) -> int:
        """
        Device height pixels.
        """
        return self._framebuf.height

    def log(self, message):
        print(message)

    def display_text(self, text, *, line_margin=4, auto_return=True):
        """
        :param text:
        :param line_margin:
        :param auto_return:
        :return:
        """
        self._framebuf.fill(self.bg_color)
        if isinstance(text, str):
            text = text.splitlines()
        if auto_return:
            text = self._auto_return_text(text)
        for i, line in enumerate(text):
            self.log('{}, {}'.format(
                line, i, i * (self.char_height + line_margin)))
            self._framebuf.text(
                line, 0,
                i * (self.char_height + line_margin) + self.text_y_offset,
                self.fg_color)
        self._refresh()

    def _auto_return_text(self, text):
        new_text = []
        x_width = self.width // self.char_width
        for line in text:
            new_text += [
                line[i:i + x_width] for i in range(0, len(line), x_width)]
        return new_text

    def error(self, message):
        self.display_text(f'[ERROR] {message}')

    def display_base64_png_image(self, png_image_base64: bytes):
        self.display_png_image(ubinascii.a2b_base64(png_image_base64))

    def display_png_image(self, png_image: bytes):
        """
        Show PNG image on center of display.

        Support only 1-bit monochrome PNG image.
        """
        try:
            reader = Reader(bytes=png_image)
        except Exception as e:
            self.error('Invalid png data: {} {}'.format(
                e.__class__.__name__, e))
            return

        png_width, png_height, pixels, png_meta = reader.asDirect()

        if not png_meta['greyscale']:
            self.error('PNG is not greyscale image.')
            return

        if png_meta['alpha']:
            self.error('PNG with alpha is not supported.')
            return

        if png_meta['bitdepth'] != 1:
            self.error('PNG bitdepth is not 1.')
            return

        self._framebuf.fill(self.bg_color)
        _bg_is_dark = not self.bg_color
        for y, png_monochrome_bits_row in enumerate(pixels):
            y_offset = (self.height - png_height) // 2
            for x, png_monochrome_bit in enumerate(png_monochrome_bits_row):
                x_offset = (self.width - png_width) // 2
                fixed_x = x + x_offset
                fixed_y = y + y_offset
                if fixed_x < 0 or self.width <= fixed_x:
                    continue
                if fixed_y < 0 or self.height <= fixed_y:
                    continue
                if _bg_is_dark and png_monochrome_bit:
                    self._framebuf.pixel(fixed_x, fixed_y, self.fg_color)
                elif not _bg_is_dark and not png_monochrome_bit:
                    self._framebuf.pixel(fixed_x, fixed_y, self.fg_color)

        self._refresh()


class DisplayAdapterSSD1306(DisplayAdapterBase):
    """
    SSD1306_I2C OLED Controller Class
    """
    # SDA_PIN = 16
    # SCL_PIN = 17
    SDA_PIN = 20
    SCL_PIN = 21
    I2C_FREQ = 400000
    DISPLAY_WIDTH = 128
    DISPLAY_HEIGHT = 64

    def _create_framebuf(self) -> framebuf.FrameBuffer:
        import ssd1306
        i2c = I2C(
            0, sda=Pin(self.SDA_PIN), scl=Pin(self.SCL_PIN),
            freq=self.I2C_FREQ)
        return ssd1306.SSD1306_I2C(
            self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT, i2c)

    def _refresh(self):
        self._framebuf.show()


class DisplayAdapterEPaper213(DisplayAdapterBase):
    """
    e-paper 2.13inch display

    https://www.waveshare.com/wiki/Pico-ePaper-2.13

    Required: Download https://github.com/waveshare/Pico_ePaper_Code/blob/main/python/Pico_ePaper-2.13_V3.py
    as pico_e_paper.py
    """
    bg_color = 1
    fg_color = 0
    text_y_offset = 8

    def _create_framebuf(self) -> framebuf.FrameBuffer:
        from pico_e_paper import EPD_2in13_V3_Landscape
        return EPD_2in13_V3_Landscape()

    def _refresh(self):
        self._framebuf.display(self._framebuf.buffer)

    @property
    def width(self):
        return self._framebuf.height

    @property
    def height(self):
        return self._framebuf.width


def get_adapter_class_by_name(name: str):
    """
    :param name: Display adapter name.
    :return: Display adapter class.
    """
    upper_name = name.upper()
    if upper_name == 'SSD1306':
        return DisplayAdapterSSD1306
    elif upper_name == 'EPAPER213':
        return DisplayAdapterEPaper213
    raise ValueError('Unknown display adapter: {}'.format(name))


def get_adapter_by_name(name: str) -> DisplayAdapterBase:
    """
    :param name: Display adapter name. SSD1306 | EPAPER213
    :return: Display adapter instance.
    """
    return get_adapter_class_by_name(name)()


png_image_base64 = b'iVBORw0KGgoAAAANSUhEUgAAAIAAAABAAQAAAAD6rULSAAABe0lEQVR4nM2TvUtCYRTGj1+UOlgY1dYHFwwXGxsCJYIKSWxqif6Ippao1SmiwYiiSWoIbHSroaWCCKOhgjAXKUpu5kem930arr73vI619C738uM8z3Pec+61gdRjp9+DpRPzaWuZNp2GQ6lwUmXYfEP7nKcBAE7p9uTikipR6ZiDLNH7HQc3RLfLEQYyRNdXEZYSAhKeMAC0wCmgxTcZAMScK6T2cR8NK502tzyLTLKOurbgs4AA9IR2qJi+jk4NAIAcUC2QXbU6FUTux3LGHEwL14q7H1ZsA7ic7YsCQHumlCr6Vt54Re+aZ4bHigSeR3isuDjzB/ldDHd+3m9JPqGnmsmCBRp48Bs+WB5VSk5imm2uLMoheFmFCFfGscP2ImL1nO2ISb4DL8A2k9TG+okmmMShE9Egk5QO5GdiVthzcj3mxGKGBHYiIlGISEAAoG8MSQ8CgEowrYJ8T5eaUtyPqx4wvJ197KmxRJoErUV9dXcA6/zlF/tv4AfY1mEuwRaXpQAAAABJRU5ErkJggg=='  # NOQA


def _demo():
    # adapter = DisplayAdapterEPaper213()
    adapter = DisplayAdapterSSD1306()
    print('step1')
    adapter.display_text([
        'hello, world.',
        # 'I am a e-paper display.',
        'Width: {}, Height: {}'.format(
            adapter.width, adapter.height)])
    utime.sleep(5)
    adapter.display_base64_png_image(png_image_base64)
    print('end.')


if __name__ == '__main__':
    _demo()
