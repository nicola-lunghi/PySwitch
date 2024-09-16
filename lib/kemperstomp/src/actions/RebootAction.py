import supervisor

from .Action import Action

from ...kemperstomp_def import Colors

# Action to reboot the device (for development)
class RebootAction(Action):
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self.switch.set_colors((Colors.BLUE, Colors.BLUE, Colors.BLUE))
        self.switch.set_brightness(1)

    def down(self):
        supervisor.reload()

