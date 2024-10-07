
# Kemper Effect slot IDs, MIDI addresses and display properties
class KemperEffectSlot:
    
    # IDs for the available effect slots
    EFFECT_SLOT_ID_A = 0
    EFFECT_SLOT_ID_B = 1
    EFFECT_SLOT_ID_C = 2
    EFFECT_SLOT_ID_D = 3
    
    EFFECT_SLOT_ID_X = 4
    EFFECT_SLOT_ID_MOD = 5
    EFFECT_SLOT_ID_DLY = 6
    EFFECT_SLOT_ID_REV = 7

    # CC Address for Effect Slot enable/disable. Order has to match the one defined above!
    CC_EFFECT_SLOT_ENABLE = (
        17,    # Slot A
        18,    # Slot B
        19,    # Slot C
        20,    # Slot D

        22,    # Slot X
        24,    # Slot MOD        
        27,    # Slot DLY (with Spillover)        
        29     # Slot REV (with Spillover)
    )

    # Slot address pages. Order has to match the one defined above!
    NRPN_SLOT_ADDRESS_PAGE = (
        0x32,   # Slot A
        0x33,   # Slot B
        0x34,   # Slot C
        0x35,   # Slot D

        0x38,   # Slot X
        0x3a,   # Slot MOD
        0x3c,   # Slot DLY
        0x3d    # Slot REV
    )    

    # Freeze parameter addresses on page 0x7d (Looper and Delay Freeze) for all slots. 
    # Order has to match the one defined above!
    NRPN_FREEZE_SLOT_PARAMETER_ADDRESSES = [
        0x6b,   # Slot A
        0x6c,   # Slot B
        0x6d,   # Slot C
        0x6e,   # Slot D

        0x6f,   # Slot X
        0x71,   # Slot MOD
        0x72,   # Slot DLY
        0x73    # Slot REV
    ]    

     # Slot names for display. Order has to match the one defined above!
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
        return KemperEffectSlot.EFFECT_SLOT_NAMES[self._slot_id]