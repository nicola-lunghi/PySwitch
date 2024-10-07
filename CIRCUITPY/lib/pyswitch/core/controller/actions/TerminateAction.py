import sys

from .base.Action import Action
from ....definitions import Colors


# Action to reboot the device (used for development)
class TerminateAction(Action):
    def __init__(self, config = {}):
        super().__init__(config)

        self.uses_switch_leds = True

    def init(self, appl, switch):
        super().init(appl, switch)
        
        self.switch_color = Colors.YELLOW
        self.switch_brightness = 1

    def push(self):
        print("Terminate on user request")
        sys.exit()

