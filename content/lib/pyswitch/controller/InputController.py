from ..misc import get_option, PeriodCounter

# Controller class for expression pedals, encoders and other inputs
class InputController:

    # config must be a dictionary holding the following attributes:
    # { 
    #     "assignment": {
    #         "model":         Model instance for the hardware. Must implement an init() method and a .value property.
    #     },
    #
    #     "actions": [         Array of actions. Entries must be objects of type InputAction (see below)
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
                    
    # Process the input
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


class InputAction:
    def __init__(self, 
                 mapping,                 # Parameter mapping to be controlled
                 max_value = 16384,       # Maximum value plus one (!) of the mapping (16384 for NRPN, 128 for CC)
                 max_frame_rate = 24,     # Maximum frame rate for sending MIDI values (fps)
                 num_steps = 128,         # Number of steps to be regarded as different (saves MIDI traffic at the cost of precision)
                 enable_callback = None,  # Callback to set enabled state (optional). Must contain an enabled(action) function.
                 transfer = None          # Transfer handler instance. See TransferFunction below. If used, this disables the num_steps parameter.
                                          # When designing your transfer function, take care that the output values do not change too often as this 
                                          # imposes performance issues! 
        ):
        self.__mapping = mapping
        self.__factor = max_value / 65536
        self.__period = PeriodCounter(1000 / max_frame_rate)
        self.__enable_callback = enable_callback
        self.__step_width = int(65536 / num_steps)
        self.__last_value = -1
        self.__transfer = transfer

    @property
    def enabled(self):
        return self.__enable_callback.enabled(self) if self.__enable_callback else True

    def init(self, appl):
        self.__appl = appl

    # Process a value in range [0..65535]
    def process(self, value):
        if self.__period.exceeded:
            if self.__transfer:
                # Use an external transfer function
                v = self.__transfer.get(value)
            else:
                # Scale and quantize
                v = value * self.__factor
                v = int(v / self.__step_width) * self.__step_width 

            if self.__last_value != v:
                # Update value on client
                self.__last_value = v
                self.__appl.client.set(self.__mapping, v)


# class TransferFunction:
#     # Input is the raw encoder value in range [0..65535]. Must return the value to be sent for the mapping, in its range.
#     def get(self, raw_value):
#         return 0