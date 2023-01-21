import framebuf
from machine import Pin, I2C
import utime
import ubinascii

try:
    from png import Reader
except ImportError:
    print('png module not found.\n'
          'Download: https://github.com/Ratfink/micropython-png png.py '
          'to project root directory.')
    raise


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

    def display_png_image(self, png_image_base64):
        """
        Show PNG image on center of display.
        """
        png_width, png_height, png_monochrome_bits, png_meta = \
            png_image_base64_to_monochrome_bits(png_image_base64)
        self._framebuf.fill(self.bg_color)
        _bg_is_dark = not self.bg_color
        for y, png_monochrome_bits_row in enumerate(png_monochrome_bits):
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
    SDA_PIN = 16
    SCL_PIN = 17
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
        # return self._framebuf.width  # 128. It's error.
        return 122


png_image_base64 = b'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'


def _demo():
    adapter = DisplayAdapterEPaper213()
    print('step1')
    adapter.display_text([
        'hello, world.',
        'I am a e-paper display.',
        'Width: {}, Height: {}'.format(
            adapter.width, adapter.height)])
    utime.sleep(5)
    adapter.display_png_image(png_image_base64)
    print('end.')


if __name__ == '__main__':
    _demo()
