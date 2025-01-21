from micropython import const
from .. import KemperParameterMapping, KemperNRPNExtendedMessage

from adafruit_midi.control_change import ControlChange

_CC_TAP_TEMPO = const(30)

# Switch tuner mode on/off (no receive possible!)
def MAPPING_TAP_TEMPO(): 
    return KemperParameterMapping(
        name = "Tap Tempo",
        set = ControlChange(
            _CC_TAP_TEMPO, 
            0    # Dummy value, will be overridden
        )
    )

def MAPPING_TEMPO_DISPLAY():
    return KemperParameterMapping(
        name = "Tempo",
        response = KemperNRPNExtendedMessage(
            0x01,
            [
                0x7c,
                0x00,
                0x00
            ]
        )
    )

# MIDI Clock message, sent 24x every beat
#MAPPING_MIDI_CLOCK = KemperParameterMapping(
#    name = "Clock",
#    response = MidiClockMessage()
#)

#MAPPING_MIDI_CLOCK_START = KemperParameterMapping(
#    name = "Start",
#    response = Start()
#)