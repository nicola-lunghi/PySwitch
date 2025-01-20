from micropython import const
from ....controller.actions import PushButtonAction
from ....controller.callbacks import EffectEnableCallback
from ...kemper import KemperMappings
from ....misc import Colors, DEFAULT_LABEL_COLOR

# Switch an effect slot on / off
def EFFECT_STATE(slot_id, 
                 display = None, 
                 mode = PushButtonAction.HOLD_MOMENTARY, 
                 id = False, 
                 use_leds = True, 
                 enable_callback = None
    ):
    return PushButtonAction({
        "callback": KemperEffectEnableCallback(slot_id),
        "mode": mode,
        "display": display,
        "id": id,
        "useSwitchLeds": use_leds,
        "enableCallback": enable_callback,
    })


# Used for effect enable/disable ParameterAction
class KemperEffectEnableCallback(EffectEnableCallback):

    # Effect types enum (used internally, also for indexing colors, so be sure these are always a row from 0 to n)
    CATEGORY_WAH = const(1)
    CATEGORY_DISTORTION = const(2)
    CATEGORY_COMPRESSOR = const(3)
    CATEGORY_NOISE_GATE = const(4)
    CATEGORY_SPACE = const(5)
    CATEGORY_CHORUS = const(6)
    CATEGORY_PHASER_FLANGER = const(7)
    CATEGORY_EQUALIZER = const(8)
    CATEGORY_BOOSTER = const(9)
    CATEGORY_LOOPER = const(10)
    CATEGORY_PITCH = const(11)
    CATEGORY_DUAL = const(12)
    CATEGORY_DELAY = const(13)
    CATEGORY_REVERB = const(14)

    # Effect colors. The order must match the enums for the effect types defined above!
    CATEGORY_COLORS = (
        DEFAULT_LABEL_COLOR,                            # None
        Colors.ORANGE,                                  # Wah
        Colors.RED,                                     # Distortion
        Colors.BLUE,                                    # Comp
        Colors.BLUE,                                    # Gate
        Colors.GREEN,                                   # Space
        Colors.BLUE,                                    # Chorus
        Colors.PURPLE,                                  # Phaser/Flanger
        Colors.YELLOW,                                  # EQ
        Colors.RED,                                     # Booster
        Colors.PURPLE,                                  # Looper
        Colors.WHITE,                                   # Pitch
        Colors.GREEN,                                   # Dual
        Colors.GREEN,                                   # Delay
        Colors.GREEN,                                   # Reverb
    )

    # Effect type display names. The order must match the enums for the effect types defined above!
    CATEGORY_NAMES = (
        "-",
        "Wah",
        "Dist",
        "Comp",
        "Gate",
        "Space",
        "Chorus",
        "Phaser",
        "EQ",
        "Boost",
        "Looper",
        "Pitch",
        "Dual",
        "Delay",
        "Reverb"
    )

    def __init__(self, slot_id):
        super().__init__(
            mapping_state = KemperMappings.EFFECT_STATE(slot_id),
            mapping_type = KemperMappings.EFFECT_TYPE(slot_id)
        )
    
    # Must return the effect category for a mapping value
    def get_effect_category(self, kpp_effect_type):
        # NOTE: The ranges are defined by Kemper with a lot of unused numbers, so the borders between types
        # could need to be adjusted with future Kemper firmware updates!
        if (kpp_effect_type == 0):
            return self.CATEGORY_NONE
        elif (0 < kpp_effect_type and kpp_effect_type <= 10) or kpp_effect_type == 12:
            return self.CATEGORY_WAH
        elif kpp_effect_type == 11 or kpp_effect_type == 13:
            return self.CATEGORY_PITCH
        elif (14 < kpp_effect_type and kpp_effect_type <= 45):
            return self.CATEGORY_DISTORTION
        elif (45 < kpp_effect_type and kpp_effect_type <= 55):
            return self.CATEGORY_COMPRESSOR
        elif (55 < kpp_effect_type and kpp_effect_type <= 60):
            return self.CATEGORY_NOISE_GATE       
        elif (60 < kpp_effect_type and kpp_effect_type <= 64):
            return self.CATEGORY_SPACE            
        elif (64 < kpp_effect_type and kpp_effect_type <= 80):
            return self.CATEGORY_CHORUS
        elif (80 < kpp_effect_type and kpp_effect_type <= 95):
            return self.CATEGORY_PHASER_FLANGER
        elif (95 < kpp_effect_type and kpp_effect_type <= 110):
            return self.CATEGORY_EQUALIZER
        elif (110 < kpp_effect_type and kpp_effect_type <= 120):
            return self.CATEGORY_BOOSTER
        elif (120 < kpp_effect_type and kpp_effect_type <= 125):
            return self.CATEGORY_LOOPER
        elif (125 < kpp_effect_type and kpp_effect_type <= 135):
            return self.CATEGORY_PITCH
        elif (135 < kpp_effect_type and kpp_effect_type <= 143):
            return self.CATEGORY_DUAL
        elif (143 < kpp_effect_type and kpp_effect_type <= 170):
            return self.CATEGORY_DELAY
        else:
            return self.CATEGORY_REVERB
        
    # Must return the color for a category    
    def get_effect_category_color(self, category):
        return self.CATEGORY_COLORS[category]

    # Must return the text to show for a category    
    def get_effect_category_text(self, category):
        return self.CATEGORY_NAMES[category]