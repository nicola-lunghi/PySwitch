from js import document
from math import pow
import colorsys

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
            def trans(x, gamma = 0.28):
                return pow((x/255), gamma) * 255
            
            value = [trans(v) for v in value]

            # # Change orientation towards white
            # hsv = colorsys.rgb_to_hsv(value[0] / 255, value[1] / 255, value[2] / 255)
            # print("---")
            # print(hsv)
            # value = colorsys.hsv_to_rgb(
            #     hsv[0],
            #     hsv[1],
            #     1 - hsv[2]
            # )
            # value = [v * 255 for v in value]
            # print(value)

            # When black, make transparent
            led.style.backgroundColor = f"rgb({ value[0] }, { value[1] }, { value[2] })"


    def __init__(self, dom_namespace):
        self.leds = None
        self.dom_namespace = dom_namespace
        
    def init(self, num_leds):
        self.leds = self.LedList(self.dom_namespace) 

        while len(self.leds) < num_leds:
            self.leds.append(None)


