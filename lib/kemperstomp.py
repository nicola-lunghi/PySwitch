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

#################################################################################################################################

## Initialize Display first (to have it already going when the configuration is parsed, so the user can
## debug eventual errors)
displayio.release_displays()

disp_width = 240
disp_height = 240

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
spi.configure(baudrate = 24000000)  # Configure SPI for 24MHz
spi.unlock()

display_bus = FourWire(
    spi, 
    command = tft_dc, 
    chip_select = tft_cs, 
    reset = None
)

display = ST7789(
    display_bus,
    width=disp_width, 
    height=disp_height,
    rowstart = 80, 
    rotation = 180
)

######################################################################################################################################################

## Load configuration. This is realized with a separate script which contains a dictionary called Config.
## (this is an efficient way for a microcontroller script, as YAML or XML etc. take much more resources to validate and parse)
from kemperstomp_config import Config

## Initialize Neopixel (status messaging will not really be needed anymore as the longest tast is already done, however
## we already need the number of switches here so this has to be done after config loading)

# Neopixel documentation:
# https://docs.circuitpython.org/projects/neopixel/en/latest/
# https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
NUM_LEDS = len(Config["switches"]) * 3
LED = neopixel.NeoPixel(board.GP7, NUM_LEDS) #, brightness=0.3)

# Set Constants and initial values
# Kemper colors
'''darkgreen = (0, 100, 0)
green = (0, 255, 0)
white = (255, 255, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
purple = (30, 0, 20)
orange = (255, 165, 0)
blue = (0, 0, 255)
turquoise = (64, 242, 208)
gray = (190, 190, 190)

# Set Bitmap Palette with Kemper Colors
palette = displayio.Palette(10)
palette[0] = white
palette[1] = yellow
palette[2] = orange
palette[3] = red
palette[4] = purple
palette[5] = turquoise
palette[6] = blue
palette[7] = green
palette[8] = darkgreen
palette[9] = gray
# palette[10] = 0x2F4538  # Kemper cover green
'''

######################################################################################################################################################
'''
# Draw Effect Module DLY
rect = Rect(1, 1, 120, 40, fill=palette[7], outline=0x0, stroke=1)
splash.append(rect)  # position splash[0] IMPORTANT!

text_group_DLY = displayio.Group(scale=1, x=1, y=1)
text_DLY = "Delay"
text_DLY_area = label.Label(font_H20, text=text_DLY, color=0xFFFFFF, anchor_point=(0.5, 0.5), anchored_position=(60, 20))
text_group_DLY.append(text_DLY_area)  # Subgroup for text scaling

# Draw Effect Module REV
rect = Rect(120, 1, 120, 40, fill=palette[8], outline=0x0, stroke=1)
splash.append(rect)  # position splash[1] IMPORTANT!

text_group_REV = displayio.Group(scale=1, x=120, y=1)
text_REV = "Reverb"
text_REV_area = label.Label(font_H20, text=text_REV, color=0xFFFFFF, anchor_point=(0.5, 0.5), anchored_position=(60, 20))
text_group_REV.append(text_REV_area)  # Subgroup for text scaling

# Draw Effect Module A
rect = Rect(1, 200, 120, 40, fill=palette[5], outline=0x0, stroke=1)
splash.append(rect)  # position splash[2] IMPORTANT!

text_group_A = displayio.Group(scale=1, x=1, y=200)
text_A = "Module A"
text_A_area = label.Label(font_H20, text=text_A, color=0xFFFFFF, anchor_point=(0.5, 0.5), anchored_position=(60, 20))
text_group_A.append(text_A_area)  # Subgroup for text scaling

# Draw Effect Module A
rect = Rect(120, 200, 120, 40, fill=palette[6], outline=0x0, stroke=1)
splash.append(rect)  # position splash[3] IMPORTANT!

text_group_B = displayio.Group(scale=1, x=120, y=200)
text_B = "Module B"
text_B_area = label.Label(font_H20, text=text_B, color=0xFFFFFF, anchor_point=(0.5, 0.5), anchored_position=(60, 20))
text_group_B.append(text_B_area)  # Subgroup for text scaling

# show Rig Name
text_group_rig = displayio.Group(scale=1)
text1 = "Kemper\nEffects Slot Modus"
text_area_rig = label.Label(font, text="\n".join(wrap_text_to_pixels(text1, wrap_width, font)).center(14), color=0xFFFFFF, line_spacing=0.8)
text_area_rig.anchor_point = (0.5, 0.5)
text_area_rig.anchored_position = (CENTER_X, CENTER_Y)
text_group_rig.append(text_area_rig)  # Subgroup for text scaling

# add  text groups
splash.append(text_group_rig)
splash.append(text_group_DLY)
splash.append(text_group_REV)
splash.append(text_group_A)
splash.append(text_group_B)

# activate Display
display.show(splash)


# pick your USB MIDI out channel here, 1-16
MIDI_USB_channel = 1

midi_usb = adafruit_midi.MIDI(midi_out=usb_midi.ports[1],
                              out_channel=MIDI_USB_channel - 1,
                              midi_in=usb_midi.ports[0],
                              in_buf_size=60, debug=False)


# Define Footswitch Class
class FootSwitch:
    def __init__(self, pin, color):
        self.switch = digitalio.DigitalInOut(pin)          # hardware assingment
        self.switch.direction = digitalio.Direction.INPUT
        self.switch.pull = digitalio.Pull.UP
        self.color = [color]                               # color of assingment

    state = "off"                                          # initial state
    effecttype = -1
    bitmap_palette_index = 0

    def setcolor(self):
        # print('new color for ' + str(self.effecttype))

        if (0 < self.effecttype and self.effecttype < 14):
            # Wah -> orange
            self.color = [orange]
            self.bitmap_palette_index = 2
        elif (16 < self.effecttype and self.effecttype < 45):
            # Booster -> red
            self.color = [red]
            self.bitmap_palette_index = 3
        elif (47 < self.effecttype and self.effecttype < 60):
            # Compressor -> blue
            self.color = [turquoise]
            self.bitmap_palette_index = 5
        elif (60 < self.effecttype and self.effecttype < 64):
            # Space -> green
            self.color = [green]
            self.bitmap_palette_index = 8
        elif (64 < self.effecttype and self.effecttype < 80):
            # Chorus -> blue
            self.color = [blue]
            self.bitmap_palette_index = 6
        elif (80 < self.effecttype and self.effecttype < 95):
            # Phaser/Flanger -> purple
            self.color = [purple]
            self.bitmap_palette_index = 4
        elif (90 < self.effecttype and self.effecttype < 110):
            # Equalizer -> yellow
            self.color = [yellow]
            self.bitmap_palette_index = 1
        elif (110 < self.effecttype and self.effecttype < 120):
            # Booster -> red
            self.color = [red]
            self.bitmap_palette_index = 3
        elif (120 < self.effecttype and self.effecttype < 125):
            # Looper -> purple
            self.color = [turquoise]
            self.bitmap_palette_index = 5
        elif (125 < self.effecttype and self.effecttype < 135):
            # Pitch -> white
            self.color = [white]
            self.bitmap_palette_index = 0
        elif (135 < self.effecttype and self.effecttype < 140):
            # Dual -> green
            self.color = [green]
            self.bitmap_palette_index = 7
        elif (140 < self.effecttype and self.effecttype < 170):
            # Delay -> green
            self.color = [green]
            self.bitmap_palette_index = 7
        else:
            # Reverb -> green
            self.color = [darkgreen]
            self.bitmap_palette_index = 8

        return


# function to control neopixel segments - color in full brightness
def light_active(x, c):
    # print(str(x) + ' : ' + str(c[0]))
    pixelpin = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11],  
                [12, 13, 14], [15, 16, 17]]

    for i in pixelpin[x]:
        LED[i] = c[0]

    switch[x].state = "on"
    return


# function to control neopixel segments - color in smaller brightness
def light_dim(x, c):
    # print(str(x) + ' : ' + str(c[0]))
    pixelpin = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11],
                [12, 13, 14], [15, 16, 17]]
    dimcolor = (c[0][0]//10, c[0][1]//10, c[0][2]//10)

    for i in pixelpin[x]:
        LED[i] = dimcolor

    switch[x].state = "off"
    return

    
# function to control neopixel segments - deactivate light
def light_off(x):
    pixelpin = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], 
                [12, 13, 14], [15, 16, 17]]

    for i in pixelpin[x]:
        LED[i] = (0, 0, 0)

    # deactivate switch
    switch[x].state = "na"
    return

    

# function to get Kemper Player Rig Name
def request_kpp_rig_name():
    # request rig name
    midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                  [0x02, 0x7f, 0x43, 0x00, 0x00, 0x01]))

# function to get Kemper Player Rig Creation Date
def request_kpp_rig_date():
    # request rig date
    midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                  [0x02, 0x7f, 0x43, 0x00, 0x00, 0x03]))


# function to get Kemper Player Rig Infos
def request_kpp_rig_details():

    # KPP Effect Module DLY
    # Stomp Type
    midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                  [0x02, 0x7f, 0x41, 0x00, 0x3c, 0x00]))
    # KPP Effekt Module REV
    # Stomp Type
    midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                  [0x02, 0x7f, 0x41, 0x00, 0x3d, 0x00]))
    # KPP Effect Module A
    # Stomp Type (Integer)
    midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                  [0x02, 0x7f, 0x41, 0x00, 0x32, 0x00]))
    # KPP Effect Module+ B
    # Stomp Type
    midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                  [0x02, 0x7f, 0x41, 0x00, 0x33, 0x00]))
    return

# function to get Kemper Effect Status Infos
def get_kpp_effect_status():
    # KPP Effect Module DLY
    # Stomp DLY Status
    if switch[0].state != 'na':
        midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                      [0x02, 0x7f, 0x41, 0x00, 0x3c, 0x03]))

    # KPP Effekt Module REV
    # Stomp Status
    if switch[1].state != 'na':
        midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                      [0x02, 0x7f, 0x41, 0x00, 0x3d, 0x03]))
    # KPP Effect Module A
    # Stomp Status
    if switch[2].state != 'na':
        midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                      [0x02, 0x7f, 0x41, 0x00, 0x32, 0x03]))
    # KPP Effect Module+ B
    # Stomp Status
    if switch[3].state != 'na':
        midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                      [0x02, 0x7f, 0x41, 0x00, 0x33, 0x03]))
    return


# function to control neopixel segments - color in full brightness
def get_module_name(x):
    name = ''
    if (0 < x and x < 14):
        # Wah -> orange
        name = 'Wah Wah'
    elif (16 < x and x < 45):
        # Booster -> red
        name = 'Distortion'
    elif (47 < x and x < 55):
        # Compressor -> blue
        name = 'Compress'
    elif (55 < x and x < 60):
        # Compressor -> blue
        name = 'Noise Gate'
    elif (60 < x and x < 64):
        # Space -> green
        name = 'Space'
    elif (64 < x and x < 80):
        # Chorus -> blue
        name = 'Chorus'
    elif (80 < x and x < 95):
        # Phaser/Flanger -> purple
        name = 'Phaser'
    elif (90 < x and x < 110):
        # Equalizer -> yellow
        name = 'Equalizer'
    elif (110 < x and x < 120):
        # Booster -> red
        name = 'Booster'
    elif (120 < x and x < 125):
        # Phaser/Flanger -> purple
        name = 'Loop'
    elif (125 < x and x < 135):
        # Pitch -> white
        name = 'Transpose '
    elif (135 < x and x < 142):
        # Dual -> green
        name = 'Dual'
    elif (140 < x and x < 170):
        # Dual -> green
        name = 'Delay'
    else:
        name = 'Reverb'

    return name
'''

######################################################################################################################################################

# Color definitions
class Colors:
    DARK_GREEN = (0, 100, 0)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    PURPLE = (30, 0, 20)
    ORANGE = (255, 165, 0)
    BLUE = (0, 0, 255)
    TURQUOISE = (64, 242, 208)
    GRAY = (190, 190, 190)


# Controller for an effect slot label on the user interface
class DisplayLabel:
    def __init__(self, ui, x, y, width, height, font, initial_text = "", initial_color = None, line_spacing = 1):
        self.ui = ui
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.initial_color = initial_color   
        self.initial_text = initial_text            
        self.font = font
        self.line_spacing = line_spacing

        self._add_to_splash()

    # Adds the slot to the splash
    def _add_to_splash(self):
        # Append background, if any
        if self.initial_color != None:
            self.background_splash_address = len(self.ui.splash)
            self.ui.splash.append(self._create_background(self.initial_color))        

        # Append text area
        self.label = label.Label(
            self.font, 
            text = self.initial_text, 
            color = 0xFFFFFF, 
            anchor_point = (0.5, 0.5), 
            anchored_position = (
                int(self.width / 2), 
                int(self.height / 2)
            ),
            line_spacing = self.line_spacing
        )
        
        group = displayio.Group(
            scale = 1, 
            x = self.x, 
            y = self.y
        )

        group.append(self.label) 
        
        self.label_splash_address = len(self.ui.splash)
        self.ui.splash.append(group)        

    # Sets the background color
    def set_color(self, color):
        self.ui.splash[self.background_splash_address] = self._create_background(color)

    # Sets the text
    def set_text(self, text):
        self.label.text = text

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

######################################################################################################################################################


# Implements the UI controller
class UserInterface:

    # config must be like:
    # {
    #     "effectLabelHeight": Height of the four effect unit label areas (pixels, default: 40)
    #     "initialInfoText": Text initially shown in the center area (where the rig name goes later on)
    #     "maxTextWidth": Maximum text width in pixels (default: 220)
    #     "maxTextWidthCharacters": Maximum text width in characters (default: 14)
    # }
    def __init__(self, display, width, height, config):
        self.display = display
        self.width = width
        self.height = height
        self.config = config

        # Effect slots are modeled in a list of DisplayLabel instances (DLY, REV, A, B)
        self.effectSlots = []

        # Set up needed fonts
        self.font = bitmap_font.load_font("/fonts/PTSans-NarrowBold-40.pcf")
        self.font_H20 = bitmap_font.load_font("/fonts/H20.pcf")

    def show(self):
        # Init screen stacking (order matters here!)
        self._init_splash()
        self._init_info_area()
        self._init_slots()
        
        self.display.show(self.splash)

    # Initialize display splash container
    def _init_splash(self):
        self.splash = displayio.Group()
        self.display.rootgroup = self.splash

    # Initialize the effect slots
    def _init_slots(self):
        # Set up the handlers
        slotHeight = self.config["effectLabelHeight"]
        slotWidth = int(self.width / 2)
        lowerY = self.width - slotHeight

        self.effectSlots.append(DisplayLabel(self, 1,   1,      slotWidth, slotHeight, self.font_H20, "DLY", (50, 50, 50)))
        self.effectSlots.append(DisplayLabel(self, 120, 1,      slotWidth, slotHeight, self.font_H20, "REV", (50, 50, 50)))
        self.effectSlots.append(DisplayLabel(self, 1,   lowerY, slotWidth, slotHeight, self.font_H20, "A", (50, 50, 50)))
        self.effectSlots.append(DisplayLabel(self, 120, lowerY, slotWidth, slotHeight, self.font_H20, "B", (50, 50, 50)))

    # Initialize the info (rig name) area
    def _init_info_area(self):
        text = "\n".join(
            wrap_text_to_pixels(
                self.config["initialInfoText"], 
                self.config["maxTextWidth"], 
                self.font
            )
        ).center(self.config["maxTextWidthCharacters"])

        self.info = DisplayLabel(self, 0, 0, self.width, self.height, self.font, initial_text = text, line_spacing = 0.8)
        

######################################################################################################################################################

# Controller class for a Foot Switch. Each foot switch has three Neopixels.
class FootSwitch:

    # Switch states
    STATE_ON = "on"
    STATE_OFF = "off"
    STATE_NOT_ASSIGNED = "na"

    # config must be a dictionary holding the following attributes:
    # { 
    #     "assignment": {
    #         "port": The board GPIO pin definition to be used for this switch (for example board.GP1)
    #         "pixels": List of three indexes for the Neopixels that belong to this switch, for example (0, 1, 2)
    #     }
    # }
    def __init__(self, config):
        self.config = config        
        self.colors = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
        self.state = FootSwitch.STATE_OFF
        
        if len(self.config["assignment"]["pixels"]) != len(self.colors):
            raise Exception("Invalid configuration: Amount of pixels not matching " + len(self.colors))
        
        self._random_colors()
        self._init_switch()
        
    # Set random colors on the neopixels
    def _random_colors(self):
        random_colors = (Colors.YELLOW, Colors.ORANGE, Colors.RED, Colors.GREEN, Colors.BLUE)    
        self.set_colors((
            random_colors[random.randint(0, len(random_colors)-1)],
            random_colors[random.randint(0, len(random_colors)-1)],
            random_colors[random.randint(0, len(random_colors)-1)]
        ))
        self._set_brightness(1)

    # Initializes the switch
    def _init_switch(self):
        self.switch = digitalio.DigitalInOut(self.config["assignment"]["port"]) 
        
        self.switch.direction = digitalio.Direction.INPUT
        self.switch.pull = digitalio.Pull.UP
        
    # Set switch colors (all LEDs individually)
    def set_colors(self, colors):
        if len(colors) != len(self.colors):
            raise Exception("Invalid amount of colors: " + len(colors))
        self.colors = colors

    # Set switch color (all LEDs equally)
    def set_color(self, color):
        for i in range(len(self.colors)):
            self.colors[i] = color

    # Set switch state (on/off/na)
    def set_state(self, state):
        self.state = state
        
        if state == FootSwitch.STATE_ON:
            self._set_brightness(1)
        elif state == FootSwitch.STATE_OFF:
            self._set_brightness(0.1)
        else:
            self._set_brightness(0)

    # Set to full brightness
    def _set_brightness(self, brightness):
        for i in range(len(self.colors)):
            pixel = self.config["assignment"]["pixels"][i]
            LED[pixel] = (
                int(self.colors[i][0] * brightness), 
                int(self.colors[i][1] * brightness), 
                int(self.colors[i][2] * brightness)
            )
    

######################################################################################################################################################


# Implements all Kemper Player related functionality 
# (MIDI messaging etc.)
class KemperProfilerPlayer:

    # Effect types enum (used internally, also for indexing colors, so be sure these are always a row from 0 to n)
    TYPE_WAH = 0
    TYPE_DISTORTION = 1
    TYPE_COMPRESSOR = 2
    TYPE_NOISE_GATE = 3
    TYPE_SPACE = 4
    TYPE_CHORUS = 5
    TYPE_PHASERFLANGER = 6
    TYPE_EQUALIZER = 7
    TYPE_BOOSTER = 8
    TYPE_LOOPER = 9
    TYPE_PITCH = 10
    TYPE_DUAL = 11
    TYPE_DELAY = 12
    TYPE_REVERB = 13

    # Effect colors. The order must match the enums for the effect types defined above!
    TYPE_COLORS = (
        Colors.ORANGE,  # Wah
        Colors.RED,     # Distortion
        Colors.BLUE,    # Compressor
        Colors.BLUE,    # Noise Gate
        Colors.GREEN,   # Space
        Colors.BLUE,    # Chorus
        Colors.PURPLE,  # Phaser/Flanger
        Colors.YELLOW,  # Equalizer
        Colors.RED,     # Booster
        Colors.PURPLE,  # Looper
        Colors.WHITE,   # Pitch
        Colors.GREEN,   # Dual
        Colors.GREEN,   # Delay
        Colors.GREEN    # Reverb
    )

    # Effect type display names. The order must match the enums for the effect types defined above!
    TYPE_NAMES = (
        "Wah Wah",
        "Distortion",
        "Compressor",
        "Noise Gate",
        "Space",
        "Chorus",
        "Phaser",
        "Equalizer",
        "Booster",
        "Looper",
        "Transpose",
        "Dual",
        "Delay",
        "Reverb"
    )

    # Requires an USB driver instance
    def __init__(self, midi_usb):
        self.midi_usb = midi_usb

    # Derives the effect type (enum of this class) from the effect type returned by the profiler.
    def get_effect_type(self, kpp_effect_type):
        # NOTE: The ranges are defined by Kemper with a lot of unised numbers, so the borders between types
        # could need to be adjusted with future Kemper firmware updates!
        if (0 < kpp_effect_type and kpp_effect_type <= 14):
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

    # Request rig name
    def request_rig_name(self):
        self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x43, 0x00, 0x00, 0x01]))

    # Request rig creation date
    def request_rig_date(self):
        self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x43, 0x00, 0x00, 0x03]))

    # Request types of effect for all available effects
    def request_effect_types(self):
        # Effect Module A
        self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x41, 0x00, 0x32, 0x00]))
        # Effect Module B
        self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x41, 0x00, 0x33, 0x00]))
        # Effect Module DLY
        self. midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x41, 0x00, 0x3c, 0x00]))
        # Effect Module REV
        self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                           [0x02, 0x7f, 0x41, 0x00, 0x3d, 0x00]))

    # Request effect status
    def request_effect_status(self):
        # Effect Module A
        if switch[2].state != 'na':
            self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                               [0x02, 0x7f, 0x41, 0x00, 0x32, 0x03]))
        # Effect Module B
        if switch[3].state != 'na':
            self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                               [0x02, 0x7f, 0x41, 0x00, 0x33, 0x03]))
        # Effect Module DLY
        if switch[0].state != 'na':
            self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                               [0x02, 0x7f, 0x41, 0x00, 0x3c, 0x03]))
        # Effect Module REV
        if switch[1].state != 'na':
            self.midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                               [0x02, 0x7f, 0x41, 0x00, 0x3d, 0x03]))


##########################################################################################################

# Main application class (controls the processing)    
class KemperStompController:
    def __init__(self, ui):        
        self.ui = ui
        self._init_switches()
        self._init_midi()

    # Initialize switches
    def _init_switches(self):
        self.switches = []
        for swDef in Config["switches"]:
            self.switches.append(FootSwitch(swDef))

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
        self.ui.show()

######################################################################################################################################################

# User interface
ui = UserInterface(display, disp_width, disp_height, Config["userInterface"])

# Controller instance (runs the processing loop and keeps everything together)
appl = KemperStompController(ui)
appl.process()

######################################################################################################################################################

import time
time.sleep(200)
import sys
sys.exit()

'''
# Define Switch Objects to hold data
switch = []

# with hardware assingment and color+
switch.append(FootSwitch(board.GP1, list(darkgreen)))
switch.append(FootSwitch(board.GP25, list(green)))
#switch.append(FootSwitch(board.GP24, list(white)))
switch.append(FootSwitch(board.GP9, list(red)))
switch.append(FootSwitch(board.GP10, list(yellow)))
#switch.append(FootSwitch(board.GP11, list(orange)))


# set start values
LED.fill(0x000000)  # start using

# Kemper Rig Name
rig_name = ''
rig_date = ''

pushed = False

# Dim Light on for special switches
#light_dim(2, switch[2].color)
#light_dim(5, switch[5].color)


while True:
    if switch[0].switch.value is False:
        if pushed is False:

            pushed = True
            if switch[0].state == "off":
                midi_usb.send(ControlChange(27, 1))
                midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                              [0x02, 0x7f, 0x41, 0x00, 0x3c, 0x03]))
            else:
                midi_usb.send(ControlChange(27, 0))
                midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                              [0x02, 0x7f, 0x41, 0x00, 0x3c, 0x03]))

    elif switch[1].switch.value is False:
        if pushed is False:
            # [1][SE][0x002033][0x027f41003d03]

            pushed = True
            if switch[1].state == "off":
                midi_usb.send(ControlChange(28, 1))
                midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                              [0x02, 0x7f, 0x41, 0x00, 0x3d, 0x03]))
            else:
                midi_usb.send(ControlChange(28, 0))
                midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                              [0x02, 0x7f, 0x41, 0x00, 0x3d, 0x03]))

    #elif switch[2].switch.value is False:
    #    if pushed is False:

    #        pushed = True
    #        if switch[2].state == "off":
    #            light_active(2, switch[2].color)
    #            # switch[2].state = "on"
    #            midi_usb.send(ControlChange(31, 127))
    #        else:
    #            light_dim(2, switch[2].color)
    #            # switch[2].state = "off"
    #            midi_usb.send(ControlChange(31, 0))

    elif switch[2].switch.value is False:
        # [1][SE][0x002033][0x027f41003203]
        if pushed is False:

            pushed = True
            if switch[2].state == "off":
                midi_usb.send(ControlChange(17, 1))
                midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                              [0x02, 0x7f, 0x41, 0x00, 0x32, 0x03]))
            else:
                midi_usb.send(ControlChange(17, 0))
                midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                              [0x02, 0x7f, 0x41, 0x00, 0x32, 0x03]))

    elif switch[3].switch.value is False:
        if pushed is False:
            # [1][SE][0x002033][0x027f41003303]

            pushed = True
            if switch[3].state == "off":
                midi_usb.send(ControlChange(18, 1))
                midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                              [0x02, 0x7f, 0x41, 0x00, 0x33, 0x03]))
            else:
                midi_usb.send(ControlChange(18, 0))
                midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
                                              [0x02, 0x7f, 0x41, 0x00, 0x33, 0x03]))

    #elif switch[5].switch.value is False:
    #    if pushed is False:
    #        # ig volume booster
    #        pushed = True
    #        if switch[5].state == "off":
    #            light_active(5, switch[5].color)
    #            # switch[5].state = "on"
    #            # midi_usb.send(ControlChange(7, 127))
    #            # set rig volume to +3dB
    #            midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
    #                                          [0x02, 0x7f, 0x01, 0x00, 0x04, 0x01, 0x50, 0x00]))
    #        else:
    #            light_dim(5, switch[5].color)
    #            # switch[5].state = "off"
    #            # midi_usb.send(ControlChange(7, 1))
    #            # set rig volume to 0dB
    #            midi_usb.send(SystemExclusive([0x00, 0x20, 0x33],
    #                                          [0x02, 0x7f, 0x01, 0x00, 0x04, 0x01, 0x40, 0x00]))

    else:
        pushed = False

        # read Midi incomming data
        midimsg = midi_usb.receive()

        if midimsg is not None:
            if isinstance(midimsg, ControlChange):
                string_msg = 'ControlChange'
                string_val = str(midimsg.control)

            elif isinstance(midimsg, SystemExclusive):
                string_msg = 'SystemExclusive'
                string_val = str(midimsg.data)
                response = list(midimsg.data)

                # Stomp DLY Status
                if response[:-3] == [0x00, 0x00, 0x01, 0x00, 0x3c]:
                    if response[5] == 0x00:   # Effect Type Response

                        # Effect Type in last 2 list elements
                        effecttype = response[-2] * 128 + response[-1]

                        # is detected Effect Type new?
                        if switch[0].effecttype != effecttype:

                            # update Effect Type in Object
                            switch[0].effecttype = effecttype

                            # is Effectslot is empty?
                            if effecttype == 0:
                                light_off(0)
                                text_DLY_area.text = 'Empty'
                                splash[0] = Rect(1, 1, 120, 40, fill=palette[9], outline=0x0, stroke=1)

                            else:
                                # update new color in object
                                switch[0].setcolor()
                                text_DLY_area.text = get_module_name(effecttype)
                                splash[0] = Rect(1, 1, 120, 40, fill=palette[switch[0].bitmap_palette_index], outline=0x0, stroke=1)

                                # prepare for setting state over SysEx
                                if (switch[0].state == 'na'):
                                    switch[0].state = 'off'

                        get_kpp_effect_status()


                    elif (response[5] == 0x03) and (switch[0].effecttype != 0):   # Effect State Response
                        if (response[-1] == 0x01):
                            light_active(0, switch[0].color)
                        elif (response[-1] == 0x00):
                            light_dim(0, switch[0].color)

                # Stomp REV Status
                elif response[:-3] == [0x00, 0x00, 0x01, 0x00, 0x3d]:
                    if response[5] == 0x00:   # Effect Type Response

                        # Effect Type in last 2 list elements
                        received_typ = response[-2] * 128 + response[-1]

                        # is detected Effect Type new?
                        if switch[1].effecttype != received_typ:

                            # update Effect Type in Object
                            switch[1].effecttype = received_typ
                            # is Effectslot is empty?
                            if received_typ == 0:
                                light_off(1)
                                text_REV_area.text = 'Empty'
                                splash[1] = Rect(120, 1, 120, 40, fill=palette[9], outline=0x0, stroke=1)

                            else:
                                # update new color in object #### have to be deleted
                                switch[1].setcolor()
                                text_REV_area.text = get_module_name(received_typ)
                                splash[1] = Rect(120, 1, 120, 40, fill=palette[switch[1].bitmap_palette_index], outline=0x0, stroke=1)

                                # prepare for setting state over SysEx
                                if (switch[1].state == 'na'):
                                    switch[1].state = 'off'

                        get_kpp_effect_status()

                    elif (response[5] == 0x03) and (switch[1].effecttype != 0):   # Effect State Response
                        if (response[-1] == 0x01):
                            light_active(1, switch[1].color)
                        elif (response[-1] == 0x00):
                            light_dim(1, switch[1].color)

                # Stomp A Status
                elif response[:-3] == [0x00, 0x00, 0x01, 0x00, 0x32]:
                    if response[5] == 0x00:   # Effect Type Response

                        # Effect Type in last 2 list elements
                        received_typ = response[-2] * 128 + response[-1]

                        # is detected Effect Type new?
                        if switch[2].effecttype != received_typ:

                            # update Effect Type in Object
                            switch[2].effecttype = received_typ
                            # is Effectslot is empty?
                            if received_typ == 0:
                                light_off(2)
                                text_A_area.text = 'Empty'
                                splash[2] = Rect(1, 200, 120, 40, fill=palette[9], outline=0x0, stroke=1)
                            else:
                                # update new color in object
                                switch[2].setcolor()
                                splash[2] = Rect(1, 200, 120, 40, fill=palette[switch[2].bitmap_palette_index], outline=0x0, stroke=1)
                                text_A_area.text = get_module_name(received_typ)

                                # prepare for setting state over SysEx
                                if (switch[2].state == 'na'):
                                    switch[2].state = 'off'

                        get_kpp_effect_status()

                    elif (response[5] == 0x03) and (switch[2].effecttype != 0):   # Effect State Response
                        if (response[-1] == 0x01):
                            light_active(2, switch[2].color)
                        elif (response[-1] == 0x00):
                            light_dim(2, switch[2].color)

                # Stomp B Status
                elif response[:-3] == [0x00, 0x00, 0x01, 0x00, 0x33]:
                    if response[5] == 0x00:   # Effect Type Response

                        # Effect Type in last 2 list elements
                        received_typ = response[-2] * 128 + response[-1]

                        # is detected Effect Type new?
                        if switch[3].effecttype != received_typ:

                            # update Effect Type in Object
                            switch[3].effecttype = received_typ
                            # is Effectslot is empty?
                            if (received_typ) == 0:
                                light_off(3)
                                text_B_area.text = 'Empty'
                                splash[3] = Rect(120, 200, 120, 40, fill=palette[9], outline=0x0, stroke=1)
                            else:
                                # update new color in object #### have to be deleted
                                switch[3].setcolor()
                                text_B_area.text = get_module_name(received_typ)
                                splash[3] = Rect(120, 200, 120, 40, fill=palette[switch[3].bitmap_palette_index], outline=0x0, stroke=1)

                                # prepare for setting state over SysEx
                                if (switch[3].state == 'na'):
                                    switch[3].state = 'off'

                        get_kpp_effect_status()

                    elif (response[5] == 0x03) and (switch[3].effecttype != 0):   # Effect State Response
                        if (response[-1] == 0x01):
                            light_active(3, switch[3].color)
                        elif (response[-1] == 0x00):
                            light_dim(3, switch[3].color)

                # Rig Name
                elif response[:6] == [0x00, 0x00, 0x03, 0x00, 0x00, 0x01]:

                    ascii_string = ''.join(chr(int(c)) for c in response[6:-1])

                    if ascii_string != rig_name:
                        rig_name = ascii_string
                        # print(rig_name)
                        # rigtext = ''
                        if len(rig_name) > 22:
                            # rigtext = rig_name[:22]
                            rigtext = rig_name
                        else:
                            rigtext = rig_name

                        text_area_rig.text = "\n".join(wrap_text_to_pixels(rigtext, wrap_width, font))

                        # reset activated 'Booster' on Switch 5
                        #if switch[5].state == "on":
                        #    light_dim(5, switch[5].color)
                        #    switch[5].state = "off"
                        #    midi_usb.send(ControlChange(7, 1))

                # Rig Creation Date
                elif response[:6] == [0x00, 0x00, 0x03, 0x00, 0x00, 0x03]:

                    ascii_string = ''.join(chr(int(c)) for c in response[6:-1])

                    if ascii_string != rig_date:
                        rig_date = ascii_string
                        request_kpp_rig_details()
                        request_kpp_rig_name()
                        get_kpp_effect_status()


                else:
                    # every other SysEx mesage
                    print('not yet assignt: ' + str(response))

            elif isinstance(midimsg, MIDIUnknownEvent):
                # use Midi keep alive Message as trigger
                # these statements dectects rig changes
                request_kpp_rig_date()
                string_msg = ''


            else:
                # not yet assignt midi messages
                string_msg = ''

#'''