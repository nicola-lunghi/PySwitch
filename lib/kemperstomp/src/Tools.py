import time
from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive

from ..config import Config

# Generic tools
class Tools:

    # Dim factor for dimming colors. Will be set to configured value on first usage.
    DIM_FACTOR = -1  

    # Read a value from an option dictionary with an optional default value
    @staticmethod
    def get_option(config, name, default = False):
        if name not in config:
            return default        
        return config[name]

    # Print if we are in console mode    
    @staticmethod
    def print(msg):
        if Tools.get_option(Config, "debug") != True:
            return
        print(msg)

    # Returns a current timestmap in integer milliseconds
    @staticmethod
    def get_current_millis():
        return int(time.monotonic() * 1000)
    
    # Dims a passed color for display of disabled state
    @staticmethod
    def dim_color(color):
        if Tools.DIM_FACTOR == -1:
            Tools.DIM_FACTOR = Config["displayDimFactor"]

        return (
            int(color[0] * Tools.DIM_FACTOR),
            int(color[1] * Tools.DIM_FACTOR),
            int(color[2] * Tools.DIM_FACTOR)
        )
    
    # Stringifies a MIDI message.
    @staticmethod
    def stringify_midi_message(midi_message):
        if midi_message == None:
            return repr(None)
        
        ret = ""
        if isinstance(midi_message, SystemExclusive) == True:
            # SysEx
            ret = Tools._stringify_midi_message_part(midi_message.manufacturer_id) + Tools._stringify_midi_message_part(midi_message.data)

        elif isinstance(midi_message, ControlChange) == True:
            # CC
            ret = repr(midi_message.control) + ", " + repr(midi_message.value)

        else:
            # All others
            ret = repr(midi_message)

        # Add class name
        return ret + " (" + midi_message.__class__.__name__ + ")"
    
    # Internal helper for stringify_midi_message(): Creates a readable hex 
    # value list from the passed data.
    @staticmethod
    def _stringify_midi_message_part(part):
        intlist = list(part)
        hexlist = ""
        for i in range(len(intlist)):
            end = ", "
            if i == len(intlist) - 1:
                end = ""
            hexlist = hexlist + hex(intlist[i])[2:] + end

        return "[" + hexlist + "]"
