from ....Tools import Tools
from .....config import Config
from .....definitions import Colors

# Base class for actions. All functionality is encapsulated in a class for each, 
# inheriting from Action.
class Action:
    
    # Factory for creating actions by type (= class name of derivative of Action).
    # All created classes must have the same constructor parameters as this method.
    @staticmethod
    def get_instance(appl, switch, config):
        class_name = config["type"]

        module = __import__("kemperstomp.src.controller.actions." + class_name, globals(), locals(), [class_name])
        class_def = getattr(module, class_name)
        return class_def(appl, switch, config)

    # config: See FootSwitch    
    def __init__(self, appl, switch, config):
        self.appl = appl
        self.switch = switch
        self.config = config
        self.id = self.switch.id + " | " + self.__class__.__name__

        self.label = self._get_action_display()   # DisplayLabel instance the action is connected to (or None).

    # Called when the switch is pushed down
    def push(self):
        pass

    # Called when the switch is released
    def release(self):
        pass

    # Will be called on every tick, whether a MIDI message has been received or not
    # (in the latter case None is passed).
    def process(self, midi_message):
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
        
        display_area = self.config["display"]["area"]
        index = self.config["display"]["index"]

        area_labels = self.appl.ui.labels(display_area)
        
        if index >= len(area_labels):
            raise Exception("Invalid label index: " + str(index))

        label = area_labels[index]        
        label.text = Tools.get_option(self.config["display"], "text", "")

        return label

    # Print to the debug console
    def print(self, msg):
        if Tools.get_option(Config, "debugActions") != True:
            return
        
        Tools.print("Action " + self.id + ": " + msg)
