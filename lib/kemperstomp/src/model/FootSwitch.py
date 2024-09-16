import random

import digitalio

from ..Tools import Tools
from ..actions.ActionFactory import ActionFactory

from ...kemperstomp_def import Colors

# Controller class for a Foot Switch. Each foot switch has three Neopixels.
class FootSwitch:

    # Number of NeoPixels for one Footswitch
    NUM_PIXELS = 3

    # config must be a dictionary holding the following attributes:
    # { 
    #     "assignment": {
    #         "port": The board GPIO pin definition to be used for this switch (for example board.GP1)
    #         "pixels": List of three indexes for the Neopixels that belong to this switch, for example (0, 1, 2)
    #     },
    #     "actions": {
    #         "type": Action type. Allowed values: See the Actions class in kemperstomp_def.py
    #         ...     (individual options depending on the action)
    #     },
    #     "initialColors": [   Initial colors to set. Optional, if not set, the default initial color set is generated.
    #         Colors.RED,
    #         Colors.YELLOW,
    #         Colors.ORANGE
    #     ],
    #     "initialBrightness": Initial brightness. If not set, 1 is used. [0..1]
    # }
    def __init__(self, appl, config):
        self.appl = appl
        self.config = config        
        
        self.colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
        self.pushed = False
        self.pixels = Tools.get_option(self.config["assignment"], "pixels")

        self._initial_colors()
        self._init_switch()     
        self._init_actions()

    # Set up action instances
    def _init_actions(self):
        self.actions = []
        action_factory = ActionFactory()

        for action_config in self.config["actions"]:
            action = action_factory.get(
                self.appl,
                self,
                action_config
            )
            self.actions.append(action)

    # Set some initial colors on the neopixels
    def _initial_colors(self):
        if self.pixels == False:
            # No LEDs defined for the switch
            return
        
        initial_brightness = Tools.get_option(self.config, "initialBrightness", 1)

        if Tools.get_option(self.config, "initialColors") != False:
            # Colors from config file, if set
            self.set_colors(self.config["initialColors"])            
            self.set_brightness(initial_brightness)
            return

        # Default color scheme: Random from a list of colors
        available_colors = (Colors.GREEN, Colors.YELLOW, Colors.RED)  # Colors to be used (in that order)
        start_index = random.randint(0, len(available_colors)-1)      # Random start index  
        self.set_colors([
            available_colors[start_index],
            available_colors[(start_index + 1 ) % len(available_colors)],
            available_colors[(start_index + 2 ) % len(available_colors)]
        ])
        self.set_brightness(initial_brightness)
    
    # Initializes the switch
    def _init_switch(self):
        self.switch = digitalio.DigitalInOut(self.config["assignment"]["port"]) 
        
        self.switch.direction = digitalio.Direction.INPUT
        self.switch.pull = digitalio.Pull.UP
        
    # Return if the switch is currently pushed
    def is_pushed(self):
        return self.switch.value == False  # Inverse logic!

    # Set switch colors (each of the LEDs individually). Does not take any effect until
    # set_brightness is called!
    def set_colors(self, colors):
        if len(colors) != len(self.colors):
            raise Exception("Invalid amount of colors: " + len(colors))
        
        self.colors = colors        

    # Set switch color (all three LEDs equally). Does not take any effect until
    # set_brightness is called!
    def set_color(self, color):
        for i in range(len(self.colors)):
            self.colors[i] = color

    # Set brightness
    def set_brightness(self, brightness):
        if self.pixels == False:
            return
        
        for i in range(len(self.colors)):
            pixel = self.pixels[i]
            self.appl.led_driver.leds[pixel] = (
                int(self.colors[i][0] * brightness),   # R
                int(self.colors[i][1] * brightness),   # G
                int(self.colors[i][2] * brightness)    # B
            )
    
    # Process the switch: Check if it is currently pushed, set state accordingly
    # and send the MIDI messages configured.
    def process(self, midi_message):
        # Call the receive routine on every tick
        self._process_actions_receive(midi_message)

        # Is the switch currently pushed? If not, return false.
        if self.is_pushed() == False:
            if self.pushed == True:
                self.pushed = False
                self._process_actions_up()                

            return

        # Switch is pushed: Has it been pushed before already? 
        if self.pushed == True:
            return 
        
        # Mark as pushed (prevents redundant messages in the following ticks, when the switch can still be down)
        self.pushed = True
        self._process_actions_down()

    # Processes all actions assigned to the switch (down)
    def _process_actions_down(self):
        for action in self.actions:
            action.down()

    # Processes all actions assigned to the switch (up)
    def _process_actions_up(self):
        for action in self.actions:
            action.up()

    # Processes all receive routines
    def _process_actions_receive(self, midi_message):
        for action in self.actions:
            action.receive(midi_message)

    # Sets a value in the config object of all actions
    def set_action_config(self, name, value):
        for action in self.actions:
            action.set_config_value(name, value)
