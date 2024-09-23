from ..Tools import Tools
from .InfoParameter import InfoParameter

# Manages the display areas of the program, updating their values.
class InfoParameterController:

    # config must be an array of configurations for DisplayAreaController.
    def __init__(self, appl, config, debug):
        self._appl = appl
        self._config = config
        self._debug = debug

        self._init_areas()

    # Initialize all areas
    def _init_areas(self):
        self._areas = []

        for definition in self._config:
            self._areas.append(
                InfoParameter(
                    self._appl,
                    definition, 
                    self._debug
                )
            )

    # Called on every update period
    def update(self):
        for area in self._areas:
            area.update()

