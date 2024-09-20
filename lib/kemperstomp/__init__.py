#################################################################################################################################
# 
# Custom Firmware script for CircuitPi based devices such as the PaintAudio MIDICaptain series, to control the Kemper
# Profiler Player, including display of Rig Name, Effect type feedback etc. which is not implemented by the PaintAudio 
# Kemper firmware (yet).
#
#################################################################################################################################
# v 2.0
# Changes @tunetown (Tom Weber):
# - Complete Rewrite (standalone firmware without dependency on PaintAudio Code, object oriented design etc.)
# - Customization by config script
# - Out-of-the-box Compatibility with PaintAudio MIDICaptain Nano (4 Switches) and Mini (6 Switches),
#   configurable easily for other devices using the new Explore mode (Detect IO addressing for new devices)
# - Activate auto-reload when switch 2 (GP25) is pressed during boot
#
# -------------------------------------------------------------------------------------------------------------------------------
# v 1.2
# Changes @gstrotmann:
# - Detect Rig changes via rig date
# - Change color for Compressor/Noise Gate to turquoise
#
#################################################################################################################################

from .src.hardware.DisplayDriver import DisplayDriver
from .src.Tools import Tools

# Initialize Display first to get console output on config errors
display_driver = DisplayDriver(240, 240)
display_driver.init()

# Load configuration
from .config import Config

if Tools.get_option(Config, "exploreMode") == True:
    # Explore mode: Just shows the pressed GPIO port. This can be used to determine switch assignment 
    # on unknown devices, to create layouts for the configuration.
    from .src.controller.ExploreModeController import ExploreModeController

    appl = ExploreModeController(Config)
    appl.process()
else:
    # Normal mode
    from .src.ui.UserInterface import UserInterface
    from .src.controller.KemperStompController import KemperStompController

    # Create User interface
    ui = UserInterface(display_driver, Config)

    # Controller instance (runs the processing loop and keeps everything together)
    appl = KemperStompController(ui, Config)
    appl.process()
