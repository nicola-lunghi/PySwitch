import supervisor

from .base.Action import Action
from ....definitions import Colors


# Action to reboot the device (for development)
class RebootAction(Action):
    def __init__(self, appl, switch, config, index):
        super().__init__(appl, switch, config, index)

        self.switch_color = Colors.BLUE
        self.switch_brightness = 1

    def push(self):
        print("Reboot on user request")
        supervisor.reload()

