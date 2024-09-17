import neopixel


# Implements communication with an array of NeoPixels
class LedDriver:
    def __init__(self, port, num_leds):
        self.port = port
        self.num_leds = num_leds        

        self._init_neopixel()

    # Initialize NeoPixel array. Neopixel documentation:
    # https://docs.circuitpython.org/projects/neopixel/en/latest/
    # https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
    def _init_neopixel(self):        
        self.leds = neopixel.NeoPixel(self.port, self.num_leds)