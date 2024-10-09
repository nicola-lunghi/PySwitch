import board

# Display driver
from busio import SPI
from displayio import release_displays
from adafruit_misc.adafruit_st7789 import ST7789

try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

# Font loader
from adafruit_bitmap_font import bitmap_font

# Neopixel driver
from adafruit_misc.neopixel import NeoPixel

# Switch driver
from digitalio import DigitalInOut, Direction, Pull


# TFT driver class
class AdafruitST7789DisplayDriver:

    def __init__(self, 
                width = 240, 
                height = 240,
                tft_cs = board.GP13,
                tft_dc = board.GP12,
                spi_mosi = board.GP15,
                spi_clk = board.GP14,
                row_start = 80,
                rotation = 180,
                baudrate = 24000000         # 24MHz
        ):
        self.width = width
        self.height = height

        self._tft_cs = tft_cs
        self._tft_dc = tft_dc
        self._spi_mosi = spi_mosi
        self._spi_clk = spi_clk

        self._row_start = row_start
        self._rotation = rotation
        self._baudrate = baudrate

    # Initialize the display
    def init(self):        
        release_displays()
        
        spi = SPI(
            self._spi_clk, 
            MOSI = self._spi_mosi
        )
        while not spi.try_lock():
            pass
        
        spi.configure(
            baudrate = self._baudrate
        )
        spi.unlock()

        display_bus = FourWire(
            spi, 
            command = self._tft_dc, 
            chip_select = self._tft_cs, 
            reset = None
        )

        self.tft = ST7789(
            display_bus,
            width = self.width, 
            height = self.height,
            rowstart = self._row_start,
            rotation = self._rotation
        )


##################################################################################################


# Buffered font loader
class AdafruitFontLoader:
    _fonts = {}

    # Returns a font (buffered)
    def get(self, path):
        if path in self._fonts:
            return self._fonts[path]
        
        font = bitmap_font.load_font(path)
        self._fonts[path] = font

        return font


##################################################################################################


# Implements communication with an array of NeoPixels
class AdafruitNeoPixelDriver:

    def __init__(self, port = board.GP7):
        self._port = port
        self.leds = None
        
    # Initialize NeoPixel array. Neopixel documentation:
    # https://docs.circuitpython.org/projects/neopixel/en/latest/
    # https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
    def init(self, num_leds):
        self.leds = NeoPixel(self._port, num_leds)


##################################################################################################


# Simple GPIO switch
class AdafruitSwitch: #(SwitchDriver):
    
    # port: The board GPIO pin definition to be used for this switch (for example board.GP1)
    def __init__(self, port):
        self._port = port
        self._switch = None

    # Initializes the switch to the GPIO port
    def init(self):
        self._switch = DigitalInOut(self._port)
        
        self._switch.direction = Direction.INPUT
        self._switch.pull = Pull.UP

    # Representational string for debug output (optional)
    def __repr__(self):
        return repr(self._port)

    # Return if the switch is currently pushed
    @property
    def pushed(self):
        if not self._switch:
            return False
        
        return self._switch.value == False  # Inverse logic!

