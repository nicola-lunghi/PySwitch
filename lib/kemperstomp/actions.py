#################################################################################################################################
# 
# Defines some useful action predefinitions. If you need more options on one of them, just
# use them as template to create your own (directly in config.py)
#
#################################################################################################################################

from .definitions import ActionTypes, KemperMidi, Colors, PushButtonModes
from .mappings import KemperMappings

# All defined actions here have one parameter in common: A display definition (see definitions.py)
class Actions: 

    @staticmethod
    def EFFECT_ON_OFF(slot_id, display, mode = PushButtonModes.HOLD_MOMENTARY):
        return {
            "type": ActionTypes.EFFECT_ON_OFF,
            "slot": slot_id,
            "mode": mode,
            "display": display
        }

    # Volume boost function, based on setting rig volume to a certain boost value. To 
    # make sense, all rig volumes have to be zero in your rigs! You can then set the
    # boost rig volume by passing a value in range [0..1] (corresponding to the range of the
    # rig volume paramneter: 0.5 is 0dB, 0.75 is +6dB, 1.0 is +12dB)
    @staticmethod
    def RIG_VOLUME_BOOST(boost_volume, display):
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": KemperMappings.RIG_VOLUME,
            "valueEnabled": KemperMidi.NRPN_VALUE(boost_volume),
            "valueDisabled": KemperMidi.NRPN_VALUE(0.5),           # 0dB
            "display": display,
            "color": Colors.PINK,
            "text": "RigBoost"        # TODO not working yet
        }

    @staticmethod
    def BANK_UP(display):
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": KemperMappings.NEXT_BANK,
            "mode": PushButtonModes.ENABLE,
            "valueEnabled": KemperMidi.CC_VALUE_BANK_CHANGE,
            "display": display,
            "color": Colors.WHITE,
            "text": "Bank up"        # TODO not working yet
        }
    
    @staticmethod
    def BANK_DOWN(display):
        return {
            "type": ActionTypes.PARAMETER,
            "mapping": KemperMappings.PREVIOUS_BANK,
            "mode": PushButtonModes.ENABLE,
            "valueEnabled": KemperMidi.CC_VALUE_BANK_CHANGE,
            "display": display,
            "color": Colors.WHITE,
            "text": "Bank down"        # TODO not working yet
        }