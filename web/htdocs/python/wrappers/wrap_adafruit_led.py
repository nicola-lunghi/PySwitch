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
            

            # # Scale up values so that the "on" brightness (set to 0.3 in PySwitchRunner) will be one.
            # value = [floor(v * (1 / 0.3), 1) for v in value]

            # Apply a non-linear function to approximate the NeoPixel behaviour. 
            # steepness: Low values are steeper than high ones. Shall not be larger than 128.
            def trans(x, steepness = 80):
                return round((1 - pow(10, -(x / steepness))) * 255)

            value = [trans(v) for v in value]

            print(trans(0))
            print(trans(1))
            print(trans(2))
            print(trans(17))

            led.style.backgroundColor = f"rgb({ value[0] }, { value[1] }, { value[2] })"


    def __init__(self, dom_namespace):
        self.leds = None
        self.dom_namespace = dom_namespace
        
    def init(self, num_leds):
        self.leds = self.LedList(self.dom_namespace) 

        while len(self.leds) < num_leds:
            self.leds.append(None)


