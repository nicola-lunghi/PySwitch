#################################################################################################################################
# 
# Ports configuration for kemperstomp. This helps addressing the different devices. Only change this when either
# one of the supported devices has been updated or new devices are added.
#
#################################################################################################################################
 
import board

#################################################################################################################################

# This defines ports and pixel assignments for the foot switches
class Ports:
    # PaintAudio MIDI Captain Nano (4 Switches)
    # Board Infos
    # Raspberry Pi Pico (RP2040)
    #
    # GP0
    # GP1  - FootSwitch 1
    # GP2
    # GP3
    # GP4  bat_chg_led
    # GP5
    # GP6  charging
    # GP7  NeoPixel
    # GP8  asyncio PWMOut frequency
    # GP9  - FootSwitch 3
    # GP10 - FootSwitch 4
    # GP11 
    # GP12 tft_dc   (SPI1 RX)
    # GP13 tft_cs   (Chip Select)
    # GP14 spi_clk  (SPI1SCK)
    # GP15 spi_mosi (SPI1 TX)
    # GP16 Midi GP16GP17 baudrate
    # GP17 Midi GP16GP17 baudrate
    # GP18
    # GP19
    # GP20
    # GP21
    # GP22
    # GP23
    # GP24 
    # GP25 - FootSwitch 2
    # GP26
    # GP27
    # GP28
    PA_MIDICAPTAIN_NANO_SWITCH_1 = { "port": board.GP1,  "pixels": (0, 1, 2) }
    PA_MIDICAPTAIN_NANO_SWITCH_2 = { "port": board.GP25, "pixels": (3, 4, 5) }
    PA_MIDICAPTAIN_NANO_SWITCH_3 = { "port": board.GP9,  "pixels": (6, 7, 8) }
    PA_MIDICAPTAIN_NANO_SWITCH_4 = { "port": board.GP10, "pixels": (9, 10, 11) }

    # PaintAudio MIDI Captain Mini (6 Switches)
    # Board Infos
    # Raspberry Pi Pico (RP2040)
    #
    # GP0
    # GP1  - FootSwitch 1
    # GP2
    # GP3
    # GP4  bat_chg_led
    # GP5
    # GP6  charging
    # GP7  NeoPixel
    # GP8  asyncio PWMOut frequency
    # GP9  - FootSwitch 4
    # GP10 - FootSwitch 5
    # GP11 - FootSwitch 6
    # GP12 tft_dc   (SPI1 RX)
    # GP13 tft_cs   (Chip Select)
    # GP14 spi_clk  (SPI1SCK)
    # GP15 spi_mosi (SPI1 TX)
    # GP16 Midi GP16GP17 baudrate
    # GP17 Midi GP16GP17 baudrate
    # GP18
    # GP19
    # GP20
    # GP21
    # GP22
    # GP23
    # GP24 - FootSwitch 3
    # GP25 - FootSwitch 2
    # GP26
    # GP27
    # GP28
    PA_MIDICAPTAIN_MINI_SWITCH_1 = { "port": board.GP1,  "pixels": (0, 1, 2) }
    PA_MIDICAPTAIN_MINI_SWITCH_2 = { "port": board.GP25, "pixels": (3, 4, 5) }
    PA_MIDICAPTAIN_MINI_SWITCH_3 = { "port": board.GP24, "pixels": (6, 7, 8) }
    PA_MIDICAPTAIN_MINI_SWITCH_4 = { "port": board.GP9,  "pixels": (9, 10, 11) }
    PA_MIDICAPTAIN_MINI_SWITCH_5 = { "port": board.GP10, "pixels": (12, 13, 14) }
    PA_MIDICAPTAIN_MINI_SWITCH_6 = { "port": board.GP11, "pixels": (15, 16, 17) }

#################################################################################################################################

# Color definitions
class Colors:
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    RED = (255, 0, 0)
    PURPLE = (30, 0, 20)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 100, 0)
    TURQUOISE = (64, 242, 208)
    BLUE = (0, 0, 255)
    GRAY = (190, 190, 190)
    DARK_GRAY = (50, 50, 50)
    BLACK = (0, 0, 0)

    # UI Colors
    TEXT_COLOR_BRIGHT = (255, 255, 0)             # Bright text color
    TEXT_COLOR_DARK = (0, 0, 0)                   # Dark text color

    DEFAULT_SLOT_COLOR = (50, 50, 50)             # Default backfround color for effect slots (until an effect type is set)

    INFO_AREA_TEXT_COLOR = (215, 255, 255)        # Text color for the info area (rig name).
    INFO_AREA_BACK_COLOR = (20, 50, 30)           # Background color for the info area (rig name).
    
    DEBUG_BACK_COLOR = (20, 20, 70)               # Debug area: Background color (if debug is enabled in Config)
    DEBUG_TEXT_COLOR = (255, 255, 0)              # Debug area: Text color (if debug is enabled in Config)

#################################################################################################################################

# Kemper specific definitions
class KemperDefinitions:
    # Effect type color assignment
    EFFECT_COLOR_NONE = Colors.DEFAULT_SLOT_COLOR
    EFFECT_COLOR_WAH = Colors.ORANGE
    EFFECT_COLOR_DISTORTION = Colors.RED,
    EFFECT_COLOR_COMPRESSOR = Colors.BLUE,
    EFFECT_COLOR_NOISE_GATE = Colors.BLUE,
    EFFECT_COLOR_SPACE = Colors.GREEN,
    EFFECT_COLOR_CHORUS = Colors.BLUE,
    EFFECT_COLOR_PHASER_FLANGER = Colors.PURPLE,
    EFFECT_COLOR_EQUALIZER = Colors.YELLOW,
    EFFECT_COLOR_BOOSTER = Colors.RED,
    EFFECT_COLOR_LOOPER = Colors.PURPLE,
    EFFECT_COLOR_PITCH = Colors.WHITE,
    EFFECT_COLOR_DUAL = Colors.GREEN,
    EFFECT_COLOR_DELAY = Colors.GREEN,
    EFFECT_COLOR_REVERB = Colors.GREEN

    # Effect type display names
    EFFECT_NAME_NONE = "-"
    EFFECT_NAME_WAH = "Wah Wah"
    EFFECT_NAME_DISTORTION = "Distortion"
    EFFECT_NAME_COMPRESSOR = "Compressor"
    EFFECT_NAME_NOISE_GATE = "Noise Gate"
    EFFECT_NAME_SPACE = "Space"
    EFFECT_NAME_CHORUS = "Chorus"
    EFFECT_NAME_PHASER_FLANGER = "Phaser"
    EFFECT_NAME_EQUALIZER = "Equalizer"
    EFFECT_NAME_BOOSTER = "Booster"
    EFFECT_NAME_LOOPER = "Looper"
    EFFECT_NAME_PITCH = "Transpose"
    EFFECT_NAME_DUAL = "Dual"
    EFFECT_NAME_DELAY = "Delay"
    EFFECT_NAME_REVERB = "Reverb"

    # Some internal addressing (acc. to Kemper MIDI specification, should not be needed to change)
    PARAMETER_ADDRESS_EFFECT_TYPE = 0x00   
    PARAMETER_ADDRESS_EFFECT_STATUS = 0x03

    RESPONSE_ID_GLOBAL_PARAMETER = -1
    RESPONSE_ID_EFFECT_TYPE = 0x00
    RESPONSE_ID_EFFECT_STATUS = 0x03

    RESPONSE_ANSWER_STATUS_ON = 0x01
    RESPONSE_ANSWER_STATUS_OFF = 0x00

    RESPONSE_PREFIX_RIG_NAME = [0x00, 0x00, 0x03, 0x00, 0x00, 0x01]
    RESPONSE_PREFIX_RIG_DATE = [0x00, 0x00, 0x03, 0x00, 0x00, 0x03]

#################################################################################################################################

# IDs for the available effect slots
class Slots:
    EFFECT_SLOT_ID_A = 0
    EFFECT_SLOT_ID_B = 1
    EFFECT_SLOT_ID_DLY = 2
    EFFECT_SLOT_ID_REV = 3

    # Slot enable/disable. Order has to match the one defined above!
    CC_EFFECT_SLOT_ENABLE = (
        17,    # Slot A
        18,    # Slot B
        27,    # Slot DLY (with Spillover)
        28     # Slot REV (with Spillover)
    )
    
    # Slot address pages. Order has to match the one defined above!
    SLOT_ADDRESS_PAGE = (
        0x32,   # Slot A
        0x33,   # Slot B
        0x3c,   # Slot DLY
        0x3d    # Slot REV
    )

#################################################################################################################################

# This defines the available actions. 
class Actions:

    # Switches an effect on/off, if the slot is assigned.
    # Available options:
    # {
    #     "type": Actions.EFFECT_ON_OFF
    #     "slot": SLot ID: Use one of the constants defined in Slots, for example Slots.EFFECT_SLOT_A
    # }
    EFFECT_ON_OFF = 0
