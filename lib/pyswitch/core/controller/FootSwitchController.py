import random

from .conditions.Condition import Condition, ConditionListener
from .actions.base.Action import Action
from ..misc.Tools import Tools
from ...definitions import Colors
from .Updateable import Updateable


# Controller class for a Foot Switch. Each foot switch has three Neopixels.
class FootSwitchController(ConditionListener, Updateable):

    # config must be a dictionary holding the following attributes:
    # { 
    #     "assignment": {
    #         "model":         Model instance for the switch hardware. Must implement an init() method and a .pushed property.
    #         "pixels":        List of indexes for the Neopixels that belong to this switch, for example (0, 1, 2)
    #     },
    #
    #     "actions": [         Array of actions. Entries must be either action specifications or Conditions with action
    #                          specifications.
    #         {
    #             "type":               Action type. Allowed values: See the Actions class
    #             "id":                 Action id. Optional.
    #             ...                   (individual options depending on the specific action type)
    #         },
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
        self.pixels = Tools.get_option(self.config["assignment"], "pixels")
        
        self._switch = self.config["assignment"]["model"]
        self._switch.init()

        self.id = Tools.get_option(self.config["assignment"], "name", repr(self._switch))

        self._appl = appl
        self._colors = [(0, 0, 0) for i in range(len(self.pixels))]
        self._brightnesses = [0 for i in range(len(self.pixels))]
        self._pushed_state = False
        self._debug = Tools.get_option(self._appl.config, "debugSwitches")

        self._initial_switch_colors()
        self._init_actions()
    
    # Set up action instances
    def _init_actions(self):
        if self._debug == True:
            self._print("Init actions")
        
        self.actions = []
        
        for action_config in self.config["actions"]:
            self._evaluate_action_definition(action_config)

        for action in self.actions:            
            action.init()
            action.update_displays()

    def _evaluate_action_definition(self, action_config):
        if isinstance(action_config, Condition):
            # Condition based: Create actions for both outcomes
            actions_yes = self._add_actions(action_config.yes, True)
            actions_no = self._add_actions(action_config.no, False)

            # Set the actions on the condition for later access
            action_config.set_instances(
                self._appl,
                inst_yes = actions_yes,
                inst_no = actions_no
            )

            # Add this instance as listener on condition changes
            action_config.add_listener(self)

            # Add the condition to the global list of conditions, so it will
            # be updated periodically
            self._appl.updateables.append(action_config)
        else:
            # Simple action definition
            self._add_action(action_config, True)


    # Creates and adds one or more actions and returns an array
    def _add_actions(self, action_config, enabled):
        if action_config == None:
            return None
        
        ret = []
        if isinstance(action_config, list): #hasattr(action_config, '__iter__'):
            for ac in action_config:
                ret.append(self._add_action(ac, enabled))
        
        else:
            ret.append(self._add_action(action_config, enabled))
        
        return ret
        
    # Creates and adds one action and returns it
    def _add_action(self, action_config, enabled):
        if Tools.get_option(action_config, "enabled", None) == None:
            action_config["enabled"] = enabled

        action = Action.get_instance(
            self._appl,
            self,
            action_config
        )

        self.actions.append(action)

        return action

    # Set some initial colors on the neopixels
    def _initial_switch_colors(self):
        if self.pixels == False:
            # No LEDs defined for the switch
            return
        
        if self._debug == True:
            self._print("Set initial colors")

        initial_brightness = Tools.get_option(self.config, "initialBrightness", 1)

        if Tools.get_option(self.config, "initialColors") != False:
            # Colors from config file, if set
            self.colors = self.config["initialColors"]
            self.brightness = initial_brightness
            return

        # Default color scheme: Random from a list of colors
        available_colors = (Colors.GREEN, Colors.YELLOW, Colors.RED)  # Colors to be used (in that order)
        index = random.randint(0, len(available_colors)-1)            # Random start index  

        self.colors = [available_colors[(index + i) % len(available_colors)] for i in range(len(self.pixels))]
        self.brightness = initial_brightness
        
    # Process the switch: Check if it is currently pushed, set state accordingly
    def process(self):
        # Is the switch currently pushed? If not, return false.
        if self.pushed == False:
            if self._pushed_state == True:
                self._pushed_state = False
                self._process_actions_release()

            return

        # Switch is pushed: Has it been pushed before already? 
        if self._pushed_state == True:
            return 
        
        # Mark as pushed (prevents redundant messages in the following ticks, when the switch can still be down)
        self._pushed_state = True
        self._process_actions_push()

    # Called every update interval
    def update(self):
        for action in self.actions:
            if not action.enabled:
                continue

            action.update()

    # Reset all actions
    def reset(self):
        for action in self.actions:
            action.reset()

    # Return if the switch is currently pushed
    @property
    def pushed(self):
        return self._switch.pushed
                
    # Processes all push actions assigned to the switch 
    def _process_actions_push(self):
        for action in self.actions:
            if not action.enabled:
                continue

            if self._debug == True:
                self._print("Push action " + action.id)

            action.push()

    # Processes all release actions assigned to the switch 
    def _process_actions_release(self):
        for action in self.actions:
            if not action.enabled:
                continue

            if self._debug == True:
                self._print("Release action " + action.id)
                
            action.release()

    # Called on condition changes. The yes value will be True or False.
    def condition_changed(self, condition, bool_value):
        # Order plays a role here: Disable before enable
        collection = {
            "enable": [],
            "disable": []
        }

        # Get lists of which actions to disable and enable
        self._get_update_condition_actions(collection, condition.model.yes, True, bool_value)
        self._get_update_condition_actions(collection, condition.model.no, False, bool_value)
        
        # Execute the two lists in the correct order
        for action in collection["disable"]:
            action.reset_display()
            action.enabled = False

        for action in collection["enable"]:
            action.enabled = True

    # Updates all yes/no actions of a condition
    def _get_update_condition_actions(self, collection, actions, ref_bool_value, bool_value):
        if actions == None:
            return
        
        for action in actions:
            enable = ref_bool_value == bool_value

            if enable:
                collection["enable"].append(action)
            else:
                collection["disable"].append(action)

    # Colors of the switch (array)
    @property
    def colors(self):
        return self._colors

    # Set switch colors (each of the LEDs individually). Does not take any effect until
    # set_brightness is called!
    @colors.setter
    def colors(self, colors):
        if len(colors) != len(self._colors):
            raise Exception("Invalid amount of colors: " + repr(len(colors)))
        
        if self._debug == True:
            self._print(" -> Set colors to " + repr(colors))

        self._colors = colors        

    # Color (this just uses the first one)
    @property
    def color(self):
        return self._colors[0]

    # Set switch color (all three LEDs equally). Does not take any effect until
    # set_brightness is called!
    @color.setter
    def color(self, color):
        if self._debug == True:
            self._print(" -> Set color to " + repr(color))

        for i in range(len(self._colors)):
            self._colors[i] = color

    # Returns current brightness (this just uses the first one)
    @property
    def brightness(self):
        return self._brightnesses[0]

    # Set brightness equally of all LEDs
    @brightness.setter
    def brightness(self, brightness):
        if self._debug == True:
            self._print(" -> Set brightness to " + repr(brightness))

        b = []
        for i in range(len(self._brightnesses)):
            b.append(brightness)
        
        self.brightnesses = b
    
    # Returns current brightnesses of all LEDs
    @property
    def brightnesses(self):
        return self._brightnesses

    # Set brightnesses of all LEDs
    @brightnesses.setter
    def brightnesses(self, brightnesses):
        if self.pixels == False:
            return
        
        if self._debug == True:
            self._print(" -> Set brightnesses to " + repr(brightnesses))

        for i in range(len(self._brightnesses)):
            pixel = self.pixels[i]
            self._appl.led_driver.leds[pixel] = (
                int(self._colors[i][0] * brightnesses[i]),   # R
                int(self._colors[i][1] * brightnesses[i]),   # G
                int(self._colors[i][2] * brightnesses[i])    # B
            )

        self._brightnesses = brightnesses

    # Debug console output
    def _print(self, msg):
        if self._debug != True:
            return
        
        state_str = ""
        if self.pushed == True:
            state_str = "pushed"
        else:
            state_str = "off"
            
        Tools.print("Switch " + self.id + " (" + state_str + "): " + msg)


################################################################################################


# Base class for implementing switch driver classes
class SwitchDriver:
    
    # Initializes the switch. Called once before usage.
    def init(self):
        pass

    # Return if the switch is currently pushed (bool).
    @property
    def pushed(self):
        return False
    

