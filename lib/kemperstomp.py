#################################################################################################################################
# 
# Custom Firmware script for CircuitPi based devices such as the PaintAudio MIDICaptain series, to control the Kemper
# Profiler Player, including display of Rig Name, Effect type feedback etc. which is not implemented by the PaintAudio 
# Kemper firmware (yet).
#
#################################################################################################################################
# v 2.0
# Changes @tunetown:
# - Complete Rewrite 
# - Customization by config script
# - Compatibility with PaintAudio MIDICaptain Nano (4 Switches) and Mini (6 Switches), configurable easily for other devices
#
# -------------------------------------------------------------------------------------------------------------------------------
# v 1.2
# Changes @gstrotmann:
# - Detect Rig changes via rig date
# - Change color for Compressor/Noise Gate to turquoise
#
#################################################################################################################################

import board
import digitalio
import busio
import displayio
from adafruit_display_text import label, wrap_text_to_pixels
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
import usb_midi
import adafruit_midi 
from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive
from adafruit_midi.midi_message import MIDIUnknownEvent

try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

from adafruit_st7789 import ST7789
import neopixel
import random
import time

#################################################################################################################################

# Display properties (cannot be defined in the config file, because the display is initialized before config is loaded)
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240

DISPLAY_ROW_START = 80
DISPLAY_ROTATION = 180
SPI_BAUDRATE = 24000000         # 24MHz

#################################################################################################################################


# TFT driver class
class DisplayDriver:

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def init(self):        
        displayio.release_displays()

        tft_res = board.GP8
        tft_cs = board.GP13
        tft_dc = board.GP12
        spi_mosi = board.GP15
        spi_clk = board.GP14

        spi = busio.SPI(
            spi_clk, 
            MOSI = spi_mosi
        )
        while not spi.try_lock():
            pass
        
        spi.configure(baudrate = SPI_BAUDRATE)  
        spi.unlock()

        display_bus = FourWire(
            spi, 
            command = tft_dc, 
            chip_select = tft_cs, 
            reset = None
        )

        self.tft = ST7789(
            display_bus,
            width = self.width, 
            height = self.height,
            rowstart = DISPLAY_ROW_START, 
            rotation = DISPLAY_ROTATION
        )


#################################################################################################################################

# Initialize Display immediately (to have it already going for debug output when the script and configuration is parsed)
display = DisplayDriver(DISPLAY_WIDTH, DISPLAY_HEIGHT)
display.init()

# Load configuration and definitions. This is realized with a separate script which contains a dictionary called Config.
# (this is an efficient way for a microcontroller script, as YAML or XML etc. take much more resources to validate and parse)
from kemperstomp_def import Actions, Slots, Colors, KemperDefinitions
from kemperstomp_config import Config

#################################################################################################################################


# Buffered font loader
class FontLoader:
    _fonts = {}

    # Returns a font (buffered)
    def get(self, path):
        if path in self._fonts:
            return self._fonts[path]
        
        font = bitmap_font.load_font(path)
        self._fonts[path] = font

        return font


#################################################################################################################################


# Controller for an effect slot label on the user interface
class DisplayLabel:

    # config:
    # {
    #     "font": Path to the font, example: "/fonts/H20.pcf"
    #     "maxTextWidth": Maximum text width in pixels (default: 220) optional
    #     "lineSpacing": Line spacing (optional), float (default: 1)
    # }
    def __init__(self, ui, x, y, width, height, config, text = "", back_color = None, text_color = None):
        self.ui = ui

        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

        self.config = config
        self.font = self.ui.font_loader.get(self.config["font"])

        self.initial_text = text

        self.back_color = back_color
        self.text_color = text_color

        self._add_to_splash()

    # Adds the slot to the splash
    def _add_to_splash(self):
        # Append background, if any
        if self.back_color != None:
            self.background_splash_address = len(self.ui.splash)
            self.ui.splash.append(self._create_background(self.back_color))        

        # Append text area
        self.label = label.Label(
            self.font,
            color = self._get_text_color(),
            anchor_point = (0.5, 0.5), 
            anchored_position = (
                int(self.width / 2), 
                int(self.height / 2)
            ),
            line_spacing = self._get_config_option("lineSpacing")
        )
        self.set_text(self.initial_text)
        
        group = displayio.Group(
            scale = 1, 
            x = self.x, 
            y = self.y
        )

        group.append(self.label) 
        
        self.label_splash_address = len(self.ui.splash)
        self.ui.splash.append(group)        

    # Reads an option
    def _get_config_option(self, name, default = False):
        if name not in self.config:
            return default        
        return self.config[name]

    # Sets the background color
    def set_back_color(self, color):
        self.back_color = color
        self.ui.splash[self.background_splash_address] = self._create_background(color)

        # Also set text color again (might have been changed)
        if self.text_color == None:
            self.label.color = self._get_text_color()

    # Sets the text
    def set_text(self, text):
        if self._get_config_option("maxTextWidth") != False:
            # Wrap text if requested
            text_out = "\n".join(
                wrap_text_to_pixels(
                    text, 
                    self.config["maxTextWidth"], 
                    self.font
                )
            )
        else:
            text_out = text

        self.text = text_out
        self.label.text = text_out

    # Create background Rect
    def _create_background(self, color):
        return Rect(
            self.x, 
            self.y,
            self.width, 
            self.height, 
            fill = color,
            outline = 0x0, 
            stroke = 1
        )

    # Text color: If none is set, auto-detect according to the background
    def _get_text_color(self):        
        text_color = self.text_color
        if text_color == None:
            text_color = self._determine_text_color()
        return text_color

    # Determines a text color by the current background color.
    # Algorithm adapted from https://nemecek.be/blog/172/how-to-calculate-contrast-color-in-python
    def _determine_text_color(self):
        if self.back_color == None:
            return Colors.WHITE
        
        luminance = self._get_luminance(self.back_color)
        if luminance < 140:
            return Colors.WHITE
        else:
            return Colors.BLACK
        
    # Get the luminance of a color, in range [0..255]. 
    def _get_luminance(self, color):
        return color[0] * 0.2126 + color[1] * 0.7151 + color[2] * 0.0721


#################################################################################################################################


# Implements the UI controller
class UserInterface:

    # config must be like:
    # {
    #     "effectLabelHeight": Height of the four effect unit label areas (pixels, default: 40)
    #     "initialInfoText": Text initially shown in the center area (where the rig name goes later on)
    #     "effectSlotLayout": Layout definition for effect slot labels (see DisplayLabel)
    #     "infoAreaLayout": Layout definition for the info area (rig name) label (see DisplayLabel)
    #     "debugAreaLayout": Layout definition for the debug area label (see DisplayLabel)
    # }
    def __init__(self, display, config):
        self.display = display
        self.width = display.width
        self.height = display.height
        self.config = config
        self.debug_area = None
        self.rig_name = None
        self.rig_date = None

        # Effect slots are modeled in a list of DisplayLabel instances (DLY, REV, A, B)
        self.effect_slots = []

        # Font loader (buffered)
        self.font_loader = FontLoader()

    # Show the user interface
    def show(self):
        # Init screen stacking (order matters here!)
        self._init_splash()
        self._init_info_area()
        self._init_slots()
        self._init_debug_area()
        
        self.display.tft.show(self.splash)

    # Set a new rig name. Returns if changed
    def set_rig_name(self, name):
        if self.rig_name == name:
            return False
        
        self.rig_name = name
        self.info.set_text(self.rig_name)
        return True

    # React to a new rig date. Returns if changed
    def set_rig_date(self, date):
        if self.rig_date == date:
            return False
        
        self.rig_date = date
        return True
        
    # Initialize display splash container
    def _init_splash(self):
        self.splash = displayio.Group()
        self.display.tft.rootgroup = self.splash

    # Initialize the effect slots
    def _init_slots(self):
        # Set up the handlers
        slotHeight = self.config["effectLabelHeight"]
        slotWidth = int(self.width / 2)
        lowerY = self.height - slotHeight

        slot_config = self.config["effectSlotLayout"]

        self.effect_slots.append(DisplayLabel(self, 1,   lowerY, slotWidth, slotHeight, slot_config, "A", Colors.DEFAULT_SLOT_COLOR))
        self.effect_slots.append(DisplayLabel(self, 120, lowerY, slotWidth, slotHeight, slot_config, "B", Colors.DEFAULT_SLOT_COLOR))
        self.effect_slots.append(DisplayLabel(self, 1,   1,      slotWidth, slotHeight, slot_config, "DLY", Colors.DEFAULT_SLOT_COLOR))
        self.effect_slots.append(DisplayLabel(self, 120, 1,      slotWidth, slotHeight, slot_config, "REV", Colors.DEFAULT_SLOT_COLOR))

    def _init_info_area(self):
        self.info = DisplayLabel(
            self, 
            0, 0, 
            self.width, self.height,
            self.config["infoAreaLayout"],
            text = self.config["initialInfoText"], 
            back_color = Colors.INFO_AREA_BACK_COLOR,
            text_color = Colors.INFO_AREA_TEXT_COLOR
        )
        
    # Initialize the debug area, if debugging is switched on
    def _init_debug_area(self):
        if Config["debug"] != True:
            return
        
        slotHeight = self.config["effectLabelHeight"]
        upperY = self.height - slotHeight * 2
        self.debug_area = DisplayLabel(
            self, 
            1, upperY, 
            self.width, slotHeight, 
            self.config["debugAreaLayout"],
            text = "DLY", 
            back_color = Colors.DEBUG_BACK_COLOR
        )

    # Show a debug message on the UI if debugging is switched on
    def debug(self, message):
        if self.debug_area == None:
            return
        
        self.debug_area.set_text(message)


#################################################################################################################################


# Implements communication with an array of NeoPixels
class LedDriver:
    def __init__(self, port, num_leds):
        self.port = port
        self.num_leds = num_leds        

        self._init_neopixel()

    # Initialize NeoPixel array. Neopixel documentation:
    # https://docs.circuitpython.org/projects/neopixel/en/latest/
    # https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
    def _init_neopixel(self):        
        self.leds = neopixel.NeoPixel(self.port, self.num_leds)


#################################################################################################################################


# Factory for Action Implementations
class ActionImplementations:

    # Returns an action instance (featuring a process() method), created according to the action configuration passed.
    def get(self, ui, switch, kemper, action_config):
        type = action_config["type"]

        if type == Actions.EFFECT_ON_OFF:
            # Enable/disable an effect slot
            return EffectEnableAction(ui, switch, kemper, action_config)
        
        elif type == Actions.REBOOT:
            # Reboot the device
            return RebootAction(switch, action_config)
        
        else:
            raise Exception("Invalid action type: " + type + ", is this defined in kemperstomp_def.py?")


#################################################################################################################################


# Implements the effect enable/disable footswitch action
class EffectEnableAction:
    
    # Switch states
    STATE_ON = "on"
    STATE_OFF = "off"
    STATE_NOT_ASSIGNED = "na"

    def __init__(self, ui, switch, kemper, action_config):
        self.config = action_config
        self.ui = ui
        self.kemper = kemper
        self.switch = switch
        self.slot_id = self.config["slot"]
        self.effect_type = -1
        self.state = EffectEnableAction.STATE_OFF

    # Process the action
    def process(self):
        self.kemper.set_slot_enabled(self.slot_id, self._enabled())
        self.kemper.request_effect_status(self.slot_id)

    # Receive MIDI messages related to this action
    def receive(self, midi_message):
        type = self.kemper.parse_effect_type(midi_message, self.slot_id)
        status = self.kemper.parse_effect_status(midi_message, self.slot_id)

        if type != None:
            self._receive_type(type)

        if status != None:
            self._receive_status(status)

    # Receive a type value (instance of KemperResponse)
    def _receive_type(self, response):
        if response.value == self.effect_type:
            return

        self.effect_type = response.value

        # Set UI background color according to effect type
        self.switch.set_color(KemperProfilerPlayer.TYPE_COLORS[self.effect_type])

        # Set effect name on UI
        self.ui.effect_slots[self.slot_id].set_text(KemperProfilerPlayer.TYPE_NAMES[self.effect_type])

        if self.effect_type == KemperProfilerPlayer.TYPE_NONE:
            # No effect assigned: Switch off lights
            self.switch.set_brightness(Config["ledBrightness"]["notAssigned"])

        # Request status of the effect after type changes
        self.kemper.request_effect_status(self.slot_id)

    # Receive a status value (instance of KemperResponse)
    def _receive_status(self, response):
        if response.value == True:
            self.state = EffectEnableAction.STATE_ON
            self.switch.set_brightness(Config["ledBrightness"]["on"])
        else:
            self.state = EffectEnableAction.STATE_OFF
            self.switch.set_brightness(Config["ledBrightness"]["off"])

    # Returns if the effect is currently enabled
    def _enabled(self):
        return self.state == EffectEnableAction.STATE_ON


#################################################################################################################################


# Action to reboot the device (for development)
class RebootAction:
    
    def __init__(self, switch, action_config):
        self.config = action_config
        self.switch = switch

        self.switch.set_colors((Colors.YELLOW, Colors.ORANGE, Colors.RED))
        self.switch.set_brightness(1)

        #print(self.switch)

        #time.sleep(5)
        #self.process()

    def process(self):
        import supervisor
        supervisor.reload()

    def receive(self, midi_message):
        pass

#################################################################################################################################


# Controller class for a Foot Switch. Each foot switch has three Neopixels.
class FootSwitch:

    # Number of NeoPixels for one Footswitch
    NUM_PIXELS = 3

    # config must be a dictionary holding the following attributes:
    # { 
    #     "assignment": {
    #         "port": The board GPIO pin definition to be used for this switch (for example board.GP1)
    #         "pixels": List of three indexes for the Neopixels that belong to this switch, for example (0, 1, 2)
    #     },
    #     "actions": {
    #         "type": Action type. Allowed values: See the Actions class in kemperstomp_def.py
    #         ...     (individual options depending on the action)
    #     }
    # }
    def __init__(self, ui, led_driver, kemper, config):
        self.ui = ui
        self.led_driver = led_driver
        self.kemper = kemper
        self.config = config        
        
        self.colors = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
        self.pushed = False
        
        if len(self.config["assignment"]["pixels"]) != len(self.colors):
            raise Exception("Invalid configuration: Amount of pixels not matching " + len(self.colors))
        
        self._initial_colors()
        self._init_switch()     
        self._init_actions()

    # Set up action instances
    def _init_actions(self):
        self.actions = []
        action_factory = ActionImplementations()

        for action_config in self.config["actions"]:
            action = action_factory.get(
                self.ui, 
                self, 
                self.kemper, 
                action_config
            )
            self.actions.append(action)

    # Set some initial colors on the neopixels
    def _initial_colors(self):
        available_colors = (Colors.GREEN, Colors.YELLOW, Colors.RED)  # Colors to be used (in that order)
        start_index = random.randint(0, len(available_colors)-1)      # Random start index  
        self.set_colors((
            available_colors[start_index],
            available_colors[(start_index + 1 ) % len(available_colors)],
            available_colors[(start_index + 2 ) % len(available_colors)]
        ))
        self.set_brightness(1)
    
    # Initializes the switch
    def _init_switch(self):
        self.switch = digitalio.DigitalInOut(self.config["assignment"]["port"]) 
        
        self.switch.direction = digitalio.Direction.INPUT
        self.switch.pull = digitalio.Pull.UP
        
    # Set switch colors (each of the LEDs individually)
    def set_colors(self, colors):
        if len(colors) != len(self.colors):
            raise Exception("Invalid amount of colors: " + len(colors))
        self.colors = colors        

    # Set switch color (all three LEDs equally)
    def set_color(self, color):
        for i in range(len(self.colors)):
            self.colors[i] = color

    # Set to full brightness
    def set_brightness(self, brightness):
        for i in range(len(self.colors)):
            pixel = self.config["assignment"]["pixels"][i]
            self.led_driver.leds[pixel] = (
                int(self.colors[i][0] * brightness), 
                int(self.colors[i][1] * brightness), 
                int(self.colors[i][2] * brightness)
            )
    
    # Return if the switch is currently pushed
    def is_pushed(self):
        return self.switch.value == False  # Inverse logic!

    # Process the switch: Check if it is currently pushed, set state accordingly
    # and send the MIDI messages configured.
    # Returns boolean if the switch has been down.
    def process(self):
        # Is the switch currently pushed? If not, return false.
        if self.is_pushed() == False:
            self.pushed = False
            return False

        # Switch is pushed: Has it been pushed before already? If so, return true but 
        # do not send any MIDI messages again.
        if self.pushed != False:
            return True
        
        # Mark as pushed (prevents redundant messages in the following ticks, when the switch can still be down)
        self.pushed = True

        # Process the assigned action
        self._process_switch_actions()
        return True    

    # Processes all actions assigned to the switch
    def _process_switch_actions(self):
        for action in self.actions:
            action.process()

    # Receive MIDI messages for all actions
    def receive(self, midi_message):
        for action in self.actions:
            action.receive(midi_message)


#################################################################################################################################


# Response from Kemper
class KemperResponse:
    def __init__(self, type, value):
        self.type = type
        self.value = value


#################################################################################################################################


# Implements all Kemper Player related functionality 
# (MIDI messaging etc.)
class KemperProfilerPlayer:

    # Effect types enum (used internally, also for indexing colors, so be sure these are always a row from 0 to n)
    TYPE_NONE = 0
    TYPE_WAH = 1
    TYPE_DISTORTION = 2
    TYPE_COMPRESSOR = 3
    TYPE_NOISE_GATE = 4
    TYPE_SPACE = 5
    TYPE_CHORUS = 6
    TYPE_PHASER_FLANGER = 7
    TYPE_EQUALIZER = 8
    TYPE_BOOSTER = 9
    TYPE_LOOPER = 10
    TYPE_PITCH = 11
    TYPE_DUAL = 12
    TYPE_DELAY = 13
    TYPE_REVERB = 14

    # Effect colors. The order must match the enums for the effect types defined above!
    TYPE_COLORS = (
        KemperDefinitions.EFFECT_COLOR_NONE,
        KemperDefinitions.EFFECT_COLOR_WAH,
        KemperDefinitions.EFFECT_COLOR_DISTORTION,
        KemperDefinitions.EFFECT_COLOR_COMPRESSOR,
        KemperDefinitions.EFFECT_COLOR_NOISE_GATE,
        KemperDefinitions.EFFECT_COLOR_SPACE,
        KemperDefinitions.EFFECT_COLOR_CHORUS,
        KemperDefinitions.EFFECT_COLOR_PHASER_FLANGER,
        KemperDefinitions.EFFECT_COLOR_EQUALIZER,
        KemperDefinitions.EFFECT_COLOR_BOOSTER,
        KemperDefinitions.EFFECT_COLOR_LOOPER,
        KemperDefinitions.EFFECT_COLOR_PITCH,
        KemperDefinitions.EFFECT_COLOR_DUAL,
        KemperDefinitions.EFFECT_COLOR_DELAY,
        KemperDefinitions.EFFECT_COLOR_REVERB
    )

    # Effect type display names. The order must match the enums for the effect types defined above!
    TYPE_NAMES = (
        KemperDefinitions.EFFECT_NAME_NONE,
        KemperDefinitions.EFFECT_NAME_WAH,
        KemperDefinitions.EFFECT_NAME_DISTORTION,
        KemperDefinitions.EFFECT_NAME_COMPRESSOR,
        KemperDefinitions.EFFECT_NAME_NOISE_GATE,
        KemperDefinitions.EFFECT_NAME_SPACE,
        KemperDefinitions.EFFECT_NAME_CHORUS,
        KemperDefinitions.EFFECT_NAME_PHASER_FLANGER,
        KemperDefinitions.EFFECT_NAME_EQUALIZER,
        KemperDefinitions.EFFECT_NAME_BOOSTER,
        KemperDefinitions.EFFECT_NAME_LOOPER,
        KemperDefinitions.EFFECT_NAME_PITCH,
        KemperDefinitions.EFFECT_NAME_DUAL,
        KemperDefinitions.EFFECT_NAME_DELAY,
        KemperDefinitions.EFFECT_NAME_REVERB
    )

    # Requires an USB driver instance
    def __init__(self, midi_usb):
        self.midi_usb = midi_usb

    # Derives the effect type (enum of this class) from the effect type returned by the profiler.
    def get_effect_type(self, kpp_effect_type):
        # NOTE: The ranges are defined by Kemper with a lot of unised numbers, so the borders between types
        # could need to be adjusted with future Kemper firmware updates!
        if (kpp_effect_type == 0):
            return KemperProfilerPlayer.TYPE_NONE
        elif (0 < kpp_effect_type and kpp_effect_type <= 14):
            return KemperProfilerPlayer.TYPE_WAH
        elif (14 < kpp_effect_type and kpp_effect_type <= 45):
            return KemperProfilerPlayer.TYPE_DISTORTION
        elif (45 < kpp_effect_type and kpp_effect_type <= 55):
            return KemperProfilerPlayer.TYPE_COMPRESSOR
        elif (55 < kpp_effect_type and kpp_effect_type <= 60):
            return KemperProfilerPlayer.TYPE_NOISE_GATE       
        elif (60 < kpp_effect_type and kpp_effect_type <= 64):
            return KemperProfilerPlayer.TYPE_SPACE            
        elif (64 < kpp_effect_type and kpp_effect_type <= 80):
            return KemperProfilerPlayer.TYPE_CHORUS
        elif (80 < kpp_effect_type and kpp_effect_type <= 95):
            return KemperProfilerPlayer.TYPE_PHASERFLANGER
        elif (95 < kpp_effect_type and kpp_effect_type <= 110):
            return KemperProfilerPlayer.TYPE_EQUALIZER
        elif (110 < kpp_effect_type and kpp_effect_type <= 120):
            return KemperProfilerPlayer.TYPE_BOOSTER
        elif (120 < kpp_effect_type and kpp_effect_type <= 125):
            return KemperProfilerPlayer.TYPE_LOOPER
        elif (125 < kpp_effect_type and kpp_effect_type <= 135):
            return KemperProfilerPlayer.TYPE_PITCH
        elif (135 < kpp_effect_type and kpp_effect_type <= 143):
            return KemperProfilerPlayer.TYPE_DUAL
        elif (143 < kpp_effect_type and kpp_effect_type <= 170):
            return KemperProfilerPlayer.TYPE_DELAY
        else:
            return KemperProfilerPlayer.TYPE_REVERB

    # Request all rig info (except date)
    def request_rig_info(self):
        self.request_effect_types()
        self.request_rig_name()
        self.request_effects_status()

    # Request rig name
    def request_rig_name(self):
        self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x43, 0x00, 0x00, 0x01]))

    # Request rig creation date
    def request_rig_date(self):
        self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x43, 0x00, 0x00, 0x03]))

    # Sets a slot enabled or disabled
    def set_slot_enabled(self, slot_id, enable):
        enable_int = 0
        if enable == True:
            enable_int = 1

        self.midi_usb.send(ControlChange(Slots.CC_EFFECT_SLOT_ENABLE[slot_id], enable_int))

    # Request types of effect for all slots
    def request_effect_types(self):
        self.request_effect_type(Slots.EFFECT_SLOT_ID_A)
        self.request_effect_type(Slots.EFFECT_SLOT_ID_B)
        self.request_effect_type(Slots.EFFECT_SLOT_ID_DLY)
        self.request_effect_type(Slots.EFFECT_SLOT_ID_REV)

    # Request the effect type of a specific slot
    def request_effect_type(self, slot_id):     
        self.request_single_parameter(
            Slots.SLOT_ADDRESS_PAGE[slot_id], 
            KemperDefinitions.PARAMETER_ADDRESS_EFFECT_TYPE
        )

    # Request effect status for all slots
    def request_effects_status(self):
        self.request_effect_status(Slots.EFFECT_SLOT_ID_A)
        self.request_effect_status(Slots.EFFECT_SLOT_ID_B)
        self.request_effect_status(Slots.EFFECT_SLOT_ID_DLY)
        self.request_effect_status(Slots.EFFECT_SLOT_ID_REV)

    # Request effect status for a specific slot
    def request_effect_status(self, slot_id):
        self.request_single_parameter(
            Slots.SLOT_ADDRESS_PAGE[slot_id], 
            KemperDefinitions.PARAMETER_ADDRESS_EFFECT_STATUS
        )

    def request_single_parameter(self, page, address):
        self.midi_usb.send(
            SystemExclusive(
                [
                    0x00, 
                    0x20, 
                    0x33
                ],
                [
                    0x02, 
                    0x7f, 
                    0x41, 
                    0x00, 
                    page,
                    address
                ]
            )
        )

    # Parse a response for the current rig name
    def parse_rig_name(self, midi_message):
        return self.parse_global_parameter(midi_message, KemperDefinitions.RESPONSE_PREFIX_RIG_NAME)
        
    # Parse a response for the current rig last changed date
    def parse_rig_date(self, midi_message):
        return self.parse_global_parameter(midi_message, KemperDefinitions.RESPONSE_PREFIX_RIG_DATE)

    # Parse a global parameter response
    def parse_global_parameter(self, midi_message, response_prefix):
        if not isinstance(midi_message, SystemExclusive):
            return None

        response = list(midi_message.data)
                
        if response[:6] != response_prefix:
            return None
        
        return KemperResponse(
            KemperDefinitions.RESPONSE_ID_GLOBAL_PARAMETER,
            ''.join(chr(int(c)) for c in response[6:-1])
        )

    # Parse a response for an effect type. Returns None if not relevant to the context.
    def parse_effect_type(self, midi_message, slot_id):
        return self.parse_effect_response(midi_message, slot_id, KemperDefinitions.RESPONSE_ID_EFFECT_TYPE)

    # Parse a response for an effect status. Returns None if not relevant to the context.
    def parse_effect_status(self, midi_message, slot_id):
        return self.parse_effect_response(midi_message, slot_id, KemperDefinitions.RESPONSE_ID_EFFECT_STATUS)

    # Parse a response for an effect parameter. Returns None if not relevant to the context.
    def parse_effect_response(self, midi_message, slot_id, response_type):
        if not isinstance(midi_message, SystemExclusive):
            return None

        response = list(midi_message.data)
                
        if response[:-3] != [0x00, 0x00, 0x01, 0x00, Slots.SLOT_ADDRESS_PAGE[slot_id]]:
            # Message does not belong to this slot
            return None

        if response[5] != response_type:
            # Message is the wrong response type
            return None

        if response[5] == KemperDefinitions.RESPONSE_ID_EFFECT_TYPE:
            # Response to an effect type request
            kpp_effect_type = response[-2] * 128 + response[-1]
            
            return KemperResponse(
                KemperDefinitions.RESPONSE_ID_EFFECT_TYPE,
                self.get_effect_type(kpp_effect_type)
            )
        
        elif response[5] == KemperDefinitions.RESPONSE_ID_EFFECT_STATUS:
            # Response to an effect status request
            if (response[-1] == KemperDefinitions.RESPONSE_ANSWER_STATUS_ON):
                # Effect on
                return KemperResponse(
                    KemperDefinitions.RESPONSE_ID_EFFECT_TYPE,
                    True
                )
            elif (response[-1] == KemperDefinitions.RESPONSE_ANSWER_STATUS_OFF):
                # Effect off
                return KemperResponse(
                    KemperDefinitions.RESPONSE_ID_EFFECT_TYPE,
                    False
                )
        


#################################################################################################################################


# Main application class (controls the processing)    
class KemperStompController:
    def __init__(self, ui, led_driver):        
        self.ui = ui
        self.led_driver = led_driver

        self._init_midi()
        self.kemper = KemperProfilerPlayer(self.midi_usb)

        self._init_switches()

    # Initialize switches
    def _init_switches(self):
        self.switches = []

        for swDef in Config["switches"]:
            self.switches.append(
                FootSwitch(
                    self.ui, 
                    self.led_driver, 
                    self.kemper, 
                    swDef
                )
            )

    # Start MIDI communication
    def _init_midi(self):
        self.midiChannel = Config["midiChannel"]
        
        self.midi_usb = adafruit_midi.MIDI(
            midi_out    = usb_midi.ports[1],
            out_channel = self.midiChannel - 1,
            midi_in     = usb_midi.ports[0],
            in_buf_size = Config["midiBufferSize"], 
            debug       = False
        )

    # Runs the processing loop (which never ends)
    def process(self):
        # Show user interface
        self.ui.show()

        # Start processing loop
        while True:
            start_time = self._get_current_millis()
            self._tick()
            self.ui.debug(str(int((self._get_current_millis() - start_time) * 1000)) + "ms")

    # Processing loop implementation
    def _tick(self):
        # Process all switches
        processed = False
        
        for switch in self.switches:
            processed = switch.process() or processed

        # If any of the switches has been processed, we are done for this tick
        if processed == True:
            return
        
        # No switch has been processed: Receive MIDI messages
        midimsg = self.midi_usb.receive()
        if midimsg == None:
            return
        
        # Receive all switch actions first
        for switch in self.switches:
            switch.receive(midimsg)

        # Receive rig name / date
        self._parse_rig_info(midimsg)

        # Use Midi keep alive Message as trigger to request rig changes
        if isinstance(midimsg, MIDIUnknownEvent):
            self.kemper.request_rig_date()

    # Parse rig info messages
    def _parse_rig_info(self, midi_message):
        rig_name = self.kemper.parse_rig_name(midi_message)
        if rig_name != None:
            self.ui.set_rig_name(rig_name.value)

        rig_date = self.kemper.parse_rig_date(midi_message)
        if rig_date != None:
            if self.ui.set_rig_date(rig_date.value) == True:
                self.kemper.request_rig_info()

    # Returns a current timestmap in milliseconds
    def _get_current_millis(self):
        return time.monotonic()
            

#################################################################################################################################
#################################################################################################################################

# NeoPixel driver 
leds = LedDriver(Config["neoPixelPort"], len(Config["switches"]) * FootSwitch.NUM_PIXELS)

# User interface
ui = UserInterface(display, Config["userInterface"])

# Controller instance (runs the processing loop and keeps everything together)
appl = KemperStompController(ui, leds)
appl.process()
