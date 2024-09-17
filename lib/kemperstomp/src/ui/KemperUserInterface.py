import displayio

from .DisplayLabel import DisplayLabel
from ..hardware.FontLoader import FontLoader
from ..Tools import Tools
from ...definitions import Colors
from ...config import Config


# Implements the Kemper UI
class KemperUserInterface:

    # config must be like:
    # {
    #     "effectLabelHeight": Height of the four effect unit label areas (pixels, default: 40)
    #     "initialInfoText": Text initially shown in the center area (where the rig name goes later on)
    #     "effectSlotLayout": Layout definition for effect slot labels (see DisplayLabel)
    #     "infoAreaLayout": Layout definition for the info area (rig name) label (see DisplayLabel)
    #     "debugAreaLayout": Layout definition for the debug area label (see DisplayLabel)
    # }
    def __init__(self, display, config):
        self.config = config        
        self.width = display.width
        self.height = display.height        
        self.effect_slots = []            # Effect slots are modeled in a list of DisplayLabel instances (DLY, REV, A, B)
        self.font_loader = FontLoader()   # Buffered font loader
        self.rig_date = None

        self._display = display
        self._debug_area = None

        self._slot_height = self.config["effectLabelHeight"]
        self._slot_config = self.config["effectSlotLayout"]
        self._info_area_config = self.config["infoAreaLayout"]
        self._info_initial_text = self.config["initialInfoText"]
        self._debug_config = self.config["debugAreaLayout"]

    # Show the user interface
    def show(self):
        # Init screen stacking (order matters here!)
        self._init_splash()
        self._init_info_area()
        self._init_slots()
        self._init_debug_area()
        
        self._display.tft.show(self.splash)

    # Returns the rig name currently set
    @property
    def rig_name(self):
        return self._info.text

    # Set a new rig name. Returns if changed
    @rig_name.setter
    def rig_name(self, name):
        self._info.text = name
        
    # Initialize display splash container
    def _init_splash(self):
        self.splash = displayio.Group()
        self._display.tft.rootgroup = self.splash

    # Initialize the effect slots
    def _init_slots(self):
        # Set up the handlers
        slot_width = int(self.width / 2)
        lowerY = self.height - self._slot_height

        self.effect_slots.append(DisplayLabel(self, 1,   lowerY, slot_width, self._slot_height, self._slot_config , "A", Colors.DEFAULT_SLOT_COLOR))
        self.effect_slots.append(DisplayLabel(self, 120, lowerY, slot_width, self._slot_height, self._slot_config , "B", Colors.DEFAULT_SLOT_COLOR))
        self.effect_slots.append(DisplayLabel(self, 1,   1,      slot_width, self._slot_height, self._slot_config , "DLY", Colors.DEFAULT_SLOT_COLOR))
        self.effect_slots.append(DisplayLabel(self, 120, 1,      slot_width, self._slot_height, self._slot_config , "REV", Colors.DEFAULT_SLOT_COLOR))

    # Initialize the info area (rig name)
    def _init_info_area(self):
        self._info = DisplayLabel(
            self, 
            0, 
            0, 
            self.width, 
            self.height,
            self._info_area_config,
            text = self._info_initial_text, 
            back_color = Colors.INFO_AREA_BACK_COLOR,
            text_color = Colors.INFO_AREA_TEXT_COLOR
        )
        
    # Initialize the debug area, if debugging is switched on
    def _init_debug_area(self):
        if Tools.get_option(Config, "debug") != True:
            return
        
        upperY = self.height - self._slot_height * 2
        self._debug_area = DisplayLabel(
            self, 
            1, 
            upperY, 
            self.width, 
            self._slot_height, 
            self._debug_config,
            back_color = Colors.DEBUG_BACK_COLOR
        )

    # Show a debug message on the UI if debugging is switched on
    def debug(self, message):
        if self._debug_area == None:
            return
        
        self._debug_area.text = message