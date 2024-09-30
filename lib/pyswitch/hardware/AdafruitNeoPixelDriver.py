import neopixel
import board


# Implements communication with an array of NeoPixels
class AdafruitNeoPixelDriver:

    def __init__(self, port = board.GP7):
        self._port = port
        self.leds = None
        
    # Initialize NeoPixel array. Neopixel documentation:
    # https://docs.circuitpython.org/projects/neopixel/en/latest/
    # https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
    def init(self, num_leds):
        self.leds = neopixel.NeoPixel(self._port, num_leds)



        