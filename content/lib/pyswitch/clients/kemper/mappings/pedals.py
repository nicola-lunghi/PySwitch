from micropython import const
from .. import KemperParameterMapping

from adafruit_midi.control_change import ControlChange


# NOTE: Morph pedal is implemented in morph.py
_CC_WAH_PEDAL = const(1)
_CC_PITCH_PEDAL = const(4)
_CC_VOLUME_PEDAL = const(7)
_CC_DELAY_MIX = const(68)
_CC_DELAY_FEEDBACK = const(69)
_CC_REVERB_MIX = const(70)
_CC_REVERB_TIME = const(71)
_CC_OUTPUT_VOLUME = const(73)


def MAPPING_WAH_PEDAL(): 
    return KemperParameterMapping(
        name = "Wah",
        set = ControlChange(
            _CC_WAH_PEDAL, 
            0
        )
    )

def MAPPING_VOLUME_PEDAL(): 
    return KemperParameterMapping(
        name = "Vol",
        set = ControlChange(
            _CC_VOLUME_PEDAL, 
            0
        )
    )

def MAPPING_PITCH_PEDAL(): 
    return KemperParameterMapping(
        name = "Pitch",
        set = ControlChange(
            _CC_PITCH_PEDAL, 
            0
        )
    )

def MAPPING_DELAY_MIX_PEDAL(): 
    return KemperParameterMapping(
        name = "DlyMix",
        set = ControlChange(
            _CC_DELAY_MIX, 
            0
        )
    )

def MAPPING_DELAY_FEEDBACK_PEDAL(): 
    return KemperParameterMapping(
        name = "DlyFB",
        set = ControlChange(
            _CC_DELAY_FEEDBACK, 
            0
        )
    )

def MAPPING_REVERB_MIX_PEDAL(): 
    return KemperParameterMapping(
        name = "RevMix",
        set = ControlChange(
            _CC_REVERB_MIX, 
            0
        )
    )

def MAPPING_REVERB_TIME_PEDAL(): 
    return KemperParameterMapping(
        name = "RevTime",
        set = ControlChange(
            _CC_REVERB_TIME, 
            0
        )
    )

def MAPPING_VOLUME_OUTPUT_PEDAL(): 
    return KemperParameterMapping(
        name = "OutVol",
        set = ControlChange(
            _CC_OUTPUT_VOLUME, 
            0
        )
    )
