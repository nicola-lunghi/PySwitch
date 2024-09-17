import random
import digitalio

from .actions.ActionFactory import ActionFactory
from ..Tools import Tools
from ...definitions import Colors, ActionEvents


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
    #         "type":               Action type. Allowed values: See the Actions class in kemperstomp_def.py
    #         "events": [           Array of events to trigger the action 
    #             ActionEvents.SWITCH_DOWN
    #         ],
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
        
        self._appl = appl
        self._actions = []
        self._colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
        self._brightness = 0
        self._pushed_state = False

        self._initial_switch_colors()
        self._init_switch()     
        self._init_actions()

    # Set up action instances
    def _init_actions(self):        
        action_factory = ActionFactory()

        for action_config in self.config["actions"]:
            action = action_factory.get(
                self._appl,
                self,
                action_config
            )
            self._actions.append(action)

    # Set some initial colors on the neopixels
    def _initial_switch_colors(self):
        if self.pixels == False:
            # No LEDs defined for the switch
            return
        
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
        self.switch = digitalio.DigitalInOut(self.config["assignment"]["port"]) 
        
        self.switch.direction = digitalio.Direction.INPUT
        self.switch.pull = digitalio.Pull.UP
        
    # Return if the switch is currently pushed
    @property
    def pushed(self):
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
        
        self._colors = colors        

    # Color (this just uses the first one)
    @property
    def color(self):
        return self._colors[0]

    # Set switch color (all three LEDs equally). Does not take any effect until
    # set_brightness is called!
    @color.setter
    def color(self, color):
        for i in range(len(self._colors)):
            self._colors[i] = color

    # Returns current brightness
    @property
    def brightness(self):
        return self._brightness

    # Set brightness
    @brightness.setter
    def brightness(self, brightness):
        if self.pixels == False:
            return
        
        for i in range(len(self._colors)):
            pixel = self.pixels[i]
            self._appl.led_driver.leds[pixel] = (
                int(self._colors[i][0] * brightness),   # R
                int(self._colors[i][1] * brightness),   # G
                int(self._colors[i][2] * brightness)    # B
            )

        self._brightness = brightness

    # Process the switch: Check if it is currently pushed, set state accordingly
    # and send the MIDI messages configured.
    def process(self, midi_message):
        # Let all actions process the message if they like (or do other periodic stuff)
        self._process_actions_process(midi_message)

        # Is the switch currently pushed? If not, return false.
        if self.pushed == False:
            if self._pushed_state == True:
                self._pushed_state = False
                self._process_actions_event(ActionEvents.SWITCH_UP)

            return

        # Switch is pushed: Has it been pushed before already? 
        if self._pushed_state == True:
            return 
        
        # Mark as pushed (prevents redundant messages in the following ticks, when the switch can still be down)
        self._pushed_state = True
        self._process_actions_event(ActionEvents.SWITCH_DOWN)

    # Processes all actions assigned to the switch if they have the given event registered in their config
    def _process_actions_event(self, event):
        for action in self._actions:
            if action.has_event(event) == True:
                action.trigger(event)

    # Executes all action's process() method
    def _process_actions_process(self, midi_message):
        for action in self._actions:
            action.process(midi_message)

