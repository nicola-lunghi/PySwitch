from random import randint

from .ConditionTree import ConditionTree
from ..misc import Tools, Colors


# Controller class for a Foot Switch. Each foot switch has three Neopixels.
class FootSwitchController: #ConditionListener

    # config must be a dictionary holding the following attributes:
    # { 
    #     "assignment": {
    #         "model":         Model instance for the switch hardware. Must implement an init() method and a .pushed property.
    #         "pixels":        List of indexes for the Neopixels that belong to this switch, for example (0, 1, 2)
    #     },
    #
    #     "actions": [         Array of actions. Entries must be either Action instances or Conditions with Action
    #                          instance(s) inside (conditions can be deep).
    #         ExampleAction({
    #             "id":                 Action id. Optional.
    #             ...                   (individual options depending on the specific action type)
    #         }),
    #         ...
    #     ],
    #
    #     "initialColors": [    Initial colors to set. Optional, if not set, the default initial color set is generated.
    #         Colors.RED,
    #         Colors.YELLOW,
    #         Colors.ORANGE
    #     ],
    #     "initialBrightness":  Initial brightness. If not set, 1 is used. [0..1]
    # }
    def __init__(self, appl, config):
        self.config = config        
        self.pixels = Tools.get_option(self.config["assignment"], "pixels", [])
        
        self._switch = self.config["assignment"]["model"]
        self._switch.init()

        self.id = Tools.get_option(self.config["assignment"], "name", repr(self._switch))

        self._appl = appl
        self._pushed_state = False
        self._debug = Tools.get_option(self._appl.config, "debugSwitches")

        self._colors = [(0, 0, 0) for i in range(len(self.pixels))]
        self._brightnesses = [0 for i in range(len(self.pixels))]        

        self._initial_switch_colors()

        self._init_actions()
        
    # Set up action instances
    def _init_actions(self):
        if self._debug:
            self._print("Init actions")
        
        self._action_tree = ConditionTree(
            subject = Tools.get_option(self.config, "actions", []),
            listener = self
        )

        self._action_tree.init(self._appl)

        self.actions = self._action_tree.entries

        for action in self.actions:
            action.init(self._appl, self)
            
            self._appl.add_updateable(action)
            
            action.update_displays()

        # Update actions to initialize the correct enabled state
        self.condition_changed(None)
        
    # Called on condition changes.
    def condition_changed(self, condition):
        active_actions = self._action_tree.values

        to_disable = [a for a in self.actions if a.enabled and not a in active_actions]
        to_enable = [a for a in self.actions if not a.enabled and a in active_actions]

        # Execute the two lists in the correct order
        for action in to_disable:
            action.reset_display()
            action.enabled = False

        for action in to_enable:
            action.enabled = True

    # Set some initial colors on the neopixels
    def _initial_switch_colors(self):
        if not self.pixels:
            # No LEDs defined for the switch
            return
        
        if self._debug:
            self._print("Set initial colors")

        initial_brightness = Tools.get_option(self.config, "initialBrightness", 1)

        if Tools.get_option(self.config, "initialColors") != False:
            # Colors from config file, if set
            self.colors = self.config["initialColors"]
            self.brightness = initial_brightness
            return

        # Default color scheme: Random from a list of colors
        available_colors = (Colors.GREEN, Colors.YELLOW, Colors.RED)  # Colors to be used (in that order)
        index = randint(0, len(available_colors)-1)                   # Random start index  

        self.colors = [available_colors[(index + i) % len(available_colors)] for i in range(len(self.pixels))]
        self.brightness = initial_brightness
        
    # Process the switch: Check if it is currently pushed, set state accordingly
    def process(self):
        # Is the switch currently pushed? If not, return false.
        if not self.pushed:
            if self._pushed_state:
                self._pushed_state = False
                self._process_actions_release()

            return

        # Switch is pushed: Has it been pushed before already? 
        if self._pushed_state:
            return 
        
        # Mark as pushed (prevents redundant messages in the following ticks, when the switch can still be down)
        self._pushed_state = True
        self._process_actions_push()
        
    # Return if the (hardware) switch is currently pushed
    @property
    def pushed(self):
        return self._switch.pushed
                
    # Processes all push actions assigned to the switch 
    def _process_actions_push(self):
        for action in self.actions:
            if not action.enabled:
                continue

            if self._debug:
                self._print("Push action " + action.id)

            action.push()

    # Processes all release actions assigned to the switch 
    def _process_actions_release(self):
        for action in self.actions:
            if not action.enabled:
                continue

            if self._debug:
                self._print("Release action " + action.id)
                
            action.release()

    # Colors of the switch (array)
    @property
    def colors(self):
        return self._colors

    # Set switch colors (each of the LEDs individually). Does not take any effect until
    # set_brightness is called!
    @colors.setter
    def colors(self, colors):
        if len(colors) != len(self.pixels):
            raise Exception("Invalid amount of colors: " + repr(len(colors)))
        
        if not isinstance(colors, list):
            raise Exception("Invalid type for colors, must be a list: " + repr(colors))
        
        if self._debug:
            self._print(" -> Set colors to " + repr(colors))

        self._colors = colors        

    # Color (this just uses the first one)
    @property
    def color(self):
        if not self.pixels:
            return None
        
        return self._colors[0]

    # Set switch color (all three LEDs equally). Does not take any effect until
    # set_brightness is called!
    @color.setter
    def color(self, color):
        if self._debug:
            self._print(" -> Set color to " + repr(color))

        for i in range(len(self.pixels)):
            self._colors[i] = color

    # Returns current brightness (this just uses the first one)
    @property
    def brightness(self):
        if not self.pixels:
            return None
        
        return self._brightnesses[0]

    # Set brightness equally of all LEDs
    @brightness.setter
    def brightness(self, brightness):
        b = []
        for i in range(len(self.pixels)):
            b.append(brightness)
        
        self.brightnesses = b
    
    # Returns current brightnesses of all LEDs
    @property
    def brightnesses(self):
        return self._brightnesses

    # Set brightnesses of all LEDs
    @brightnesses.setter
    def brightnesses(self, brightnesses):
        if not self.pixels:
            return
        
        if not isinstance(brightnesses, list):
            raise Exception("Invalid type for brightnesses, must be a list: " + repr(brightnesses))
        
        if len(brightnesses) != len(self.pixels):
            raise Exception("Invalid amount of colors: " + repr(len(brightnesses)))
        
        if self._debug:
            self._print(" -> Set brightnesses to " + repr(brightnesses))

        for i in range(len(self.pixels)):
            pixel = self.pixels[i]
            self._appl.led_driver.leds[pixel] = (
                int(self._colors[i][0] * brightnesses[i]),   # R
                int(self._colors[i][1] * brightnesses[i]),   # G
                int(self._colors[i][2] * brightnesses[i])    # B
            )

        self._brightnesses = brightnesses

    # Debug console output
    def _print(self, msg):
        state_str = "pushed" if self.pushed else "off"            
        Tools.print("Switch " + self.id + " (" + state_str + "): " + msg)


################################################################################################


## Base class for implementing switch driver classes
#class SwitchDriver:
#    
#    # Initializes the switch. Called once before usage.
#    def init(self):
#        pass
#
#    # Return if the switch is currently pushed (bool).
#    @property
#    def pushed(self):
#        return False
    
