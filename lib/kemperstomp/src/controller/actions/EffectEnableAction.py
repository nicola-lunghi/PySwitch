from .BinaryParameterAction import BinaryParameterAction
from ...model.KemperEffectCategories import KemperEffectCategories
from ...Tools import Tools
from ....config import Config
from ....mappings import KemperMappings
from ....definitions import Colors, ActionDefaults


# Implements the effect enable/disable footswitch action
class EffectEnableAction(BinaryParameterAction):
    
    def __init__(self, appl, switch, config):        
        # Mapping for status (used by BinaryParameterAction)
        config["mapping"] = KemperMappings.MAPPING_EFFECT_SLOT_ON_OFF(config["slot"])
        
        super().__init__(appl, switch, config)

        self._effect_category = KemperEffectCategories.CATEGORY_NONE        
        self._current_category = -1

        # Mapping for effect type
        self._mapping_fxtype = KemperMappings.MAPPING_EFFECT_SLOT_TYPE(self.config["slot"])

        self.color = KemperEffectCategories.CATEGORY_COLORS[self._effect_category]
        self.label.corner_radius = Tools.get_option(self.config["display"], "cornerRadius", ActionDefaults.DEFAULT_EFFECT_SLOT_CORNER_RADIUS)

    # Request effect type periodically (which itself will trigger a status request).
    # Does not call super.update because the status is requested here later anyway.
    def update(self):
        if self._mapping_fxtype.can_receive == False:
            return            
        
        self.print("Request type")
        self.appl.kemper.request(self._mapping_fxtype)

    # Update display and LEDs to the current state and effect category
    def update_displays(self):
        super().update_displays()

        # Only update when category of state have been changed
        if self._current_category == self._effect_category:
            return
        
        self._current_category = self._effect_category

        # Effect category text
        if self.label != None:
            self.label.text = KemperEffectCategories.CATEGORY_NAMES[self._current_category]            
    
    # Update switch brightness
    def set_switch_color(self, color):
        if self._effect_category == KemperEffectCategories.CATEGORY_NONE:
            # Set pixels to black (this effectively deactivates the LEDs) 
            color = Colors.BLACK

        super().set_switch_color(color)
    
    # Update label color, if any
    def set_label_color(self, color):
        if self._effect_category == KemperEffectCategories.CATEGORY_NONE:
            # Do not dim the color when not assigned (this makes it black effectively) 
            self.label.back_color = color
        else:
            super().set_label_color(color)

    # Receive MIDI messages
    def process(self, midi_message):
        super().process(midi_message)
        
        # Receive MIDI messages related to this action, only if a MIDI message has been received
        if midi_message == None:
            return
        
        # Get effect type
        type = self.appl.kemper.parse(self._mapping_fxtype, midi_message)
        if type == None:
            return
        
        # Convert to effect category
        category = KemperEffectCategories.get_effect_category(type)
        self._receive_category(category)

    # Receive a category value (instance of KemperResponse)
    def _receive_category(self, response):
        self.print(" -> Receiving effect category " + repr(response))

        if response == self._effect_category:
            # Request status also when category has not changed
            super().update()
            return

        # New effect category
        self._effect_category = response

        if self._effect_category == KemperEffectCategories.CATEGORY_NONE:
            self.state = False

        self.color = KemperEffectCategories.CATEGORY_COLORS[self._effect_category]
        self.update_displays()

        # Request status, too
        super().update()

