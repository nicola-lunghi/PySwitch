from .BinaryParameterAction import BinaryParameterAction
from ...model.KemperEffectCategories import KemperEffectCategories
from ...model.KemperRequest import KemperRequestListener
from ...Tools import Tools
from ....mappings import KemperMappings
from ....definitions import Colors, ActionDefaults


# Implements the effect enable/disable footswitch action
class EffectEnableAction(BinaryParameterAction, KemperRequestListener):
    
    def __init__(self, appl, switch, config, index):        
        # Mapping for status (used by BinaryParameterAction)
        config["mapping"] = KemperMappings.EFFECT_SLOT_ON_OFF(config["slot"])
        
        super().__init__(appl, switch, config, index)

        self._effect_category = KemperEffectCategories.CATEGORY_NONE        
        self._current_category = -1

        # Mapping for effect type
        self._mapping_fxtype = KemperMappings.EFFECT_SLOT_TYPE(self.config["slot"])

        if self.label != None:
            self.label.corner_radius = Tools.get_option(self.config["display"], "cornerRadius", ActionDefaults.DEFAULT_EFFECT_SLOT_CORNER_RADIUS)

    # Request effect type periodically (which itself will trigger a status request).
    # Does not call super.update because the status is requested here later anyway.
    def update(self):
        if self._mapping_fxtype.can_receive == False:
            return            
        
        if self.debug == True:
            self.print("Request type")

        self.appl.kemper.request(self._mapping_fxtype, self)

    # Update display and LEDs to the current state and effect category
    def update_displays(self):
        # Only update when category of state have been changed
        if self._current_category == self._effect_category:
            super().update_displays()
            return
        
        self._current_category = self._effect_category

        # Effect category color
        self.color = KemperEffectCategories.CATEGORY_COLORS[self._effect_category]

        # Effect category text
        if self.label != None:
            self.label.text = KemperEffectCategories.CATEGORY_NAMES[self._current_category]            
    
        super().update_displays()

    # Update switch brightness
    def set_switch_color(self, color):
        if self._effect_category == KemperEffectCategories.CATEGORY_NONE:
            # Set pixels to black (this effectively deactivates the LEDs) 
            color = Colors.BLACK

        super().set_switch_color(color)
    
    # Update label color, if any
    def set_label_color(self, color):
        if self.label == None:
            return
        
        if self._effect_category == KemperEffectCategories.CATEGORY_NONE:
            # Do not dim the color when not assigned (this makes it black effectively) 
            self.label.back_color = color
        else:
            super().set_label_color(color)

    # Called by the Kemper class when a parameter request has been answered
    def parameter_changed(self, mapping):
        super().parameter_changed(mapping)
        
        if mapping != self._mapping_fxtype:
            return
        
        # Convert to effect category
        category = KemperEffectCategories.get_effect_category(mapping.value)

        if self.debug == True:
            self.print(" -> Receiving effect category " + repr(category))

        if category == self._effect_category:
            # Request status also when category has not changed
            super().update()
            return

        # New effect category
        self._effect_category = category

        if self._effect_category == KemperEffectCategories.CATEGORY_NONE:
            self.state = False

        self.update_displays()

        # Request status, too
        super().update()

    # Called when the Kemper is offline (requests took too long)
    def request_terminated(self, mapping):
        super().request_terminated(mapping)

        if mapping != self._mapping_fxtype:
            return
        
        if self.debug == True:
            self.print(" -> Terminated request for effect type, is the device offline?")
        
        self._effect_category = KemperEffectCategories.CATEGORY_NONE
        
        self.update_displays()

