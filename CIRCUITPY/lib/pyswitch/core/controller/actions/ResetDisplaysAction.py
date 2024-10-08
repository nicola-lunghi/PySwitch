from .base.Action import Action
from ...misc.Tools import Tools


# Simple action that prints a fixed text on the console
class ResetDisplaysAction(Action):    
    
    # Used to reset the screen areas which show rig info details directly after rig changes.
    # Additional options:
    # {
    #     "resetSwitches":        Reset switches (including LEDs and display labels, if assigned) (optional)
    #     "ignoreOwnSwitch":      Do not reset the switch this action is assigned to (optional)
    #     "resetDisplayAreas":    Reset display areas (optional)
    # }
    def __init__(self, config = {}):
        super().__init__(config)
                
        self._reset_switches = Tools.get_option(config, "resetSwitches")
        self._ignore_own_switch = Tools.get_option(config, "ignoreOwnSwitch")
        self._reset_display_areas = Tools.get_option(config, "resetDisplayAreas")

    def push(self):
        if self._reset_switches:
            if self._ignore_own_switch:
                self.appl.reset_switches([self.switch])
            else:
                self.appl.reset_switches()

        if self._reset_display_areas:
            self.appl.reset_display_areas()
