import supervisor

from .base.Action import Action
from ....definitions import Colors


# Action to reboot the device (for development)
class RebootAction(Action):
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self.switch.colors = (Colors.BLUE, Colors.BLUE, Colors.BLUE)
        self.switch.brightness = 1

        if self.label != None:
            self.label.text = "Reboot"

    def push(self):
        supervisor.reload()

