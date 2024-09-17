import displayio

from .DisplayLabel import DisplayLabel
from ..hardware.FontLoader import FontLoader
from ..Tools import Tools
from ...definitions import DisplayAreaDefinitions


# Implements the Kemper UI
class KemperUserInterface:

    # switches_config is only needed when numHeaderSlots/numFooterSlots are not set).
    #
    # config must be like:
    # {    
    #     "slotLabelHeight": Height of the four effect unit label areas (pixels, default: 40)
    #     "initialInfoText": Text initially shown in the center area (where the rig name goes later on)
    #     "slotLayout": Layout definition for effect slot labels (see DisplayLabel)
    #     "infoAreaLayout": Layout definition for the info area (rig name) label (see DisplayLabel)
    #     "statsAreaLayout": Layout definition for the statistics area label (see DisplayLabel)
    # }
    def __init__(self, display, config, switches_config):
        self.config = config                    # UI configuration
        self.font_loader = FontLoader()         # Buffered font loader
        self.width = display.width
        self.height = display.height        

        self._display = display
        self._info_area_layout = self.config["infoAreaLayout"]
        self._areas = DisplayAreaDefinitions

        self._stats_area = None
        self._stats_layout = Tools.get_option(self.config, "statsAreaLayout")
        self._stats_height = Tools.get_option(self.config, "statsAreaHeight")

        # Checks how much slots each area needs, and prepares _areas 
        self._prepare_areas(switches_config)

        # Init screen stacking (order matters here!)
        self._init_splash()
        self._init_info_area()
        self._init_slot_areas()
        self._init_stats_area()

    @property
    def info_text(self):
        return self._info.text

    @info_text.setter
    def info_text(self, text):
        self._info.text = text
        
    # Returns the labels for a given display position, or None if not found
    def labels(self, display_area):
        for label_def in self._areas:
            if label_def["area"] != display_area:
                continue

            return label_def["labels"]
        return None

    # If a switches configuration is passed and the number of slots in header/footer
    # has not been defined manually, this detects the needed areas from the switches 
    # configuration.
    def _prepare_areas(self, switches_config):
        for area in self._areas:
            area["labels"] = []
            area["num_slots"] = self._determine_num_of_switch_actions(switches_config, area["area"])

    # Determines how many positions are needed in one area (this is determined by the maximum index)
    def _determine_num_of_switch_actions(self, switches_config, display_area):
        max = -1
        for switch in switches_config:
            for action in switch["actions"]:
                if Tools.get_option(action, "display") == False:
                    continue

                if action["display"]["area"] != display_area:
                    continue

                if action["display"]["index"] > max:
                    max = action["display"]["index"]
                    
        return max + 1

    # Show the user interface
    def show(self):
        self._display.tft.show(self.splash)

    # Initialize display splash container
    def _init_splash(self):
        self.splash = displayio.Group()
        self._display.tft.rootgroup = self.splash

    # Initialize the slots
    def _init_slot_areas(self):
        for area in self._areas:
            self._create_area_labels(area)
        
    # Create the labels in one area
    def _create_area_labels(self, area):
        num_slots = area["num_slots"]
        if num_slots <= 0:
            return
        
        area_x = area["x"]
        area_y = area["y"]

        slot_width = area["width"] / num_slots
        slot_height = area["height"]
        slot_layout = area["layout"]
        area_name = Tools.get_option(area, "name", "UnknownArea")

        for i in range(num_slots):      
            area["labels"].append(
                DisplayLabel(
                    self, 
                    area_x + i * slot_width, 
                    area_y, 
                    slot_width, 
                    slot_height,
                    slot_layout,
                    id = area_name + " | " + str(i)
                )
            )
        
    # Initialize the _info area (normally showing the rig name), which takes the whole screen behind all other stuff
    def _init_info_area(self):
        self._info = DisplayLabel(
            self, 
            0, 
            0, 
            self.width, 
            self.height,
            self._info_area_layout,
            id = "Info"
        )
        
    ##############################################################################################################################

    # Initialize the statistics area, if switched on.
    def _init_stats_area(self):
        if Tools.get_option(self.config, "showFrameStats") != True:
            return
        
        upperY = self.height - self._stats_height * 2
        self._stats_area = DisplayLabel(
            self, 
            1, 
            upperY, 
            self.width, 
            self._stats_height, 
            self._stats_layout,
            id = "Stats"
        )

    # Show statistics
    def set_stats(self, frame_time_ms):
        if self._stats_area == None:
            return
        
        self._stats_area.text = str(frame_time_ms) + "ms"
        