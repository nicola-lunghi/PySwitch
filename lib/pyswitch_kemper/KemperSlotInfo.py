#################################################################################################################################
# 
# Global kemper configuration for the KemperStomp script: definitions of kemper MIDI addresses, effect categories and a defaulted
# SysEx message class to be used in mappings for convenience. The MIDI message composition/parsing is also implemented here.
#
#################################################################################################################################

from pyswitch.core.controller.actions.EffectEnableAction import SlotInfoProvider

#################################################################################################################################


# Provides slot names for display
class KemperSlotInfo(SlotInfoProvider):

    # Slot names for display. Order has to match the one defined above in KemperMidi!
    EFFECT_SLOT_NAMES = [
        "A",
        "B",
        "C",
        "D",

        "X",
        "MOD",
        "DLY",
        "REV"
    ]

    def __init__(self, slot_id):
        self._slot_id = slot_id

    # Must return the lot name
    def get_name(self):
        return KemperSlotInfo.EFFECT_SLOT_NAMES[self._slot_id]


