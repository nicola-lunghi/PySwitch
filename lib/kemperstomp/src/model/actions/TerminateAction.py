import sys

from .Action import Action
from ....definitions import Colors


# Action to reboot the device (for development)
class TerminateAction(Action):
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self.switch.colors = (Colors.YELLOW, Colors.YELLOW, Colors.YELLOW)
        self.switch.brightness = 1

        if self.label != None:
            self.label.text = "Terminate"

    def trigger(self, event):
        sys.exit()

