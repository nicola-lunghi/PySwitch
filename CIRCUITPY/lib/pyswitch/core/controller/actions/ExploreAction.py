from .base.Action import Action
from ...misc.Colors import Colors

# Action to explore switch GPIO assignments (used internally only in explore mode!)
# Also used to examine neopixel addressing.
class ExploreAction(Action):
    
    def __init__(self, config = {}):
        super().__init__(config)

        self._name = config["name"]
        self._step = config["step"]
           
    # Must be called before usage
    def init(self, appl, switch):
        self.appl = appl
        self.switch = switch

        self._label = self.appl.get_next_port_label()

        if self._label:
            self._label.text = self._name

    def push(self):
        pixel_out = self._trigger_pixel_search()
        print("board." + self._name + " " + pixel_out)

        if self.appl.ui:
            self.appl.pixel_display.text = pixel_out

        if self._label:
            self.appl.reset_port_markers()
            self._label.back_color = Colors.RED
            
    # Enlighten the next available switch LEDs and returns a report string.
    def _trigger_pixel_search(self):
        current = self.appl.show_next_switch(self._step)
        if current == None:
            return
        
        # Get output for pixel exploration
        num_switch_leds = len(self.appl.switches) * len(self.switch.pixels)
        return "Pixels: (" + repr(current[0]) + ", " + repr(current[1]) + ", " + repr(current[2]) + ") of " + repr(num_switch_leds)        

        