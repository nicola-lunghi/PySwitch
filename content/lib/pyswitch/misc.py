from time import monotonic

from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive


# Color definitions (can be used for LEDs and labels)
class Colors:
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    DARK_YELLOW = (130, 130, 0)
    ORANGE = (255, 125, 0)
    RED = (255, 0, 0)
    PINK = (255, 125, 70)
    PURPLE = (180, 0, 120)
    DARK_PURPLE = (100, 0, 65)
    LIGHT_GREEN = (100, 255, 100)
    GREEN = (0, 255, 0)
    DARK_GREEN = (73, 110, 41)      #(0, 100, 0)
    TURQUOISE = (64, 242, 208)
    BLUE = (0, 0, 255)
    DARK_BLUE = (0, 0, 120)
    GRAY = (190, 190, 190)
    DARK_GRAY = (50, 50, 50)
    BLACK = (0, 0, 0)


####################################################################################################


class Defaults:

    # Default background color for display slots
    DEFAULT_LABEL_COLOR = (50, 50, 50)   

    # Default color for switches
    DEFAULT_SWITCH_COLOR = (255, 255, 255)


####################################################################################################


# Generic tools
class Tools:

    # Read a value from an option dictionary with an optional default value
    @staticmethod
    def get_option(config, name, default = False):
        if not config:
            return default
        if name not in config:
            return default        
        return config[name]

    # Print (for debugging only!)
    @staticmethod
    def print(msg):  # pragma: no cover
        print(msg)

    # Returns a current timestmap in integer milliseconds
    @staticmethod
    def get_current_millis():
        return int(monotonic() * 1000)
        
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

    # Compare two MIDI messages
    @staticmethod
    def compare_midi_messages(a, b):
        if a.__class__.__name__ != b.__class__.__name__:
            return False

        if isinstance(a, SystemExclusive):            
            return a.data == b.data and a.manufacturer_id == b.manufacturer_id

        if isinstance(a, ControlChange):
            return a.control == b.control
        
        return a == b
    
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


#####################################################################################################################################


# Base class for everything that needs to be updated regularily
class Updateable:
    def update(self):
        pass   # pragma: no cover

    def reset(self):
        pass   # pragma: no cover


#####################################################################################################################################


# Base class for handling updateables
class Updater:
    def __init__(self):
        self._updateables = []

    @property
    def updateables(self):
        return self._updateables

    # Add a new Updateable
    def add_updateable(self, u):
        if not isinstance(u, Updateable):
            return
        
        self._updateables.append(u)

    # Update all updateables. 
    def update(self):
        for u in self._updateables:            
            u.update()

    # Reset all updateables
    def reset(self):
        for u in self._updateables:
            u.reset()


#####################################################################################################################################


# Base class for event distributors (who call listeners)
class EventEmitter:
    def __init__(self): 
        self.listeners = []

     # Adds a listener, and returns True if added, False if already existed.
    def add_listener(self, listener):
        if listener in self.listeners:
            return False
        
        self.listeners.append(listener)
        return True
    

###############################################################################################################


# Periodic update helper    
class PeriodCounter:
    def __init__(self, interval_millis):
        self._interval_millis = int(interval_millis)

        self._last_reset = 0

    @property
    def interval(self):
        return self._interval_millis
    
    # Resets the period counter to the current time
    def reset(self):
        self._last_reset = Tools.get_current_millis()

    # Returns if the period has been exceeded. If yes, it lso resets
    # the period to the current time.
    @property
    def exceeded(self):
        current_time = Tools.get_current_millis()
        if self._last_reset + self._interval_millis < current_time:
            self._last_reset = current_time
            return True
        return False
            
