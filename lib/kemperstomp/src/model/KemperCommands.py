from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive

from .KemperResponse import KemperResponse
from ..Tools import Tools
from ...definitions import KemperDefinitions, Slots


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

    # Debug console output
    def _print(self, msg):
        Tools.print("KPP: " + msg)