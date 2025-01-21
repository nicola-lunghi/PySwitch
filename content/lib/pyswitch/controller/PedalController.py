from ..misc import get_option, PeriodCounter

# Controller class for a Foot Switch. Each foot switch has three Neopixels.
class PedalController:

    # config must be a dictionary holding the following attributes:
    # { 
    #     "assignment": {
    #         "model":         Model instance for the potentiometer hardware. Must implement an init() method and a .value property.
    #     },
    #
    #     "actions": [         Array of actions. Entries must be objects like PedalAction (see below)
    #         ExampleAction({
    #             ...                  
    #         }),
    #         ...
    #     ]
    # }
    def __init__(self, appl, config):
        self.__pot = config["assignment"]["model"]
        self.__pot.init()

        self.__actions = get_option(config, "actions", [])
        
        # Init actions
        for action in self.__actions:
            action.init(appl)
                    
    # Process the pedal
    def process(self):
        value = self.__pot.value

        for action in self.__actions:
            if not action.enabled:
                continue

            action.process(value)


################################################################################################


## Base class for implementing pot driver classes
#class PotentiometerDriver:
#    
#    # Initializes the pot. Called once before usage.
#    def init(self):
#        pass
#
#    # Returns the value of the pot (integer in range [0..65535])
#    @property
#    def value(self):
#        return 0


################################################################################################


class PedalAction:
    def __init__(self, 
                 mapping,              # Parameter mapping to be controlled
                 max_value = 16384,    # Maximum value plus one (!) of the mapping (16384 for NRPN, 128 for CC)
                 max_frame_rate = 24   # Maximum frame rate for sending MIDI values (fps)
        ):
        self.__mapping = mapping
        self.__factor = max_value / 65536
        self.__period = PeriodCounter(1000 / max_frame_rate)

    def init(self, appl):
        self.__appl = appl

    # Process a value in range [0..65535]
    def process(self, value):
        if self.__period.exceeded:
            self.__appl.client.set(self.__mapping, value * self.__factor)
        