import board

from busio import SPI
from displayio import release_displays
from adafruit_misc.adafruit_st7789 import ST7789

try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire


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

