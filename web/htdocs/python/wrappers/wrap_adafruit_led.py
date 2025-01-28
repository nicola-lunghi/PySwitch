from js import document

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
            
            # Scale up values so that the "on" brightness (set to 0.3 in PySwitchRunner) will be one.
            value = [v * (1 / 0.3) for v in value]

            led.style.backgroundColor = f"rgb({ value[0] }, { value[1] }, { value[2] })"


    def __init__(self, dom_namespace):
        self.leds = None
        self.dom_namespace = dom_namespace
        
    def init(self, num_leds):
        self.leds = self.LedList(self.dom_namespace) 

        while len(self.leds) < num_leds:
            self.leds.append(None)


