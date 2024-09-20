from ....Tools import Tools
from .....definitions import FootSwitchDefaults

# Base class for actions. All functionality is encapsulated in a class for each, 
# inheriting from Action.
class Action:
    
    # Factory for creating actions by type (= class name of derivative of Action).
    # All created classes must have the same constructor parameters as this method.
    @staticmethod
    def get_instance(appl, switch, config, index):
        class_name = config["type"]

        module = __import__("kemperstomp.src.controller.actions." + class_name, globals(), locals(), [class_name])
        class_def = getattr(module, class_name)
        return class_def(appl, switch, config, index)

    # config: See FootSwitch    
    def __init__(self, appl, switch, config, index):
        self.appl = appl
        self.switch = switch
        self.config = config
        self.index = index
        self.id = self.switch.id + " | " + self.__class__.__name__
        self.debug = Tools.get_option(self.appl.config, "debugActions")

        self.label = self._get_action_display()   # DisplayLabel instance the action is connected to (or None).

    # Color of the switch segment(s) for the action
    @property
    def switch_color(self):
        segments = self._get_led_segments()
        if len(segments) > 0:
            return self.switch.colors[segments[0]]  # Return the first segment as they are all equal
        return None

    @switch_color.setter
    def switch_color(self, color):
        segments = self._get_led_segments()
        if len(segments) == 0:
            return

        tmp = self.switch.colors    
        for segment in segments:
            tmp[segment] = color

        self.switch.colors = tmp

    # Brightness of the switch segment(s) for the action
    @property
    def switch_brightness(self):
        segments = self._get_led_segments()
        if len(segments) > 0:
            return self.switch.brightnesses[segments[0]]  # Return the first segment as they are all equal
        return None

    @switch_brightness.setter
    def switch_brightness(self, brightness):
        segments = self._get_led_segments()
        if len(segments) == 0:
            return
                
        tmp = self.switch.brightnesses
        for segment in segments:
            tmp[segment] = brightness

        self.switch.brightnesses = tmp

    # Called when the switch is pushed down
    def push(self):
        pass

    # Called when the switch is released
    def release(self):
        pass

    # Called regularly every update interval to update status of effects etc.
    def update(self):
        pass

    # Called to update the displays (LEDs and label)
    def update_displays(self):
        pass

    # Get the assigned label reference from the UI (or None)
    def _get_action_display(self):
        if Tools.get_option(self.config, "display") == False:
            return None
                
        # Set initial properties
        label = self.appl.ui.get_label(self.config["display"])
        label.text = Tools.get_option(self.config["display"], "text", "")
        label.corner_radius = Tools.get_option(self.config["display"], "cornerRadius", label.corner_radius)

        return label

    # Returns the switch LED segments to use
    def _get_led_segments(self):
        ret = []
        if self.switch.num_actions == 0:
            return ret
        
        if self.switch.num_actions == 1:
            for i in range(FootSwitchDefaults.NUM_PIXELS):
                ret.append(i)                
        
        elif self.switch.num_actions < FootSwitchDefaults.NUM_PIXELS:
            pixels_for_first = FootSwitchDefaults.NUM_PIXELS - self.switch.num_actions + 1

            if self.index == 0:
                ret = [i for i in range(0, pixels_for_first)]

                if len(ret) != pixels_for_first:
                    raise Exception("Internal error: Must return " + str(pixels_for_first) + " segments")
            else:
                ret = [pixels_for_first + self.index - 1]

                if ret[0] >= FootSwitchDefaults.NUM_PIXELS:
                    raise Exception("Internal error: Segment out of range")

        elif self.index < FootSwitchDefaults.NUM_PIXELS:
            ret = [self.index]
        
        # Check results
        if len(ret) > FootSwitchDefaults.NUM_PIXELS:
            raise Exception("Invalid segments: " + repr(ret))

        return ret

    # Print to the debug console
    def print(self, msg):
        Tools.print("Action " + self.id + ": " + msg)
