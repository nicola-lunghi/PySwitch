#################################################################################################################################
# 
# Definitions of Global Constants
#
#################################################################################################################################

# This defines the available actions. All actions have the following common options.
#
# If the display attribute is defined, this defines properties for a display label connected 
# to the action. Optional: if omitted, no display label will be assigned.
#
# {
#      "type": Type of the action. This determines what the action does, and which configuration options it needs.
#              Use the constants defined in ActionTypes, for example ActionTypes.EFFECT_ON_OFF.
# 
#      "display": {
#          "area":         ID of the display area. See display.py.
#          "index":        Position inside the display area. If omitted, always the first place is used which takes up the whole 
#                          area space. Keep all indices of one area sequentially starting from 0 (not 1!), or you will get 
#                          empty areas!
#          "text":         Text to show on the display label initially.
#          "cornerRadius": Optional corner radius. Default is the underlying layout.
#      }
#
#      "enabled": True     Optional bool parameter to disable/enable the action. Mostly used internally only. Defaults to True 
#                          when not specified.
# }
class ActionTypes:

    # Generic MIDI parameter
    # Additional options:
    # {
    #     "mode":           Mode of operation (see PushButtonModes). Optional, default is PushButtonModes.HOLD_MOMENTARY,
    #     "holdTimeMillis": Optional hold time in milliseconds. Default is PushButtonModes.DEFAULT_LATCH_MOMENTARY_HOLD_TIME
    #
    #     "mapping":        A ClientParameterMapping instance. See mappings.py for some predeifined ones.
    #                       This can also be an array: In this case the mappings are processed in the given order.
    #     "mappingDisable": Mapping to be used on disabling the state. If mapping is an array, this has also to be an array.
    #     "color":          Color for switch and display (optional, default: white). Can be either one color or a tuple of colors
    #                       with one color for each LED segment of the switch (if more actions share the LEDs, only the first
    #                       color is used)
    #     "valueEnabled":   Value to be interpreted as "enabled". Optional: Default is 1. If mapping is a list, this must
    #                       also be a list of values for the mappings.
    #     "valueDisabled":  Value to be interpreted as "disabled". Optional: Default is 0. If mappingDisable (if provided)
    #                       or mapping is a list, this must also be a list of values for the mappings.
    # }
    PARAMETER = "ParameterAction"
    
    # Switches an effect on/off, if the slot is assigned. Based on the PARAMETER (ParameterAction) action, so all options there
    # are available here, too.
    # 
    # Additional options:
    # {
    #     "mapping":        A ClientParameterMapping instance to determine the effect status (on/off). 
    #                       Here, this cannot be an array!
    #     "mappingType":    A ClientParameterMapping instance to determine the effect type. 
    #     "categories":     A EffectCategoryProvider instance to determine the colors and names of the effect types.
    #     "mode":           Mode of operation (see PushButtonModes). Optional, default is PushButtonModes.HOLD_MOMENTARY,
    #     "holdTimeMillis": Optional hold time in milliseconds. Default is PushButtonModes.DEFAULT_LATCH_MOMENTARY_HOLD_TIME
    # }
    EFFECT_ON_OFF = "EffectEnableAction"
    
    #### Internal and development actions #######################################################################################

    # Used to reset the screen areas which show rig info details directly after rig changes.
    # Additional options:
    # {
    #     "resetSwitches":        Reset switches (including LEDs and display labels, if assigned) (optional)
    #     "ignoreOwnSwitch":      Do not reset the switch this action is assigned to (optional)
    #     "resetDisplayAreas":    Reset display areas (defined in Config["displays"]) (optional)
    # }
    RESET_DISPLAYS_FOR_MAPPINGS = "ResetDisplaysAction"

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
 

# Display global constants
class DisplayConstants:

    # Properties for the performance indicator (dot)
    PERFORMANCE_INDICATOR_SIZE = 5
    PERFORMANCE_INDICATOR_MARGIN = 2

    # Factor by which the performance display (dot) is diminished in every update run. Set to 0 to disable, 1 to only show the maximum.
    # Range: [0..1]
    PERFORMANCE_DOT_REDUCE_FACTOR = 0


#################################################################################################################################


# Color definitions (used for LEDs and labels)
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


class ModuleConfig:
    # Base path of this module inside the lib folder. Used to dynamically load action implementations (see Action.py)
    MODULE_BASE_PATH = "pyswitch"


################################################################################################################################


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


################################################################################################################################


# IDs for all available measurements (for statistics)
class StatisticMeasurementTypes:
    TICK_TIME = "Tick"             # Time one processing loop takes overall
    SWITCH_UPDATE_TIME = "SwUp"    # Time between switch state updates