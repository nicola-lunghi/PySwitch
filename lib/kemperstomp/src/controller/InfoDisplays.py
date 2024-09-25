from .displays.ParameterInfoDisplay import ParameterInfoDisplay


# Manages the display areas of the program, updating their values.
class InfoDisplays:

    # config must be an array of configurations for InfoParameter (see there for details).
    def __init__(self, appl, config, debug):
        self._appl = appl
        self._config = config
        self._debug = debug

        self._init()

    # Initialize parameters
    def _init(self):
        self._parameters = []

        for definition in self._config:
            # Client parameter mapping: These are displayed using INfo Parameter
            self._parameters.append(
                ParameterInfoDisplay(
                    self._appl,
                    definition, 
                    self._debug
                )
            )

    # Called on every update period
    def update(self):
        for parameter in self._parameters:
            parameter.update()

    # Reset all parameters
    def reset(self):
        for parameter in self._parameters:
            parameter.reset()
