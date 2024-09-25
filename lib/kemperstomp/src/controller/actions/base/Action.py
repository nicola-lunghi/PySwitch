from ....misc.Tools import Tools
from ....ui.elements.DisplayLabel import DisplayLabel
from .....definitions import FootSwitchDefaults, ModuleConfig, Colors
from .....display import DisplayAreas

# Base class for actions. All functionality is encapsulated in a class for each, 
# inheriting from Action.
class Action:
    
    # Factory for creating actions by type (= class name of derivative of Action).
    # All created classes must have the same constructor parameters as this method.
    @staticmethod
    def get_instance(appl, switch, config):
        class_name = config["type"]

        module = __import__(ModuleConfig.MODULE_BASE_PATH + ".src.controller.actions." + class_name, globals(), locals(), [class_name])
        class_def = getattr(module, class_name)
        return class_def(appl, switch, config)

    ######################################################################################################################################

    # config: See FootSwitch
    def __init__(self, appl, switch, config):
        self.appl = appl
        self.switch = switch
        self.config = config
        self.debug = Tools.get_option(self.appl.config, "debugActions")
        self.id = self.switch.id + " | " + self.__class__.__name__
        
        self.uses_switch_leds = False             # Must be set True explicitly by child classes in __init__() if they use the switch LEDs
        self._initialized = False

    # Must be called before usage
    def init(self):
        self.label = self._get_action_display()   # DisplayLabel instance the action is connected to (or None).

        self._index_among_led_actions = self._get_index_among_led_actions()
        self._initialized = True

    # Color of the switch segment(s) for the action (Difficult to do with multicolor, 
    # but this property is just needed to have a setter so this is not callable)
    @property
    def switch_color(self):
        raise Exception("Getter not implemented")
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

        if isinstance(color[0], tuple):
            if len(segments) == len(color):
                # Fills all LEDs: Just pass colors
                for i in range(len(segments)):
                    tmp[segments[i]] = color[i]
            else:
                # Only fills some LEDs: Use first color only
                for segment in segments:
                    tmp[segment] = color[0]                
        else:
            # Single color: Fill all segments
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

    # Reset the action
    def reset(self):
        pass

    # Get the assigned label reference from the UI (or None)
    def _get_action_display(self):
        definition = Tools.get_option(self.config, "display", None)
        if definition == None:
            return None
        
        label = self.appl.ui.root.search(definition)
        if label != None:
            return label
        
        # Not yet existent: Get container
        container = self.appl.ui.root.search({
            "id": definition["id"]
        })

        if container == None:
            raise Exception("Action: Display element with ID " + repr(definition["id"]) + " not found")
        
        index = Tools.get_option(definition, "index", None)
        if index == None:
            return container

        layout = DisplayAreas.ACTION_LABEL_LAYOUT
        layout["backColor"] = Tools.get_option(self.config, "color", Colors.DEFAULT_LABEL_COLOR)  # Set the color as the number of items cannot be changed later!

        label = DisplayLabel(
            layout = layout,
            name = "Action " + self.id            
        )

        container.set(label, index)
        return label

    # Returns the switch LED segments to use
    def _get_led_segments(self):
        if self._initialized != True:
            raise Exception("Action not initialized")
        
        if self.uses_switch_leds != True:
            raise Exception("You have to set uses_switch_leds to True to use LEDs of switches in actions.")

        if len(self.switch.actions_using_leds) == 0:
            return []
                
        ret = []

        if len(self.switch.actions_using_leds) == 1:
            for i in range(FootSwitchDefaults.NUM_PIXELS):
                ret.append(i)                
        
        elif len(self.switch.actions_using_leds) < FootSwitchDefaults.NUM_PIXELS:
            pixels_for_first = FootSwitchDefaults.NUM_PIXELS - len(self.switch.actions_using_leds) + 1            

            if self._index_among_led_actions == 0:
                ret = [i for i in range(0, pixels_for_first)]

                if len(ret) != pixels_for_first:
                    raise Exception("Internal error: Must return " + str(pixels_for_first) + " segments")
            else:
                ret = [pixels_for_first + self._index_among_led_actions - 1]

                if ret[0] >= FootSwitchDefaults.NUM_PIXELS:
                    raise Exception("Internal error: Segment out of range")

        elif self._index_among_led_actions < FootSwitchDefaults.NUM_PIXELS:
            ret = [self._index_among_led_actions]
        
        # Check results
        if len(ret) > FootSwitchDefaults.NUM_PIXELS:
            raise Exception("Invalid segments: " + repr(ret))

        return ret

    # Returns the index of this action inside the LED-using actions of the switch.
    def _get_index_among_led_actions(self):
        if self.uses_switch_leds != True:
            return -1
        
        for i in range(len(self.switch.actions_using_leds)):
            if self.switch.actions_using_leds[i] == self:
                return i
        
        raise Exception("Action not found in LED-using actions of switch " + self.switch.id)

    # Print to the debug console
    def print(self, msg):
        Tools.print("Switch " + self.id + ": " + msg)
