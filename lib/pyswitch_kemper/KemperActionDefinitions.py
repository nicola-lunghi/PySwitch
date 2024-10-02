#################################################################################################################################
# 
# Defines some important actions. All methods return an action definition for the switches in config.py.
# You can use them for common tasks, but also define your action(s) by hand if you need more flexibility.
#
#################################################################################################################################

from pyswitch.definitions import ActionTypes, Colors
from pyswitch.defaults import FootSwitchDefaults, DisplayDefaults
from pyswitch.core.controller.actions.base.PushButtonAction import PushButtonModes

from pyswitch.core.client.ClientParameterMapping import ClientParameterMapping

from .KemperMappings import KemperMappings
from .KemperEffectCategories import KemperEffectCategories
from .KemperSlot import KemperSlot

from .Kemper import Kemper

#################################################################################################################################

CC_VALUE_BANK_CHANGE = 0

#################################################################################################################################

# All defined actions here have one parameter in common: A display definition (see definitions.py)
# which assigns a display label to the action (optional: If omitted, no visual feedback is given 
# on the display).
class KemperActionDefinitions: 

    ## Effect slots ########################################################################################################

    # Switch an effect slot on / off
    @staticmethod
    def EFFECT_ON_OFF(slot_id, display = None, mode = PushButtonModes.HOLD_MOMENTARY, id = False):
        return {
            "type": ActionTypes.EFFECT_ON_OFF,
            "mapping": KemperMappings.EFFECT_SLOT_ON_OFF(slot_id),
            "mappingType": KemperMappings.EFFECT_SLOT_TYPE(slot_id),
            "categories": KemperEffectCategories(),
            "slotInfo": KemperSlot(slot_id),
            "mode": mode,
            "display": display,
            "id": id
        }

    # Rotary speed (fast/slow)
    @staticmethod
    def ROTARY_SPEED(slot_id, display = None, color = Colors.DARK_BLUE, id = False):
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": KemperMappings.ROTARY_SPEED(slot_id),
            "display": display,
            "text": "Fast",
            "color": color,
            "id": id
        }

    ## Special functions ####################################################################################################

    # Switch tuner mode on / off
    @staticmethod
    def TUNER_MODE(display = None, color = Colors.DEFAULT_SWITCH_COLOR, id = False):
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": KemperMappings.TUNER_MODE_ON_OFF,
            "display": display,
            "text": "Tuner",
            "color": Colors.WHITE,
            "color": color,
            "id": id
        }

    # Tap tempo
    @staticmethod
    def TAP_TEMPO(display = None, color = Colors.DARK_GREEN, id = False):
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": KemperMappings.TAP_TEMPO,
            "display": display,
            "text": "Tap",
            "color": color,
            "mode": PushButtonModes.MOMENTARY,
            "id": id
        }

    ## Rig specific ##########################################################################################################

    # Volume boost function, based on setting rig volume to a certain boost value. To 
    # make sense, all rig volumes have to be zero in your rigs! You can then set the
    # boost rig volume by passing a value in range [0..1] (corresponding to the range of the
    # rig volume paramneter: 0.5 is 0dB, 0.75 is +6dB, 1.0 is +12dB)
    @staticmethod
    def RIG_VOLUME_BOOST(boost_volume, display = None, mode = PushButtonModes.HOLD_MOMENTARY, color = Colors.PINK, id = False):
        return {
            "type": ActionTypes.PARAMETER,
            "mode": mode,
            "mapping": KemperMappings.RIG_VOLUME,
            "valueEnabled": Kemper.NRPN_VALUE(boost_volume),
            "valueDisabled": Kemper.NRPN_VALUE(0.5),           # 0dB
            "display": display,
            "text": "RigBoost",
            "color": color,
            "id": id
        }

    # Used to reset the screen areas which show rig info details directly after rig changes (if you dont use this, 
    # you get no visual feedback on the device that a new rig is coming up)
    @staticmethod
    def RESET_RIG_INFO_DISPLAYS(id = False):
        return {
            "type": ActionTypes.RESET_DISPLAYS_FOR_MAPPINGS,
            "resetSwitches": True,
            "ignoreOwnSwitch": True,
            "resetDisplayAreas": True,
            "id": id
        }

    ## Amp ########################################################################################################################

    # Amp on/off
    @staticmethod
    def AMP_ON_OFF(display = None, mode = PushButtonModes.HOLD_MOMENTARY, color = Colors.DEFAULT_SWITCH_COLOR, id = False):
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": KemperMappings.AMP_ON_OFF,
            "mode": mode,
            "display": display,
            "text": "Amp",
            "color": color,
            "id": id
        }

    ## Cab ########################################################################################################################

    # Amp on/off
    @staticmethod
    def CABINET_ON_OFF(display = None, mode = PushButtonModes.HOLD_MOMENTARY, color = Colors.DEFAULT_SWITCH_COLOR, id = False):
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": KemperMappings.CABINET_ON_OFF,
            "mode": mode,
            "display": display,
            "text": "Cab",
            "color": color,
            "id": id
        }

    ## Change Rig/Bank ############################################################################################################

    # Next bank (keeps rig index)
    @staticmethod
    def BANK_UP(display = None, color = Colors.WHITE, id = False):
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": KemperMappings.NEXT_BANK,
            "mode": PushButtonModes.ONE_SHOT,
            "valueEnabled": CC_VALUE_BANK_CHANGE,
            "display": display,
            "text": "Bank up",
            "color": color,
            "id": id
        }
    
    # Previous bank (keeps rig index)
    @staticmethod
    def BANK_DOWN(display = None, color = Colors.WHITE, id = False):
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": KemperMappings.PREVIOUS_BANK,
            "mode": PushButtonModes.ONE_SHOT,
            "valueEnabled": CC_VALUE_BANK_CHANGE,
            "display": display,
            "text": "Bank dn",
            "color": color,
            "id": id
        }
    
    # Selects a specific rig, or toggles between two rigs (if rig_off is also provided) in
    # the current bank. Rigs are indexed starting from one, range: [1..5].
    # Optionally, banks can be switched too in the same logic using bank and bank_off.
    @staticmethod
    def RIG_SELECT(rig, rig_off = None, bank = None, bank_off = None, display = None, color = Colors.YELLOW, id = False):
        # Texts always show the rig to be selected when the switch is pushed the next time
        text_rig_off = str(rig)
        text_rig_on = text_rig_off

        # Mappings and values: Start with a configuration for rig_off == None and bank(_off) = None.
        mapping = [
            ClientParameterMapping(),           # Dummy to be replaced by bank select if specified
            KemperMappings.RIG_SELECT(rig - 1)
        ]
        mapping_disable = [
            ClientParameterMapping(),           # Dummy to be replaced by bank select if specified
            KemperMappings.RIG_SELECT(rig - 1)
        ]
        value_enabled = [
            0,                                  # Dummy to be replaced by bank select if specified
            Kemper.NRPN_PARAMETER_ON
        ]
        value_disabled = [
            0,                                  # Dummy to be replaced by bank select if specified
            Kemper.NRPN_PARAMETER_ON
        ]

        # Bank for main rig
        if bank != None:
            mapping[0] = KemperMappings.BANK_PRESELECT
            if rig_off == None:
                mapping_disable[0] = KemperMappings.BANK_PRESELECT
            
            value_enabled[0] = bank - 1
            value_disabled[0] = bank - 1
            
            text_rig_off = str(bank) + "-" + text_rig_off
            if rig_off == None:
                text_rig_on = text_rig_off

        # Alternate rig (the rig selected when the switch state is False)
        if rig_off != None:
            # Use a different mapping for disabling
            mapping_disable[1] = KemperMappings.RIG_SELECT(rig_off - 1)
            text_rig_on = str(rig_off)

        # Bank for alternate rig
        if bank_off != None:
            if rig_off == None:
                raise Exception("RIG_SELECT: If bank_off is set, you must also provide rig_off.")
            
            mapping_disable[0] = KemperMappings.BANK_PRESELECT
            value_disabled[0] = bank_off - 1
            
            text_rig_on = str(bank_off) + "-" + text_rig_on

        # Finally we can create the action definition ;)
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": mapping,
            "mappingDisable": mapping_disable,
            "valueEnabled": value_enabled,
            "valueDisabled": value_disabled,
            "display": display,
            "text": "Rig " + text_rig_on,
            "textDisabled": "Rig " + text_rig_off,
            "color": color,
            "ledBrightness": {
                "on": FootSwitchDefaults.DEFAULT_BRIGHTNESS_OFF,                  # Set equal brightness (we do not need status display here)
                "off": FootSwitchDefaults.DEFAULT_BRIGHTNESS_OFF
            },
            "displayDimFactorOn": DisplayDefaults.DEFAULT_SLOT_DIM_FACTOR_OFF,  # Set equal brightness (we do not need status display here)
            "mode": PushButtonModes.LATCH,
            "id": id
        }
    
