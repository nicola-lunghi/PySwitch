from .base.Action import Action
from ..FootSwitch import FootSwitch


# Action to explore switch GPIO assignments (used internally only in explore mode!)
class ExplorePixelAction(Action):
    def push(self):
        # Enlighten the next available switch
        currently_shown_switch = self.appl.show_next_switch(self.config["step"])
        if currently_shown_switch == None:
            return
        
        num_switch_leds = len(self.appl.switches) * FootSwitch.NUM_PIXELS

        print("Pixels: (" 
                + str(currently_shown_switch[0]) + ", " 
                + str(currently_shown_switch[1]) + ", " 
                + str(currently_shown_switch[2]) + ")"
                + " of " + str(num_switch_leds)
        )
