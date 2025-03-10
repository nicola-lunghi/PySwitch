from time import monotonic, localtime

from .controller.MidiController import SystemExclusive, ControlChange, ProgramChange, MIDIUnknownEvent

# PySwitch version
PYSWITCH_VERSION = "2.3.5"

# Default background color for display slots
DEFAULT_LABEL_COLOR = (50, 50, 50)   

# Default color for switches
DEFAULT_SWITCH_COLOR = (255, 255, 255)


####################################################################################################


# Color definitions (can be used for LEDs and labels)
class Colors:
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    DARK_YELLOW = (130, 130, 0)
    ORANGE = (255, 125, 0)
    RED = (255, 0, 0)
    LIGHT_RED = (255, 100, 100)
    PINK = (255, 125, 70)
    PURPLE = (180, 0, 120)
    DARK_PURPLE = (100, 0, 65)
    LIGHT_GREEN = (100, 255, 100)
    GREEN = (0, 255, 0)
    DARK_GREEN = (73, 110, 41)      #(0, 100, 0)
    TURQUOISE = (64, 242, 208)
    BLUE = (0, 0, 255)
    LIGHT_BLUE = (100, 100, 255)
    DARK_BLUE = (0, 0, 120)
    GRAY = (190, 190, 190)
    DARK_GRAY = (50, 50, 50)
    BLACK = (0, 0, 0)


####################################################################################################


# Read a value from an option dictionary with an optional default value
def get_option(config, name, default = False):
    if not config:
        return default
    if name not in config:
        return default        
    return config[name]

# Print (for debugging only!)
def do_print(msg):  # pragma: no cover
    print(msg)

# Returns a current timestmap in integer milliseconds
def get_current_millis():
    return int(monotonic() * 1000)
    
# Returns a readable string with the current timestamp (local time)
def formatted_timestamp():
    ts = localtime()
    return f"{ str(ts.tm_year) }-{ "{:02d}".format(ts.tm_mon) }-{ "{:02d}".format(ts.tm_mday) } { "{:02d}".format(ts.tm_hour) }:{ "{:02d}".format(ts.tm_min) }:{ "{:02d}".format(ts.tm_sec) }"

# Stringifies a MIDI message.
def stringify_midi_message(midi_message):
    if not midi_message:
        return repr(midi_message)
    
    ret = ""
    if isinstance(midi_message, SystemExclusive):
        # SysEx
        ret = f"{ _stringify_midi_message_part(midi_message.manufacturer_id) }{ _stringify_midi_message_part(midi_message.data) } String: { ''.join(chr(int(c)) for c in list(midi_message.data)) }"

    elif isinstance(midi_message, ControlChange):    
        # CC
        ret = repr(midi_message.control) + ", " + repr(midi_message.value)

    elif isinstance(midi_message, ProgramChange):    
        # PC
        ret = repr(midi_message.patch)

    elif isinstance(midi_message, MIDIUnknownEvent):    
        # Unknown
        ret = repr(midi_message.status)
    
    else:
        # All others
        ret = repr(midi_message)

    # Add class name
    return f"{ ret } ({ midi_message.__class__.__name__ })"

# Internal helper for stringify_midi_message(): Creates a readable hex 
# value list from the passed data.
def _stringify_midi_message_part(part):
    intlist = list(part)
    hexlist = ""
    for i in range(len(intlist)):
        end = ", "
        if i == len(intlist) - 1:
            end = ""
        hexlist = hexlist + hex(intlist[i])[2:] + end

    return f"[{ hexlist }]"

# Compare two MIDI messages
def compare_midi_messages(a, b):
    if isinstance(a, SystemExclusive) and isinstance(b, SystemExclusive):
        return a.data == b.data and a.manufacturer_id == b.manufacturer_id

    elif isinstance(a, ControlChange) and isinstance(b, ControlChange):
        return a.control == b.control
    
    elif isinstance(a, ProgramChange) and isinstance(b, ProgramChange):
        return a.patch == b.patch

    elif isinstance(a, MIDIUnknownEvent) and isinstance(b, MIDIUnknownEvent):
        return a.status == b.status

    else:
        return a == b

# Size (bytes) output formatting 
# Taken from https://stackoverflow.com/questions/1094841/get-a-human-readable-version-of-a-file-size 
def format_size(num, fill_up_to_num = 0, suffix = "B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return fill_up_to(f"{num:3.1f} {unit}{suffix}", fill_up_to_num)
        num /= 1024.0
    return fill_up_to(f"{num:.1f}Yi{suffix}", fill_up_to_num)

# Fill up string with spaces. Needed here because CircuitPython does not seem to support the ljust() function of strings.
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
        self.updateables = []

    # Add a new Updateable
    def add_updateable(self, u):
        if not isinstance(u, Updateable):
            return
        
        if u in self.updateables:
            return
        
        self.updateables.append(u)

    # Update all updateables. 
    def update(self):
        for u in self.updateables:            
            u.update()

    # Reset all updateables
    def reset(self):
        for u in self.updateables:
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
        self.interval = int(interval_millis)

        self.__last_reset = 0

    # Resets the period counter to the current time
    def reset(self):
        self.__last_reset = get_current_millis()

    # Returns the amount of milliseconds passed since the last reset
    @property
    def passed(self):
        return get_current_millis() - self.__last_reset

    # Returns if the period has been exceeded. If yes, it lso resets
    # the period to the current time.
    @property
    def exceeded(self):
        current_time = get_current_millis()
        if self.__last_reset + self.interval < current_time:
            self.__last_reset = current_time
            return True
        return False
            
