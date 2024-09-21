#################################################################################################################################
# 
# Ports configuration for kemperstomp. This helps addressing the different devices. Only change this when either
# one of the supported devices has been updated or new devices are added.
#
#################################################################################################################################
 
import board

#################################################################################################################################


# This defines the available actions. All actions have the following common options.
#
# If the display attribute is defined, this defines properties for a display label connected 
# to the action. Optional: if omitted, no display label will be assigned.
#
# {
#      "type": Type of the action. This determines what the action does, and which configuration options it needs.
#              Use the constants defined in Actions, for example Actions.EFFECT_ON_OFF.
# 
#      "display": {
#          "area":         ID of the display area. See display.py.
#          "index":        Position inside the display area. If omitted, always the first place is used which takes up the whole area space.
#                          Keep all indices of one area sequentially starting from 0 (not 1!), or you will get empty areas!
#          "text":         Text to show on the display label initially.
#          "cornerRadius": Optional corner radius. Default is the underlying layout.
#      }
# }
class Actions:

    # Switches an effect on/off, if the slot is assigned.
    # Additional options:
    # {
    #     "mode":           Mode of operation (see PushButtonModes). Optional, default is PushButtonModes.HOLD_MOMENTARY,
    #     "holdTimeMillis": Optional hold time in milliseconds. Default is PushButtonModes.DEFAULT_LATCH_MOMENTARY_HOLD_TIME
    #
    #     "slot":           Slot ID, for example KemperMidi.EFFECT_SLOT_ID_A
    # }
    EFFECT_ON_OFF = "EffectEnableAction"
    
    # Generic binary MIDI parameter (on/off)
    # Additional options:
    # {
    #     "mode":           Mode of operation (see PushButtonModes). Optional, default is PushButtonModes.HOLD_MOMENTARY,
    #     "holdTimeMillis": Optional hold time in milliseconds. Default is PushButtonModes.DEFAULT_LATCH_MOMENTARY_HOLD_TIME
    #
    #     "mapping":        A KemperParameterMapping instance. See mappings.py for some predeifined ones.
    #     "color":          Color for switch and display (optional, default: white).
    #     "valueEnabled":   Value to be interpreted as "enabled". Optional: Default is 1
    #     "valueDisabled":  Value to be interpreted as "disabled". Optional: Default is 0
    # }
    BINARY_PARAMETER = "BinaryParameterAction"
    
    #### Internal and development actions #######################################################################################

    # Soft-Reboot the device. Useful for development.
    REBOOT = "RebootAction"

    # Terminate the script. Useful for development.
    TERMINATE = "TerminateAction"

    # Used internally in expore mode to show the pressed IO port. 
    # DO NOT USE IN YOUR CONFIGURATION, OR THE CODE WILL CRASH!
    EXPLORE_IO = "ExploreIoAction"

    # Used internally in expore mode to increase/decrease the enlightened foot switch. 
    # DO NOT USE IN YOUR CONFIGURATION, OR THE CODE WILL CRASH!
    # Additional options:
    # {
    #     "step": Increment step for selecting the next enlightened switch
    # }
    EXPLORE_PIXELS = "ExplorePixelAction"

    # Simple action that prints a fixed text on the console. Used internally.
    # Additional options:
    # {
    #     "text": Text string to print on the console
    # }
    PRINT = "PrintAction"


#################################################################################################################################


# Some default values for some actions
class ActionDefaults:
    DEFAULT_EFFECT_SLOT_CORNER_RADIUS = 15


#################################################################################################################################


# Some default values for switches
class FootSwitchDefaults:

    # Number of NeoPixels for one Footswitch
    NUM_PIXELS = 3

    # Brightness values matching the colors well (i prefer darker lights, use other values) range: [0..1]
    DEFAULT_BRIGHTNESS_ON = 0.25
    DEFAULT_BRIGHTNESS_OFF = 0.01


#################################################################################################################################
 

# Modes for all PushButtonAction subclasses 
class PushButtonModes:
    ENABLE = 0                      # Switch the functionality on
    DISABLE = 10                    # Switch the functionality off
    LATCH = 20                      # Toggle state on every button push
    MOMENTARY = 30                  # Enable on push, disable on release
    MOMENTARY_INVERSE = 40          # Disable on push, Enable on release
    HOLD_MOMENTARY = 50             # Combination of latch, momentary and momentary inverse: If pushed shortly, latch mode is 
                                    # used. If pushed longer than specified in the "holdTimeMillis" parameter, momentary mode is 
                                    # used (inverse or not: This depends on the current state of the functionality. When it is
                                    # on, it will momentarily be switched off and vice versa).

    # Hold time for HOLD_MOMENTARY mode (milliseconds)
    DEFAULT_LATCH_MOMENTARY_HOLD_TIME = 300  

#################################################################################################################################


# This provides known device definitions, ready to use in the config file.
class Ports:
    # PaintAudio MIDI Captain Nano (4 Switches)
    # Board Infos
    # Raspberry Pi Pico (RP2040)
    #
    # GP1  - FootSwitch 1
    # GP4  bat_chg_led
    # GP6  charging
    # GP7  NeoPixel
    # GP8  asyncio PWMOut frequency
    # GP9  - FootSwitch A
    # GP10 - FootSwitch B
    # GP12 tft_dc   (SPI1 RX)
    # GP13 tft_cs   (Chip Select)
    # GP14 spi_clk  (SPI1SCK)
    # GP15 spi_mosi (SPI1 TX)
    # GP16 Midi GP16GP17 baudrate
    # GP17 Midi GP16GP17 baudrate
    # GP25 - FootSwitch 2
    PA_MIDICAPTAIN_NANO_SWITCH_1 = { "port": board.GP1,  "pixels": (0, 1, 2), "name": "1" }
    PA_MIDICAPTAIN_NANO_SWITCH_2 = { "port": board.GP25, "pixels": (3, 4, 5), "name": "2"  }
    PA_MIDICAPTAIN_NANO_SWITCH_A = { "port": board.GP9,  "pixels": (6, 7, 8), "name": "A"  }
    PA_MIDICAPTAIN_NANO_SWITCH_B = { "port": board.GP10, "pixels": (9, 10, 11), "name": "B"  }

    # PaintAudio MIDI Captain Mini (6 Switches)
    # Board Infos
    # Raspberry Pi Pico (RP2040)
    #
    # GP1  - FootSwitch 1
    # GP4  bat_chg_led
    # GP6  charging
    # GP7  NeoPixel
    # GP8  asyncio PWMOut frequency
    # GP9  - FootSwitch A
    # GP10 - FootSwitch B
    # GP11 - FootSwitch C
    # GP12 tft_dc   (SPI1 RX)
    # GP13 tft_cs   (Chip Select)
    # GP14 spi_clk  (SPI1SCK)
    # GP15 spi_mosi (SPI1 TX)
    # GP16 Midi GP16GP17 baudrate
    # GP17 Midi GP16GP17 baudrate
    # GP24 - FootSwitch 3
    # GP25 - FootSwitch 2
    PA_MIDICAPTAIN_MINI_SWITCH_1 = { "port": board.GP1,  "pixels": (0, 1, 2), "name": "1"  }
    PA_MIDICAPTAIN_MINI_SWITCH_2 = { "port": board.GP25, "pixels": (3, 4, 5), "name": "2"  }
    PA_MIDICAPTAIN_MINI_SWITCH_3 = { "port": board.GP24, "pixels": (6, 7, 8), "name": "3"  }
    PA_MIDICAPTAIN_MINI_SWITCH_A = { "port": board.GP9,  "pixels": (9, 10, 11), "name": "A"  }
    PA_MIDICAPTAIN_MINI_SWITCH_B = { "port": board.GP10, "pixels": (12, 13, 14), "name": "B"  }
    PA_MIDICAPTAIN_MINI_SWITCH_C = { "port": board.GP11, "pixels": (15, 16, 17), "name": "C"  }


#################################################################################################################################


# Color definitions (used for LEDs and labels)
class Colors:
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 125, 0)
    RED = (255, 0, 0)
    PURPLE = (180, 0, 120)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 100, 0)
    TURQUOISE = (64, 242, 208)
    BLUE = (0, 0, 255)
    GRAY = (190, 190, 190)
    DARK_GRAY = (50, 50, 50)
    BLACK = (0, 0, 0)

    # Text colors for automatic color detection by maximum contrast to the back color of the display label
    TEXT_COLOR_BRIGHT = (255, 255, 0)
    TEXT_COLOR_DARK = (0, 0, 0)

    # Default background color for display slots
    DEFAULT_LABEL_COLOR = (50, 50, 50)   

    # Default color for switches
    DEFAULT_SWITCH_COLOR = (255, 255, 255)

    # Default colors for some mappings (only used in config)
    MAPPING_RIG_VOLUME_COLOR = (255, 125, 70)


#################################################################################################################################


# Kemper ui specific definitions
class KemperDefinitions:
    # Rig name to show when offline
    OFFLINE_RIG_NAME = "Kemper Profiler (offline)"

    # Max. milliseconds until a request is being terminated and it is
    # assumed that the Kemper device is offline. This is the default value if
    # "maxRequestLifetimeMillis" is not set in the config.
    DEFAULT_MAX_REQUEST_LIFETIME_MILLIS = 2000

    # Effect type color assignment
    EFFECT_COLOR_NONE = Colors.DEFAULT_LABEL_COLOR
    EFFECT_COLOR_WAH = Colors.ORANGE
    EFFECT_COLOR_DISTORTION = Colors.RED
    EFFECT_COLOR_COMPRESSOR = Colors.BLUE
    EFFECT_COLOR_NOISE_GATE = Colors.BLUE
    EFFECT_COLOR_SPACE = Colors.GREEN
    EFFECT_COLOR_CHORUS = Colors.BLUE
    EFFECT_COLOR_PHASER_FLANGER = Colors.PURPLE
    EFFECT_COLOR_EQUALIZER = Colors.YELLOW
    EFFECT_COLOR_BOOSTER = Colors.RED
    EFFECT_COLOR_LOOPER = Colors.PURPLE
    EFFECT_COLOR_PITCH = Colors.WHITE
    EFFECT_COLOR_DUAL = Colors.GREEN
    EFFECT_COLOR_DELAY = Colors.GREEN
    EFFECT_COLOR_REVERB = Colors.GREEN

    # Effect type display names
    EFFECT_NAME_NONE = "-"
    EFFECT_NAME_WAH = "Wah"
    EFFECT_NAME_DISTORTION = "Dist"
    EFFECT_NAME_COMPRESSOR = "Comp"
    EFFECT_NAME_NOISE_GATE = "Gate"
    EFFECT_NAME_SPACE = "Space"
    EFFECT_NAME_CHORUS = "Chorus"
    EFFECT_NAME_PHASER_FLANGER = "Phaser"
    EFFECT_NAME_EQUALIZER = "EQ"
    EFFECT_NAME_BOOSTER = "Boost"
    EFFECT_NAME_LOOPER = "Looper"
    EFFECT_NAME_PITCH = "Pitch"
    EFFECT_NAME_DUAL = "Dual"
    EFFECT_NAME_DELAY = "Delay"
    EFFECT_NAME_REVERB = "Reverb"

    # Colors for special modes
    TUNER_MODE_COLOR = Colors.WHITE


#################################################################################################################################


# Kemper MIDI specification related definitions.
class KemperMidi:
    
    # IDs for the available effect slots
    EFFECT_SLOT_ID_A = 0
    EFFECT_SLOT_ID_B = 1
    EFFECT_SLOT_ID_C = 2
    EFFECT_SLOT_ID_D = 3
    EFFECT_SLOT_ID_X = 4
    EFFECT_SLOT_ID_MOD = 5
    EFFECT_SLOT_ID_DLY = 6
    EFFECT_SLOT_ID_REV = 7

    # Slot enable/disable. Order has to match the one defined above!
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

    CC_TUNER_MODE = 31

    # Product types
    NRPN_PRODUCT_TYPE_PROFILER = 0x00         # Kemper Profiler
    NRPN_PRODUCT_TYPE_PROFILER_PLAYER = 0x02  # Kemper Profiler Player

    # Device IDs
    NRPN_DEVICE_ID_OMNI = 0x7f

    # Parameter types
    NRPN_PARAMETER_TYPE_NUMERIC = 0   # Default, also used for on/off
    NRPN_PARAMETER_TYPE_STRING = 1

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

    # Other adress pages
    NRPN_ADDRESS_PAGE_STRINGS = 0x00
    NRPN_ADDRESS_PAGE_RIG_PARAMETERS = 0x04

    # Generally used NRPN values
    NRPN_MANUFACTURER_ID = [0x00, 0x20, 0x33]             # Kemper manufacturer ID
    NRPN_INSTANCE = 0x00                                  # Instance ID for NRPN. The profiler only supports instance 0.
    NRPN_PARAMETER_OFF = 0
    NRPN_PARAMETER_ON = 1

    # NRPN Function codes
    NRPN_FUNCTION_REQUEST_SINGLE_PARAMETER = 0x41
    NRPN_FUNCTION_REQUEST_STRING_PARAMETER = 0x43

    NRPN_FUNCTION_RESPONSE_SINGLE_PARAMETER = 0x01
    NRPN_FUNCTION_RESPONSE_STRING_PARAMETER = 0x03

    NRPN_FUNCTION_SET_SINGLE_PARAMETER = 0x01

    # NRPN parameters for effect slots
    NRPN_EFFECT_PARAMETER_ADDRESS_TYPE = 0x00   
    NRPN_EFFECT_PARAMETER_ADDRESS_ON_OFF = 0x03    
    # ... TODO add further parameters here

    # Rig parameters (page 0x04)
    NRPN_RIG_PARAMETER_VOLUME = 0x01
    # ... TODO add further parameters here

    # NRPN String parameters
    NRPN_STRING_PARAMETER_ID_RIG_NAME = 0x01
    NRPN_STRING_PARAMETER_ID_RIG_DATE = 0x03


