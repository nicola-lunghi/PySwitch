import displayio

from .DisplayArea import DisplayArea
from ..hardware.FontLoader import FontLoader
from ..Tools import Tools


# Implements the UI
class UserInterface:
    def __init__(self, display, config):
        self.config = config
        self.width = display.width
        self.height = display.height        
        self.splash = None

        self._display = display
        self._areas = []

        self._area_definitions = []

    # Must be called before usage, after setting the areas
    def setup(self):
        # Buffered font loader
        self.font_loader = FontLoader()

        # Init screen stacking (order matters here!)
        self._init_splash()
        self._init_areas()

    # Show the user interface
    def show(self):
        if self.splash == None:
            raise Exception("setup() has not been called")
        
        # Set up the display areas internally (late). This avoids unnecessary 
        # re-creating of splash items (after this, every change to the dimensions
        # of a display label will trigger a performance-costly re-creation of the (Round)Rects)
        for area in self._areas:
            area.init()

        self._display.tft.show(self.splash)

    # Initialize display splash container
    def _init_splash(self):
        self.splash = displayio.Group()
        self._display.tft.rootgroup = self.splash

    # Initialize the slots
    def _init_areas(self):
        for area_def in self._area_definitions:
            self._areas.append(
                DisplayArea(
                    self,
                    area_def
                )
            )
        
    # Adds a display area definition. Can only be called before setup().
    # See DisplayArea.
    def add_area_definition(self, area_def):
        if self.splash != None:
            raise Exception("Cannot add further areas after setup()")
        
        self._area_definitions.append(area_def)

    # Returns an area by ID, or None. Can only be called after setup().
    def area(self, id):
        if self.splash == None:
            raise Exception("setup() has not been called")
        
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
