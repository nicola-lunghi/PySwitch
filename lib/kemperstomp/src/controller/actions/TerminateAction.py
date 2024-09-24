import sys

from .base.Action import Action
from ....definitions import Colors


# Action to reboot the device (for development)
class TerminateAction(Action):
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self.uses_switch_leds = True

    def init(self):
        super().init()
        
        self.switch_color = Colors.YELLOW
        self.switch_brightness = 1

    def push(self):
        print("Terminate on user request")
        sys.exit()

