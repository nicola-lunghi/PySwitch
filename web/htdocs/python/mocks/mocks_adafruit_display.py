import re

class MockDisplayIO:
    class Group(list):
        def __init__(self, x = 0, y = 0, scale = 1):
            self.x = x
            self.y = y
            self.__scale = scale

        @property
        def scale(self):        
            return self.__scale
        
        @scale.setter
        def scale(self, s):
            self.__scale = s
            
        def __add__(self, *args, **kwargs):
            return MockDisplayIO.Group(super().__add__(*args, **kwargs))
        
        def render(self, canvas, x, y):
            for item in self:
                item.render(canvas, x + self.x, y + self.y)

    class Palette(list):
        def __init__(self, color_count, dither = False):
            while len(self) < color_count:
                self.append(None)

        def __add__(self, *args, **kwargs):
            return MockDisplayIO.Palette(super().__add__(*args, **kwargs))

        def make_opaque(self, index):
            pass

        def make_transparent(self, index):
            pass

    class Bitmap:
        def __init__(self, width, height, value_count):
            pass

    class TileGrid:
        def __init__(self, bitmap, pixel_shader, width = 1, height = 1, tile_width = None, tile_height = None, default_tile = 0, x = 0, y = 0):
            pass

    class FourWire:
        def __init__(self, spi, command, chip_select, reset):
            pass

    def release_displays():
        pass


class MockBusIO:
    class SPI:
        def __init__(self, clk, MOSI):
            pass

        def try_lock(self):
            return True
        
        def unlock(self):
            pass
        
        def configure(self, baudrate):
            pass


class MockAdafruit_ST7789:
    class ST7789:
        def __init__(self, display_bus, width, height, rowstart, rotation):
            pass
    

class MockAdafruitDisplayText:
    class label:
        class Label:
            def __init__(self, font = None, anchor_point = None, anchored_position = None, text = None, color = None, line_spacing = None, scale = 1):
                self.font = font
                self.anchor_point = anchor_point
                self.anchored_position = anchored_position
                self.text = text
                self.color = color
                self.line_spacing = line_spacing
                self.scale = scale

            def render(self, canvas, x, y):
                ctx = canvas.getContext('2d')
                ctx.font = str(self.font.size) + "px \"Arial\", sans-serif"

                ctx.fillStyle = "white"
                ctx.fillText(
                   self.text,
                   self.anchored_position[0] + x,
                   self.anchored_position[1] + y
                )

    def wrap_text_to_pixels(
        string,
        max_width,
        font = None,
        indent0 = "",
        indent1 = "",
    ):
        return [string]


class MockFont:
    def __init__(self, path):
        self.path = path

    @property
    def size(self):
        nums = re.findall(r'\d+', self.path)
        if not nums:
            return 20
        return nums[0]
    
    # def get_glyph(self, num):
    #     return MockFontIO.Glyph(None, num, self.size, self.size, 0, 0, 0, 0)


class MockAdafruitFontLoader:
    def get(self, path):
        return MockFont(path)


class MockAdafruitBitmapFont:
    class bitmap_font:
        pass


class MockFontIO:
    class FontProtocol:
        pass

    class Glyph:
        def __init__(self, bitmap, tile_index, width, height, dx, dy, shift_x, shift_y):
            self.bitmap = bitmap
            self.tile_index = tile_index
            self.width = width
            self.height = height
            self.dx = dx
            self.dy = dy
            self.shift_x = shift_x
            self.shift_y = shift_y


class MockDisplayShapes:
    class rect:
        class Rect:
            def __init__(self, x = 0, y = 0, width = 0, height = 0, fill = None): #, outline = None, stroke = 0):
                self.x = x 
                self.y = y
                self.width = width
                self.height = height
                self.fill = fill 
                #self.outline = outline
                #self.stroke = stroke

            def render(self, canvas, x, y):
                ctx = canvas.getContext('2d')
                ctx.fillStyle = f"rgb({ self.fill[0] }, { self.fill[1] }, { self.fill[2] })"
                ctx.fillRect(
                    self.x + x,
                    self.y + y,
                    self.width,
                    self.height
                )

