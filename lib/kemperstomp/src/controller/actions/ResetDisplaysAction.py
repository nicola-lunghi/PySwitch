from .base.Action import Action
from ...Tools import Tools


# Simple action that prints a fixed text on the console
class ResetDisplaysAction(Action):    
    
    # Options: see ActionTypes
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)
                
        self._reset_switches = Tools.get_option(config, "resetSwitches")
        self._ignore_own_switch = Tools.get_option(config, "ignoreOwnSwitch")
        self._reset_display_areas = Tools.get_option(config, "resetDisplayAreas")

    def push(self):
        if self._reset_switches:
            if self._ignore_own_switch == True:
                self.appl.reset_switches([self.switch])
            else:
                self.appl.reset_switches()

        if self._reset_display_areas:
            self.appl.reset_display_areas()
