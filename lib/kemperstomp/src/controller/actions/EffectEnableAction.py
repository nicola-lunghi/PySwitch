from .ParameterAction import ParameterAction
from ...client.ClientRequest import ClientRequestListener
from ...misc.Tools import Tools
from ....definitions import Colors, ActionDefaults


# Implements the effect enable/disable footswitch action
class EffectEnableAction(ParameterAction, ClientRequestListener):
    
    # config: see ActionDefinitions
    def __init__(self, appl, switch, config):
        super().__init__(appl, switch, config)

        self.uses_switch_leds = True

        self._debug_slot_names = Tools.get_option(self.appl.config, "showEffectSlotNames", False)

        # Mapping for effect type
        self._mapping_fxtype = self.config["mappingType"] 

        # Category provider of type EffectCategoryProvider
        self._categories = self.config["categories"]
        
        # Slot info provider of type SlotInfoProvider
        self._slot_info = self.config["slotInfo"]
        
        self._effect_category = self._categories.get_category_not_assigned()  
        self._current_category = -1

    # Initialize the action
    def init(self):
        super().init()
        
        if self.label != None:
            self.label.corner_radius = Tools.get_option(self.config["display"], "cornerRadius", ActionDefaults.DEFAULT_EFFECT_SLOT_CORNER_RADIUS)

    # Request effect type periodically (which itself will trigger a status request).
    # Does not call super.update because the status is requested here later anyway.
    def update(self):
        if self._mapping_fxtype.can_receive == False:
            return            
        
        if self.debug == True:
            self.print("Request type")

        self.appl.client.request(self._mapping_fxtype, self)

    # Update display and LEDs to the current state and effect category
    def update_displays(self):
        if not self.enabled:
            super().update_displays()
            return
        
        # Only update when category of state have been changed
        if self._current_category == self._effect_category:
            super().update_displays()
            return
        
        self._current_category = self._effect_category

        # Effect category color
        self.color = self._categories.get_effect_category_color(self._effect_category) 

        # Effect category text
        if self.label != None:
            if self._debug_slot_names:
                self.label.text = self._slot_info.get_name() + ": " + self._categories.get_effect_category_name(self._effect_category) 
            else:
                self.label.text = self._categories.get_effect_category_name(self._effect_category) 
    
        super().update_displays()

    # Update switch brightness
    def set_switch_color(self, color):
        if self._effect_category == self._categories.get_category_not_assigned():
            # Set pixels to black (this effectively deactivates the LEDs) 
            color = Colors.BLACK

        super().set_switch_color(color)
    
    # Update label color, if any
    def set_label_color(self, color):
        if self.label == None:
            return
        
        if self._effect_category == self._categories.get_category_not_assigned():
            # Do not dim the color when not assigned (this makes it black effectively) 
            self.label.back_color = color
        else:
            super().set_label_color(color)

    # Called by the Client class when a parameter request has been answered
    def parameter_changed(self, mapping):
        super().parameter_changed(mapping)

        if not self.enabled:
            return
         
        if mapping != self._mapping_fxtype:
            return
        
        # Convert to effect category
        category = self._categories.get_effect_category(mapping.value)

        if self.debug == True:
            self.print(" -> Receiving effect category " + repr(category))

        if category == self._effect_category:
            # Request status also when category has not changed
            super().update()
            return

        # New effect category
        self._effect_category = category

        if self._effect_category == self._categories.get_category_not_assigned():
            self.state = False

        self.update_displays()

        # Request status, too
        super().update()

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        super().request_terminated(mapping)

        if not self.enabled:
            return
         
        if mapping != self._mapping_fxtype:
            return
        
        if self.debug == True:
            self.print(" -> Terminated request for effect type, is the device offline?")
        
        self._effect_category = self._categories.get_category_not_assigned() 
        
        self.update_displays()

    # Reset the action
    def reset(self):
        super().reset()

        self._effect_category = self._categories.get_category_not_assigned() 
        self.update_displays()

    # Must reset all action states so the instance is being updated
    def force_update(self):
        super().force_update()
        
        self._current_category = -1


#######################################################################################################


# Category provider base class. A category provider must translate the value of 
# the effect type mapping set on the action's config to an effect category including
# the corresponding color and name.
class EffectCategoryProvider:
    # Must return the effect category for a mapping value
    def get_effect_category(self, value):
        raise Exception("Implement in child classes")
    
    # Must return the effect color for a mapping value
    def get_effect_category_color(self, value):
        return Colors.BLACK
    
    # Must return the effect name for a mapping value
    def get_effect_category_name(self, value):
        return ""
    
    # Must return the value interpreted as "not assigned"
    def get_category_not_assigned(self):
        raise Exception("Implement in child classes")
    

#######################################################################################################
 
 
# Provider class for slot information
class SlotInfoProvider:
    # Must return the lot name
    def get_name(self):
        raise Exception("Implement in child classes")