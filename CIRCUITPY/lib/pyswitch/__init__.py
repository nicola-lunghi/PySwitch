#################################################################################################################################
# 
# Custom Firmware script for CircuitPi based devices such as the PaintAudio MIDICaptain series, to control devices like 
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
# - Lots of features, see examples
#
# -------------------------------------------------------------------------------------------------------------------------------
#
# v 1.2
# Changes @gstrotmann:
# - Detect Rig changes via rig date
# - Change color for Compressor/Noise Gate to turquoise
#
#################################################################################################################################

from .core.misc.Tools import Tools

from .hardware.AdafruitST7789DisplayDriver import AdafruitST7789DisplayDriver
from .hardware.AdafruitNeoPixelDriver import AdafruitNeoPixelDriver
from .hardware.AdafruitFontLoader import AdafruitFontLoader
from .ui.UserInterface import UserInterface

# Initialize Display first to get console output on setup/config errors (for users who do not connect to the serial console)
display_driver = AdafruitST7789DisplayDriver()
display_driver.init()

# Config
from .config import Config

# NeoPixel driver 
led_driver = AdafruitNeoPixelDriver()

# Buffered font loader
font_loader = AdafruitFontLoader()

# Create User interface
gui = UserInterface(display_driver, font_loader)

if Tools.get_option(Config, "exploreMode"):
    # Explore mode: Just shows the pressed GPIO port. This can be used to determine switch assignment 
    # on unknown devices, to create layouts for the configuration.
    from .core.controller.ExploreModeController import ExploreModeController

    appl = ExploreModeController(led_driver, gui)

    appl.process()
    
else:
    # Normal mode
    from .core.controller.StompController import StompController

    # Load configuration
    from .setup import Setup

    # Controller instance (runs the processing loop and keeps everything together)
    appl = StompController(led_driver, Setup, Config, gui)
    appl.process()
