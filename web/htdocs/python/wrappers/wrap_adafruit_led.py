from js import document
from math import pow, floor

class WrapNeoPixelDriver:
    class LedList(list):
        def __init__(self, dom_namespace):
            super().__init__()
            self.dom_namespace = dom_namespace

        def __add__(self, *args, **kwargs):
            return WrapNeoPixelDriver.LedList(super().__add__(*args, **kwargs))
        
        def __setitem__(self, key, value):            
            super(WrapNeoPixelDriver.LedList, self).__setitem__(key, value)

            led = document.getElementById(self.dom_namespace + "-led-" + str(key))

            if not led:
                return
            
            # Apply a non-linear function to approximate the NeoPixel behaviour. 
            # steepness: Low values are steeper than high ones.
            def trans(x, steepness = 20):
                return round((1 - pow(10, -(x / steepness))) * 255 + x/2) * 2/3

            value = [trans(v) for v in value]

            led.style.backgroundColor = f"rgb({ value[0] }, { value[1] }, { value[2] })"


    def __init__(self, dom_namespace):
        self.leds = None
        self.dom_namespace = dom_namespace
        
    def init(self, num_leds):
        self.leds = self.LedList(self.dom_namespace) 

        while len(self.leds) < num_leds:
            self.leds.append(None)


