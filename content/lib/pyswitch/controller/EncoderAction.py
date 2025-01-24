from ..misc import Updateable

from adafruit_midi.system_exclusive import SystemExclusive

class EncoderAction(Updateable):
    def __init__(self, 
                 mapping,                          # Parameter mapping to be controlled
                 max_value = None,                 # Maximum value of the mapping (set to None for auto-detect: 16383 for NRPN, 127 for CC)
                 step_width = None,                # Increment/Decrement for one encoder step. Set to None for auto-detect (NRPN: 160, CC: 1)
                 enable_callback = None            # Callback to set enabled state (optional). Must contain an enabled(action) function.                 
        ):
        if isinstance(mapping.set, SystemExclusive):
            if max_value == None:
                max_value = 16383
            if step_width == None:
                step_width = 160
        else:
            if max_value == None:
                max_value = 127
            if step_width == None:
                step_width = 1

        self.__mapping = mapping
        self.__max_value = max_value
        self.__step_width = step_width
        self.__enable_callback = enable_callback
        self.__last_pos = -1
        self.__last_value = -1
                
    @property
    def enabled(self):
        return self.__enable_callback.enabled(self) if self.__enable_callback else True

    def init(self, appl):
        self.__appl = appl

        appl.client.register(self.__mapping)

    def update(self):
        self.__appl.client.request(self.__mapping)

    # Process the current encoder position
    def process(self, position):
        if self.__last_pos == -1:
            self.__last_pos = position

        if self.__last_pos == position:
            return
                        
        if self.__mapping.value == None:
            return
    
        add_value = (position - self.__last_pos) * self.__step_width        
        self.__last_pos = position

        v = self.__mapping.value + add_value
        if v < 0:
            v = 0
        if v > self.__max_value:
            v = self.__max_value

        if self.__last_value != v:
            self.__last_value = v
            
            # Send MIDI message for new value
            self.__appl.client.set(self.__mapping, v)
