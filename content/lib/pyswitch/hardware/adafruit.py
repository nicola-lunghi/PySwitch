import board

# Display driver
from busio import SPI, UART
from displayio import release_displays
from adafruit_misc.adafruit_st7789 import ST7789
from adafruit_midi import MIDI

from adafruit_midi.midi_message import MIDIUnknownEvent

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

        self.__tft_cs = tft_cs
        self.__tft_dc = tft_dc
        self.__spi_mosi = spi_mosi
        self.__spi_clk = spi_clk

        self.__row_start = row_start
        self.__rotation = rotation
        self.__baudrate = baudrate

    # Initialize the display
    def init(self):        
        release_displays()
        
        spi = SPI(
            self.__spi_clk, 
            MOSI = self.__spi_mosi
        )
        while not spi.try_lock():
            pass
        
        spi.configure(
            baudrate = self.__baudrate
        )
        spi.unlock()

        display_bus = FourWire(
            spi, 
            command = self.__tft_dc, 
            chip_select = self.__tft_cs, 
            reset = None
        )

        self.tft = ST7789(
            display_bus,
            width = self.width, 
            height = self.height,
            rowstart = self.__row_start,
            rotation = self.__rotation
        )


##################################################################################################


# Buffered font loader
class AdafruitFontLoader:
    __fonts = {}

    # Returns a font (buffered)
    def get(self, path):
        if path in self.__fonts:
            return self.__fonts[path]
        
        font = bitmap_font.load_font(path)
        self.__fonts[path] = font

        return font


##################################################################################################


# Implements communication with an array of NeoPixels
class AdafruitNeoPixelDriver:

    def __init__(self, port = board.GP7):
        self.__port = port
        self.leds = None
        
    # Initialize NeoPixel array. Neopixel documentation:
    # https://docs.circuitpython.org/projects/neopixel/en/latest/
    # https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
    def init(self, num_leds):
        self.leds = NeoPixel(self.__port, num_leds)


##################################################################################################


# Simple GPIO switch
class AdafruitSwitch: #(SwitchDriver):
    
    # port: The board GPIO pin definition to be used for this switch (for example board.GP1)
    def __init__(self, port):
        self.__port = port
        self.__switch = None

    # Initializes the switch to the GPIO port
    def init(self):
        self.__switch = DigitalInOut(self.__port)
        
        self.__switch.direction = Direction.INPUT
        self.__switch.pull = Pull.UP

    # Representational string for debug output (optional)
    def __repr__(self):
        return repr(self.__port)

    # Return if the switch is currently pushed
    @property
    def pushed(self):
        if not self.__switch:
            return False
        
        return self.__switch.value == False  # Inverse logic!


##################################################################################################


# USB MIDI Device
class AdfruitUsbMidiDevice:
    def __init__(self, 
                 port_in,
                 port_out,
                 in_buf_size,
                 in_channel = None,  # All
                 out_channel = 0,                 
        ):

        self.__midi = MIDI(
            midi_out = port_out,
            out_channel = out_channel,
            midi_in = port_in,
            in_channel = in_channel,
            in_buf_size = in_buf_size
        )

    def __repr__(self):
        return "USB"

    def send(self, midi_message):
        if isinstance(midi_message, MIDIUnknownEvent):
            return
        
        self.__midi.send(midi_message)

    def receive(self):
        return self.__midi.receive()

    
##################################################################################################


# DIN MIDI Device
class AdfruitDinMidiDevice:
    def __init__(self, 
                 gpio_in, 
                 gpio_out,
                 in_buf_size, 
                 baudrate, 
                 timeout,
                 in_channel = None,   # All
                 out_channel = 0, 
        ):

        midi_uart = UART(
            gpio_in, 
            gpio_out, 
            baudrate = baudrate, 
            timeout = timeout
        ) 

        self.__midi = MIDI(
            midi_out = midi_uart, 
            out_channel = out_channel,
            midi_in = midi_uart, 
            in_channel = in_channel,
            in_buf_size = in_buf_size
        )

    def __repr__(self):
        return "DIN"

    def send(self, midi_message):
        if isinstance(midi_message, MIDIUnknownEvent):
            return
        
        self.__midi.send(midi_message)

    def receive(self):
        return self.__midi.receive()