from adafruit_midi.system_exclusive import SystemExclusive
from adafruit_midi.control_change import ControlChange

# Midi mapping for a client command. Contains commands to set or request a parameter
class ClientParameterMapping:
    # Takes MIDI messages as argument (ControlChange or SystemExclusive)
    def __init__(self, name = "", set = None, request = None, response = None, type = None, value = None):
        self.name = name          # Mapping name (used for debug output only)
        self.set = set            # MIDI Message to set the parameter
        self.request = request    # MIDI Message to request the value
        self.response = response  # Response template MIDI message for parsing the received answer        
        self.type = type          # Type of mapping
        self.value = value        # Value of the parameter (buffer). After receiving an answer, the value 
                                  # is buffered here.                                  

    def __eq__(self, other):
        if not other:
            return False
        
        if self.request != None:
            if other.request != None:
                return self._compare_messages(self.request, other.request)
            else:
                return False
        elif self.set != None:
            if other.set != None:
                return self._compare_messages(self.set, other.set)
            else:
                return False
        return False

    # Compare two MIDI messages
    def _compare_messages(self, a, b):
        if a.__class__.__name__ != b.__class__.__name__:
            return False

        if isinstance(a, SystemExclusive):            
            return a.data == b.data

        if isinstance(a, ControlChange):
            return a.control == b.control
        
        return a == b

    @property
    def can_set(self):
        return self.set != None

    @property
    def can_receive(self):
        return self.request != None
    
    # Returns a copy of the mapping with no request/response and value. Use this
    # if you have performance issues with too much requests.
    @property
    def set_only(self):
        return ClientParameterMapping(
            name = self.name,
            set = self.set,
            type = self.type
        )

