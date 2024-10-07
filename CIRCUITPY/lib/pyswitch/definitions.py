#################################################################################################################################
# 
# Globally used definitions 
#
#################################################################################################################################


# Some processing configuration values
class ProcessingConfig:
    # Max. number of MIDI messages being parsed before the next switch state evaluation
    # is triggered. If set to 0, only one message is parsed per tick, which leads to 
    # flickering states sometimes. If set too high, switch states will not be read for too long.
    # A good value is the maximum amount of switches.
    MAX_NUM_CONSECUTIVE_MIDI_MESSAGES = 10

    # Max. milliseconds until a request is being terminated and it is
    # assumed that the Kemper device is offline. This is the default value if
    # "maxRequestLifetimeMillis" is not set in the config.
    DEFAULT_MAX_REQUEST_LIFETIME_MILLIS = 2000

    # Default interval for updating requested values (milliseconds).
    DEFAULT_UPDATE_INTERVAL_MS = 200


#################################################################################################################################


# Global defaults 
class Defaults:
    DEFAULT_EFFECT_SLOT_CORNER_RADIUS = 15

    # Brightness values matching the colors well (personally i prefer darker lights, you can use other values) range: [0..1]
    DEFAULT_LED_BRIGHTNESS_ON = 0.3
    DEFAULT_LED_BRIGHTNESS_OFF = 0.02

    # Dim factor for disabled effect slots (TFT display only)
    DEFAULT_SLOT_DIM_FACTOR_ON = 1
    DEFAULT_SLOT_DIM_FACTOR_OFF = 0.2


#################################################################################################################################


# Color definitions (can be used for LEDs and labels)
class Colors:
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    DARK_YELLOW = (130, 130, 0)
    ORANGE = (255, 125, 0)
    RED = (255, 0, 0)
    PINK = (255, 125, 70)
    PURPLE = (180, 0, 120)
    DARK_PURPLE = (100, 0, 65)
    LIGHT_GREEN = (100, 255, 100)
    GREEN = (0, 255, 0)
    DARK_GREEN = (0, 100, 0)
    TURQUOISE = (64, 242, 208)
    BLUE = (0, 0, 255)
    DARK_BLUE = (0, 0, 120)
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


################################################################################################################################


# IDs for all available measurements (for statistics)
class StatisticMeasurementTypes:
    TICK_TIME = "Tick"             # Time one processing loop takes overall
    SWITCH_UPDATE_TIME = "SwUp"    # Time between switch state updates. This measurement costs a lot of overhead!