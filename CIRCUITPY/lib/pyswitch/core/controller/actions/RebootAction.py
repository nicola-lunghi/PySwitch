import supervisor

from .base.Action import Action
from ....definitions import Colors


# Action to reboot the device (used for development)
class RebootAction(Action):
    def __init__(self, config = {}):
        super().__init__(config)

        self.uses_switch_leds = True

    def init(self, appl, switch):
        super().init(appl, switch)
        
        self.switch_color = Colors.BLUE
        self.switch_brightness = 1

    def push(self):
        print("Reboot on user request")
        supervisor.reload()

