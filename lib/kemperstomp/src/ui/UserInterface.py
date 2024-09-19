import displayio

from .DisplayLabel import DisplayLabel
from .DisplayArea import DisplayArea
from ..hardware.FontLoader import FontLoader
from ..Tools import Tools
from ...display import DisplayAreaDefinitions


# Implements the UI
class UserInterface:

    # config must be like:
    # {    
    #     "slotLabelHeight": Height of the four effect unit label areas (pixels, default: 40)
    #     "initialInfoText": Text initially shown in the center area (where the rig name goes later on)
    #     "slotLayout": Layout definition for effect slot labels (see DisplayLabel)
    #     "infoAreaLayout": Layout definition for the info area (rig name) label (see DisplayLabel)
    #     "statsAreaLayout": Layout definition for the statistics area label (see DisplayLabel)
    #     "areas": Area definitions. See DisplayAreaDefinitions (which is the default)
    # }
    def __init__(self, display, config):
        self.config = config                    # UI configuration
        self.font_loader = FontLoader()         # Buffered font loader
        self.width = display.width
        self.height = display.height        

        self._display = display
        self._areas = []

        if Tools.get_option(self.config, "areas") == False:
            self.config["areas"] = DisplayAreaDefinitions

        # Init screen stacking (order matters here!)
        self._init_splash()
        self._init_areas()

    # Show the user interface
    def show(self):
        self._display.tft.show(self.splash)

    # Initialize display splash container
    def _init_splash(self):
        self.splash = displayio.Group()
        self._display.tft.rootgroup = self.splash

    # Initialize the slots
    def _init_areas(self):
        for area_def in self.config["areas"]:
            self._areas.append(
                DisplayArea(
                    self,
                    area_def
                )
            )
        
    # Returns an area by ID, or None
    def area(self, id):
        for a in self._areas:
            if a.id == id:
                return a
        raise Exception("Display area " + repr(id) + " not found")

    # Returns a label according to the passed config:
    # {
    #     "area": Area ID (mandatory)
    #     "index": Index (optional), if not set, the first element will be returned
    # }
    def get_label(self, display_config):
        display_area = display_config["area"]
        index = Tools.get_option(display_config, "index", 0)

        return self.area(display_area).get(index)
