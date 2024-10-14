from lib.pyswitch.controller.actions.Action import Action

class MockNeoPixelDriver:
    class Led:
        def __init__(self):
            self.color = None
            self.brightness = None

    def __init__(self):
        self.leds = None
        
    def init(self, num_leds):
        self.leds = [self.Led() for i in range(num_leds)]

class MockSwitch:
    def __init__(self):
        pass

    def init(self):
        pass

    @property
    def pushed(self):
        return False

class MockValueProvider:
    def parse(self, mapping, midi_message):
        return False
    
    def set_value(self, mapping, value):
        pass


class MockAction(Action):
    pass
