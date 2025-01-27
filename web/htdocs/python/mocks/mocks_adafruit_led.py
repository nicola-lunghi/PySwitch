from js import document

class MockNeoPixel:
    class NeoPixel:
        pass


class MockNeoPixelDriver:
    class LedList(list):
        def __init__(self, dom_namespace):
            super().__init__()
            self.dom_namespace = dom_namespace

        def __add__(self, *args, **kwargs):
            return MockNeoPixelDriver.LedList(super().__add__(*args, **kwargs))
        
        def __setitem__(self, key, value):            
            super(MockNeoPixelDriver.LedList, self).__setitem__(key, value)

            led = document.getElementById(self.dom_namespace + "-led-" + str(key))

            if not led:
                return
            
            # Color transformation (the NeoPixels have a very non-linear brightness behaviour)
            def trans(v):
                return v
                v = v * 15
                if v > 255:
                    v = 255
                return v

            v_trans = [v for v in value]
            for i in range(len(value)):
                v_trans[i] = trans(value[i])

            led.style.backgroundColor = f"rgb({ v_trans[0] }, { v_trans[1] }, { v_trans[2] })"


    def __init__(self, dom_namespace):
        self.leds = None
        self.dom_namespace = dom_namespace
        
    def init(self, num_leds):
        self.leds = self.LedList(self.dom_namespace) 

        while len(self.leds) < num_leds:
            self.leds.append(None)


