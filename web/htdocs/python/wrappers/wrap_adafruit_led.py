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
            
            # When black, make transparent
            if value == (0, 0, 0):
                led.style.backgroundColor = f"rgba(0, 0, 0, 0.2)"
                return

            # Apply gamma correction
            def trans(x, gamma = 0.3):
                return pow((x/255), gamma) * 255
            
            value = [trans(v) for v in value]

            # When black, make transparent
            led.style.backgroundColor = f"rgb({ value[0] }, { value[1] }, { value[2] })"


    def __init__(self, dom_namespace):
        self.leds = None
        self.dom_namespace = dom_namespace
        
    def init(self, num_leds):
        self.leds = self.LedList(self.dom_namespace) 

        while len(self.leds) < num_leds:
            self.leds.append(None)


