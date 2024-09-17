import board
import busio
import displayio
from adafruit_st7789 import ST7789

try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire


# TFT driver class
class DisplayDriver:

    DISPLAY_ROW_START = 80
    DISPLAY_ROTATION = 180
    SPI_BAUDRATE = 24000000         # 24MHz

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def init(self):        
        displayio.release_displays()

        tft_res = board.GP8
        tft_cs = board.GP13
        tft_dc = board.GP12
        spi_mosi = board.GP15
        spi_clk = board.GP14

        spi = busio.SPI(
            spi_clk, 
            MOSI = spi_mosi
        )
        while not spi.try_lock():
            pass
        
        spi.configure(baudrate = DisplayDriver.SPI_BAUDRATE)  
        spi.unlock()

        display_bus = FourWire(
            spi, 
            command = tft_dc, 
            chip_select = tft_cs, 
            reset = None
        )

        self.tft = ST7789(
            display_bus,
            width = self.width, 
            height = self.height,
            rowstart = DisplayDriver.DISPLAY_ROW_START, 
            rotation = DisplayDriver.DISPLAY_ROTATION
        )

