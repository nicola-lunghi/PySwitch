import sys

from .base.Action import Action
from ....definitions import Colors


# Action to reboot the device (for development)
class TerminateAction(Action):
    def __init__(self, appl, switch, config, index):
        super().__init__(appl, switch, config, index)

        self.switch_color = Colors.YELLOW
        self.switch_brightness = 1

    def push(self):
        sys.exit()

