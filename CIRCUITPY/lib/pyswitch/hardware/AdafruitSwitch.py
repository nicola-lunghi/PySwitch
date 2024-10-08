from digitalio import DigitalInOut, Direction, Pull

from ..core.controller.FootSwitchController import SwitchDriver

# Simple GPIO switch
class AdafruitSwitch(SwitchDriver):
    
    # port: The board GPIO pin definition to be used for this switch (for example board.GP1)
    def __init__(self, port):
        self._port = port
        self._switch = None

    # Initializes the switch to the GPIO port
    def init(self):
        self._switch = DigitalInOut(self._port)
        
        self._switch.direction = Direction.INPUT
        self._switch.pull = Pull.UP

    # Representational string for debug output (optional)
    def __repr__(self):
        return repr(self._port)

    # Return if the switch is currently pushed
    @property
    def pushed(self):
        if not self._switch:
            return False
        
        return self._switch.value == False  # Inverse logic!

