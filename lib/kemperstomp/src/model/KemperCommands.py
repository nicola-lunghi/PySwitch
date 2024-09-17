from adafruit_midi.control_change import ControlChange

from ..Tools import Tools
from ...definitions import Slots, KemperDefinitions
from ...config import Config


# Implements all commands to the kemper (except parameter requests)
class KemperCommands:

    # Requires an USB driver instance
    def __init__(self, midi_usb):
        self._midi_usb = midi_usb

    # Sets a slot enabled or disabled
    def set_slot_enabled(self, slot_id, enable):
        self._print("Set effect slot status to " + repr(enable))

        enable_int = 0
        if enable == True:
            enable_int = 1

        self._midi_usb.send(ControlChange(Slots.CC_EFFECT_SLOT_ENABLE[slot_id], enable_int))

    # Set tuner mode
    def set_tuner_mode(self, enable):
        self._print("Set tuner mode to " + repr(enable))

        enable_int = 0
        if enable == True:
            enable_int = 127
            
        self._midi_usb.send(ControlChange(KemperDefinitions.CC_TUNER_MODE, enable_int))

    # Debug console output
    def _print(self, msg):
        if Tools.get_option(Config, "debugKemper") != True:
            return
        
        Tools.print("KPP: " + msg)