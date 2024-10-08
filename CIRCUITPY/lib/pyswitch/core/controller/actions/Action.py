from ...misc import Tools, Updateable, Defaults


# Base class for actions. All functionality is encapsulated in a class for each, 
# inheriting from Action.
class Action(Updateable):
    
    next_id = 0   # Global counted action ids (internal, just used for debugging!)

    # config: {
    #      "display": {
    #          "area":             ID of the display area. See displays defintion in config.
    #          "index":            Position inside the display area (optional for split container display areas). If omitted, always the first 
    #                              place is used which takes up the whole area space. 
    #          "layout":           Layout definition for the action label (mandatory)
    #      },
    #      "enabled": True,        Optional bool parameter to disable/enable the action. Mostly used internally only. Defaults to True 
    #                              when not specified.
    #      "id":                   Optional ID for debugging. If not set, an automatic ID is generated.
    # }
    def __init__(self, config = {}):
        self.config = config
                
        self.uses_switch_leds = False             # Must be set True explicitly by child classes in __init__() if they use the switch LEDs
        self._enabled = Tools.get_option(self.config, "enabled", True)
        self._initialized = False

    def __repr__(self):
        return self.__class__.__name__ + " " + self.id

    # Must be called before usage
    def init(self, appl, switch):
        self.appl = appl
        self.switch = switch

        self._init_id()

        self.debug = Tools.get_option(self.appl.config, "debugActions")
        self._debug_switch_port_name = Tools.get_option(self.appl.config, "actionsDebugSwitchName", None)

        self.label = self._get_display_label()   # DisplayLabel instance the action is connected to (or None).

        self._initialized = True

    # Sets up the debugging ID (either from config or a generated one)
    def _init_id(self):
        self.id = Tools.get_option(self.config, "id", False)
        if not self.id:
            self.id = self.switch.id + " | " + self.__class__.__name__ + " (" + repr(Action.next_id) + ")"
            
        Action.next_id = Action.next_id + 1

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled == value:
            return 
        
        self._enabled = value

        if self.debug:
            self.print("Set enabled to " + repr(value))

        self.force_update()

        self.update_displays()

    # Color of the switch segment(s) for the action (Difficult to do with multicolor, 
    # but this property is just needed to have a setter so this is not callable)
    @property
    def switch_color(self):
        raise Exception("Getter not implemented (yet)")

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

    # Called regularly every update interval to update status of effects etc.
    def update(self):
        if not self.enabled:
            return
                
        self.do_update()

    # Perform updates (to be redefined)
    def do_update(self):
        pass

    # Called when the switch is pushed down
    def push(self):
        pass

    # Called when the switch is released
    def release(self):
        pass

    # Called to update the displays (LEDs and label)
    def update_displays(self):
        pass

    # Reset the action
    def reset(self):
        pass

    # Must reset all action states so the instance is being updated
    def force_update(self):
        pass

    # Must reset the displays
    def reset_display(self):
        pass

    # Get the assigned label reference from the UI (or None)
    def _get_display_label(self):
        definition = Tools.get_option(self.config, "display", None)
        if not definition:
            return None
        
        label = self.appl.ui.root.search(definition)
        if label:
            return label
        
        # Not yet existent: Get container
        container = self.appl.ui.root.search({
            "id": definition["id"]
        })

        if not container:
            raise Exception("Action: Display element with ID " + repr(definition["id"]) + " not found")
        
        index = Tools.get_option(definition, "index", None)
        if index == None:
            return container

        layout = definition["layout"]
        
        # Set the color as the number of items cannot be changed later!
        layout["backColor"] = Tools.get_option(
            self.config, 
            "color", 
            Tools.get_option(
                layout, 
                "backColor",
                Defaults.DEFAULT_LABEL_COLOR
            )
        )

        label = self.appl.ui.create_label(
            layout = layout,
            name = "Action " + self.id
        )

        container.set(label, index)
        return label

    # Returns the switch LED segments to use
    def _get_led_segments(self):
        if not self.switch.pixels:
            return []
        
        if not self._initialized:
            raise Exception("Action not initialized")
        
        if not self.uses_switch_leds:
            raise Exception("You have to set uses_switch_leds to True to use LEDs of switches in actions.")

        if not self.enabled:
            return []

        actions_using_leds = self._get_actions_using_leds()

        if len(actions_using_leds) == 0:
            return []
                
        ret = []

        index = self._get_index_among_led_actions()
        num_pixels = len(self.switch.pixels)

        if len(actions_using_leds) == 1:
            for i in range(num_pixels):
                ret.append(i)                
        
        elif len(actions_using_leds) < num_pixels:
            pixels_for_first = num_pixels - len(actions_using_leds) + 1

            if index == 0:
                ret = [i for i in range(0, pixels_for_first)]

                if len(ret) != pixels_for_first:
                    raise Exception("Internal error: Must return " + str(pixels_for_first) + " segments")
            else:
                ret = [pixels_for_first + index - 1]

                if ret[0] >= num_pixels:
                    raise Exception("Internal error: Segment out of range")

        elif index < num_pixels:
            ret = [index]
        
        # Check results
        if len(ret) > num_pixels:
            raise Exception("Invalid segments: " + repr(ret))

        return ret

    # Returns the index of this action inside the LED-using actions of the switch.
    def _get_index_among_led_actions(self):
        if not self.uses_switch_leds:
            return -1
        
        actions_using_leds = self._get_actions_using_leds()

        for i in range(len(actions_using_leds)):
            if actions_using_leds[i] == self:
                return i
        
        raise Exception("Action not found in LED-using actions of switch " + self.switch.id)

    # Returns a list of the actions of the switch which are bothe enabled and use LEDs.
    def _get_actions_using_leds(self):
        return [a for a in self.switch.actions if a.uses_switch_leds and a.enabled]

    # Print to the debug console
    def print(self, msg):
        if self._debug_switch_port_name != None and self._debug_switch_port_name != self.switch.id:
            return
        
        enabled_text = "enabled" if self.enabled else "disabled"

        Tools.print("Switch " + self.id + " (" + enabled_text + "): " + msg)

