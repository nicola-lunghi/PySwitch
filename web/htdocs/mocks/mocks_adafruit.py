class MockAdafruitMIDI:
    class MIDI:
        def __init__(self, midi_out = None, out_channel = None, midi_in = None, in_buf_size = None, debug = None):
            self.midi_out = midi_out
            self.midi_in = midi_in
            self.out_channel = out_channel
            self.in_buf_size = in_buf_size

        def receive(self):
            return None
        
        def send(self, midi_message):
            pass
            

class MockAdafruitMIDIControlChange:
    class ControlChange:
        def __init__(self, control, value = 0):
            self.control = control
            self.value = value


class MockAdafruitMIDIProgramChange:
    class ProgramChange:
        def __init__(self, patch = 0):
            self.patch = patch


class MockAdafruitMIDISystemExclusive:    
    class SystemExclusive:
        def __init__(self, manufacturer_id, data = []):
            self.manufacturer_id = manufacturer_id
            self.data = data


class MockAdafruitMIDIMessage:
    class MIDIUnknownEvent:
        def __init__(self, status = 0):
            self.status = status

    class MIDIMessage:
        @staticmethod
        def register_message_type():
            pass
            
            
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
        
        # def render(self, canvas, x, y):
        #     for item in self:
        #         item.render(canvas, x + self.x, y + self.y)

    class Palette(list):
        def __init__(self, color_count, dither = False):
            while len(self) < color_count:
                self.append(None)

        def __add__(self, *args, **kwargs):
            return MockDisplayIO.Palette(super().__add__(*args, **kwargs))

    class Bitmap:
        pass

    class TileGrid:
        pass

    class FourWire:
        def __init__(self, spi, command, chip_select, reset):
            pass

    def release_displays():
        pass


class MockNeoPixelDriver:
    def __init__(self):
        self.leds = None
        
    def init(self, num_leds):
        self.leds = [None for i in range(num_leds)]


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


class MockNeoPixel:
    class NeoPixel:
        pass


class MockFontIO:
    class FontProtocol:
        pass

    class Glyph:
        pass

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
                ctx.fillStyle = "red" #f"rgb({ self.fill[0] }, { self.fill[1] }, { self.fill[2] })"
                ctx.fillRect(
                    self.x + x,
                    self.y + y,
                    self.width,
                    self.height
                )

class MockBitmapTools:
    def readinto(bitmap, file, bits_per_pixel, element_size = 1, reverse_pixels_in_element = False, swap_bytes_in_element = False, reverse_rows = False):
        pass