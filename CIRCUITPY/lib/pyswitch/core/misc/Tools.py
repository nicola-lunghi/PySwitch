import time

from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive


# Generic tools
class Tools:

    # Read a value from an option dictionary with an optional default value
    @staticmethod
    def get_option(config, name, default = False):
        if name not in config:
            return default        
        return config[name]

    # Print (for debugging only!)
    @staticmethod
    def print(msg):
        print(msg)

    # Returns a current timestmap in integer milliseconds
    @staticmethod
    def get_current_millis():
        return int(time.monotonic() * 1000)
        
    # Stringifies a MIDI message.
    @staticmethod
    def stringify_midi_message(midi_message):
        if not midi_message:
            return repr(midi_message)
        
        ret = ""
        if isinstance(midi_message, SystemExclusive):
            # SysEx
            ret = Tools._stringify_midi_message_part(midi_message.manufacturer_id) + Tools._stringify_midi_message_part(midi_message.data)

        elif isinstance(midi_message, ControlChange):
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

    # Size (bytes) output formatting 
    # Taken from https://stackoverflow.com/questions/1094841/get-a-human-readable-version-of-a-file-size 
    @staticmethod
    def format_size(num, fill_up_to = 0, suffix = "B"):
        for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
            if abs(num) < 1024.0:
                return Tools.fill_up_to(f"{num:3.1f} {unit}{suffix}", num_spaces_at_right = fill_up_to)
            num /= 1024.0
        return Tools.fill_up_to(f"{num:.1f}Yi{suffix}", num_spaces_at_right = fill_up_to)

    # Fill up string with spaces. Needed here because CircuitPython does not seem to support the ljust() function of strings.
    @staticmethod
    def fill_up_to(str, num_spaces_at_right, fill_char = " "):
        if num_spaces_at_right <= 0:
            return str
        ret = str
        while len(ret) < num_spaces_at_right:
            ret += fill_char
        return ret
