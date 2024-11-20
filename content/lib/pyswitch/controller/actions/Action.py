import math
from ...misc import get_option, Updateable
#from ...stats import RuntimeStatistics

# Base class for actions. All functionality is encapsulated in a class for each, 
# inheriting from Action.
class Action(Updateable):
    
    _next_id = 0   # Global counted action ids (internal, just used for debugging!)

    # config: {
    #      "callback":             Callback instance to update the display and LEDs. Must contain an update_displays(action) function. Optional. 
    #
    #      "display":              Optional DisplayLabel instance
    #
    #      "enableCallback":       Callback to set enabled state (optional). Must contain an enabled(action) function.
    # 
    #      "id":                   Optional ID for debugging. If not set, an automatic ID is generated.
    #
    #      "useSwitchLeds":        Use LEDs to visualize state. Optional, default is False.
    #
    # }
    def __init__(self, config = {}):
        self.uses_switch_leds = get_option(config, "useSwitchLeds", False)
        self._initialized = False

        self.label = get_option(config, "display", None)
        self.callback = get_option(config, "callback", None)

        self.id = get_option(config, "id", None)

        self._enable_callback = get_option(config, "enableCallback", None)

    # Must be called before usage
    def init(self, appl, switch):
        self.appl = appl
        self.switch = switch

        that = self
        class _CallbackListener:
            #@RuntimeStatistics.measure
            def parameter_changed(self, mapping):
                if that.enabled:
                    #that.force_update()
                    that.update_displays()

            #@RuntimeStatistics.measure
            def request_terminated(self, mapping):
                if that.enabled:
                    that.update_displays()

        # Enable callback
        if self._enable_callback:            
            self._enable_callback.init(appl, _CallbackListener())

        # Update display callback
        if self.callback:
            self.callback.init(appl, _CallbackListener())

        self._initialized = True

    @property
    def enabled(self):
        ec = self._enable_callback
        return ec.enabled(self) if ec else True
        
    # Color of the switch segment(s) for the action (Difficult to do with multicolor, 
    # but this property is just needed to have a setter so this is not callable)
    @property
    def switch_color(self):  # pragma: no cover
        raise Exception() #"Getter not implemented (yet)")

    # color can also be a tuple!
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
                # Only fills some LEDs: Use a middle color
                for segment in segments:
                    tmp[segment] = color[math.floor(len(color) / 2)]
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
        pass                                      # pragma: no cover

    # Called when the switch is pushed down
    def push(self):
        pass                                      # pragma: no cover

    # Called when the switch is released
    def release(self):
        pass                                      # pragma: no cover

    # Called to update the displays (LEDs and label)
    #@RuntimeStatistics.measure
    def update_displays(self):
        if not self.enabled:
            return
        
        cb = self.callback
        if cb:
            cb.update_displays(self)
    
    # Reset the action
    def reset(self):
        pass                                      # pragma: no cover

    # Must reset all action states so the instance is being updated
    #def force_update(self):
    #    pass                                      # pragma: no cover

    # Must reset the displays
    #def reset_display(self):
    #    pass                                      # pragma: no cover

    # Returns the switch LED segments to use
    def _get_led_segments(self):
        if not self.switch.pixels or not self.uses_switch_leds or not self.enabled:
            return []
        
        actions_using_leds = self._get_actions_using_leds()

        ret = []

        index = self._get_index_among_led_actions(actions_using_leds)
        num_pixels = len(self.switch.pixels)

        if len(actions_using_leds) == 1:
            for i in range(num_pixels):
                ret.append(i)                
        
        elif len(actions_using_leds) < num_pixels:
            pixels_for_first = num_pixels - len(actions_using_leds) + 1

            if index == 0:
                ret = [i for i in range(0, pixels_for_first)]
            else:
                ret = [pixels_for_first + index - 1]

        elif index < num_pixels:
            ret = [index]

        return ret

    # Returns the index of this action inside the LED-using actions of the switch.
    def _get_index_among_led_actions(self, actions_using_leds):
        for i in range(len(actions_using_leds)):
            if actions_using_leds[i] == self:
                return i
        
        raise Exception() #"Action " + repr(self.id) + " not found in LED-using actions of switch " + repr(self.switch.id))

    # Returns a list of the actions of the switch which are both enabled and use LEDs.
    def _get_actions_using_leds(self):
        ret = [] 

        for a in self.switch.actions:
            sub = a.get_all_actions()
            ret = ret + [s for s in sub if s.uses_switch_leds and s.enabled]

        return ret

    # Must return a list containing self and all possible sub actions
    def get_all_actions(self):
        return [self]

