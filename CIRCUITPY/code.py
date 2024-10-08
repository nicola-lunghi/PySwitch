#################################################################################################################################
# 
# Custom Firmware for CircuitPi based devices such as the PaintAudio MIDICaptain series, to control devices like 
# the Kemper Profiler Player, including display of Rig Name, Effect type feedback etc. which is not implemented by the PaintAudio 
# Kemper firmware (yet). The firmware has been created for Kemper devices but can easily be adapted to others (all Kemper
# specific definitions and code is located in the files beneath this one, the src folder is generic)
#
#################################################################################################################################
# 
# v 2.0
# Changes @tunetown (Tom Weber):
# - Complete Rewrite (standalone firmware without dependency on PaintAudio Code, object oriented design etc.)
# - Customization by config script
# - Out-of-the-box Compatibility with PaintAudio MIDICaptain Nano (4 Switches) and Mini (6 Switches),
#   configurable easily for other devices using the new Explore mode (Detect IO addressing for new devices)
# - Activate auto-reload when switch 2 (GP25) is pressed during boot
# - Conditions in switch assignents an display layouts, to make the configuration depending on device 
#   parameters like the rig name
# - ...
#
# -------------------------------------------------------------------------------------------------------------------------------
#
# v 1.2
# Changes @gstrotmann:
# - Detect Rig changes via rig date
# - Change color for Compressor/Noise Gate to turquoise
#
#################################################################################################################################

from pyswitch.misc import Tools, Memory
Memory.init(zoom=10)

from pyswitch.hardware.adafruit import AdafruitST7789DisplayDriver, AdafruitNeoPixelDriver, AdafruitFontLoader

Memory.watch("Import adafruit drivers")

from pyswitch.ui.UserInterface import UserInterface

Memory.watch("Import UserInterface")

# Initialize Display first to get console output on setup/config errors (for users who do not connect to the serial console)
display_driver = AdafruitST7789DisplayDriver()
display_driver.init()

# Load global config
from config import Config

# NeoPixel driver 
led_driver = AdafruitNeoPixelDriver()

# Buffered font loader
font_loader = AdafruitFontLoader()

# Create User interface
gui = UserInterface(display_driver, font_loader)

Memory.watch("Setup GUI and drivers")

if Tools.get_option(Config, "exploreMode"):
    # Explore mode: Just shows the pressed GPIO port. This can be used to determine switch assignment 
    # on unknown devices, to create layouts for the configuration.
    from pyswitch.controller.ExploreModeController import ExploreModeController

    Memory.watch("Import ExploreModeController")

    appl = ExploreModeController(led_driver, gui)

    Memory.watch("Controller set up")

    appl.process()
    
else:
    # Normal mode
    from pyswitch.controller.Controller import Controller

    Memory.watch("Import Controller")

    # Load configuration files
    from displays import Displays

    Memory.watch("Display Config")

    from switches import Switches, ValueProvider

    Memory.watch("Switches/ValueProvider Config")

    # Controller instance (runs the processing loop and keeps everything together)
    appl = Controller(led_driver, Config, ValueProvider, Switches, Displays, gui)

    Memory.watch("Controller set up")

    appl.process()
