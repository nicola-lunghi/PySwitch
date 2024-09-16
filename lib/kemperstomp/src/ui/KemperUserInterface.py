import displayio

from .DisplayLabel import DisplayLabel

from ..hardware.FontLoader import FontLoader
from ..Tools import Tools

from ...kemperstomp_def import Colors
from ...kemperstomp_config import Config


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
        self.display = display
        self.width = display.width
        self.height = display.height
        self.config = config
        self.debug_area = None
        self.rig_name = None
        self.rig_date = None

        self.slot_height = self.config["effectLabelHeight"]
        self.slot_config = self.config["effectSlotLayout"]
        self.info_area_config = self.config["infoAreaLayout"]
        self.info_initial_text = self.config["initialInfoText"]
        self.debug_config = self.config["debugAreaLayout"]

        # Effect slots are modeled in a list of DisplayLabel instances (DLY, REV, A, B)
        self.effect_slots = []

        # Font loader (buffered)
        self.font_loader = FontLoader()

    # Show the user interface
    def show(self):
        # Init screen stacking (order matters here!)
        self._init_splash()
        self._init_info_area()
        self._init_slots()
        self._init_debug_area()
        
        self.display.tft.show(self.splash)

    # Set a new rig name. Returns if changed
    def set_rig_name(self, name):
        if self.rig_name == name:
            return False
        
        self.rig_name = name
        self.info.set_text(self.rig_name)
        return True

    # React to a new rig date. Returns if changed
    def set_rig_date(self, date):
        if self.rig_date == date:
            return False
        
        self.rig_date = date
        return True
        
    # Initialize display splash container
    def _init_splash(self):
        self.splash = displayio.Group()
        self.display.tft.rootgroup = self.splash

    # Initialize the effect slots
    def _init_slots(self):
        # Set up the handlers
        slot_width = int(self.width / 2)
        lowerY = self.height - self.slot_height

        self.effect_slots.append(DisplayLabel(self, 1,   lowerY, slot_width, self.slot_height, self.slot_config , "A", Colors.DEFAULT_SLOT_COLOR))
        self.effect_slots.append(DisplayLabel(self, 120, lowerY, slot_width, self.slot_height, self.slot_config , "B", Colors.DEFAULT_SLOT_COLOR))
        self.effect_slots.append(DisplayLabel(self, 1,   1,      slot_width, self.slot_height, self.slot_config , "DLY", Colors.DEFAULT_SLOT_COLOR))
        self.effect_slots.append(DisplayLabel(self, 120, 1,      slot_width, self.slot_height, self.slot_config , "REV", Colors.DEFAULT_SLOT_COLOR))

    # Initialize the info area (rig name)
    def _init_info_area(self):
        self.info = DisplayLabel(
            self, 
            0, 
            0, 
            self.width, 
            self.height,
            self.info_area_config,
            text = self.info_initial_text, 
            back_color = Colors.INFO_AREA_BACK_COLOR,
            text_color = Colors.INFO_AREA_TEXT_COLOR
        )
        
    # Initialize the debug area, if debugging is switched on
    def _init_debug_area(self):
        if Tools.get_option(Config, "debug") != True:
            return
        
        upperY = self.height - self.slot_height * 2
        self.debug_area = DisplayLabel(
            self, 
            1, 
            upperY, 
            self.width, 
            self.slot_height, 
            self.debug_config,
            back_color = Colors.DEBUG_BACK_COLOR
        )

    # Show a debug message on the UI if debugging is switched on
    def debug(self, message):
        if self.debug_area == None:
            return
        
        self.debug_area.set_text(message)