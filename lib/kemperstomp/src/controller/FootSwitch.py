import random
import digitalio

from .actions.base.Action import Action
from ..Tools import Tools
from ...definitions import Colors


# Controller class for a Foot Switch. Each foot switch has three Neopixels.
class FootSwitch:

    # config must be a dictionary holding the following attributes:
    # { 
    #     "assignment": {
    #         "port": The board GPIO pin definition to be used for this switch (for example board.GP1)
    #         "pixels": List of three indexes for the Neopixels that belong to this switch, for example (0, 1, 2)
    #     },
    #     "actions": {
    #         "type":               Action type. Allowed values: See the Actions class in kemperstomp_def.py
    #         ...                   (individual options depending on the specific action type)
    #     },
    #     "initialColors": [   Initial colors to set. Optional, if not set, the default initial color set is generated.
    #         Colors.RED,
    #         Colors.YELLOW,
    #         Colors.ORANGE
    #     ],
    #     "initialBrightness": Initial brightness. If not set, 1 is used. [0..1]
    # }
    def __init__(self, appl, config):
        self.config = config        
        self.pixels = Tools.get_option(self.config["assignment"], "pixels")
        self.switch = None

        self._port = self.config["assignment"]["port"]
        self._appl = appl
        self._colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
        self._brightnesses = [0, 0, 0]
        self._pushed_state = False
        self.id = Tools.get_option(self.config["assignment"], "name", repr(self._port))
        self._debug = Tools.get_option(self._appl.config, "debugSwitches")

        self._initial_switch_colors()
        self._init_switch()     
        self._init_actions()

    # Set up action instances
    def _init_actions(self):
        if self._debug == True:
            self._print("Init actions")
        
        self._actions = []
        self.actions_using_leds = []
        
        for action_config in self.config["actions"]:
            action = Action.get_instance(
                self._appl,
                self,
                action_config
            )

            self._actions.append(action)

            if action.uses_switch_leds == True:
                self.actions_using_leds.append(action)

        for action in self._actions:            
            action.init()
            action.update_displays()

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
        start_index = random.randint(0, len(available_colors)-1)      # Random start index  
        self.colors = [
            available_colors[start_index],
            available_colors[(start_index + 1 ) % len(available_colors)],
            available_colors[(start_index + 2 ) % len(available_colors)]
        ]
        self.brightness = initial_brightness
    
    # Initializes the switch
    def _init_switch(self):
        if self._debug == True:
            self._print("Init GPIO")

        self.switch = digitalio.DigitalInOut(self._port) 
        
        self.switch.direction = digitalio.Direction.INPUT
        self.switch.pull = digitalio.Pull.UP
        
    # Return if the switch is currently pushed
    @property
    def pushed(self):
        if self.switch == None:
            return False
        return self.switch.value == False  # Inverse logic!

    # Colors of the switch (array)
    @property
    def colors(self):
        return self._colors

    # Set switch colors (each of the LEDs individually). Does not take any effect until
    # set_brightness is called!
    @colors.setter
    def colors(self, colors):
        if len(colors) != len(self._colors):
            raise Exception("Invalid amount of colors: " + len(colors))
        
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
        return self.brightnesses[0]

    # Set brightness equally of all LEDs
    @brightness.setter
    def brightness(self, brightness):
        self.brightnesses = [brightness, brightness, brightness]
    
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

        for i in range(len(self._colors)):
            pixel = self.pixels[i]
            self._appl.led_driver.leds[pixel] = (
                int(self._colors[i][0] * brightnesses[i]),   # R
                int(self._colors[i][1] * brightnesses[i]),   # G
                int(self._colors[i][2] * brightnesses[i])    # B
            )

        self._brightnesses = brightnesses

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
        for action in self._actions:
            action.update()

    # Reset all actions
    def reset(self):
        for action in self._actions:
            action.reset()

    # Processes all push actions assigned to the switch 
    def _process_actions_push(self):
        for action in self._actions:
            if self._debug == True:
                self._print("Push action " + action.id)

            action.push()

    # Processes all release actions assigned to the switch 
    def _process_actions_release(self):
        for action in self._actions:
            if self._debug == True:
                self._print("Release action " + action.id)
                
            action.release()

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