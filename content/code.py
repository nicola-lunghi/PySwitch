#################################################################################################################################
# 
# Custom Firmware for CircuitPi based devices such as the PaintAudio MIDICaptain series, to control devices like 
# the Kemper Profiler Player, including display of Rig Name, Effect type feedback etc. which is not implemented by the PaintAudio 
# Kemper firmware (yet). The firmware has been created for Kemper devices but can easily be adapted to others (all Kemper
# specific definitions and code is located in the files beneath this one, the src folder is generic)
#
#################################################################################################################################
#
# v 2.1.2
# Changes @tunetown (Tom Weber):
# - Memory usage optimized: 
#     - Avoid keeping of dictionaries for longer than __init__
#     - Removed corner radius from display elements
#     - "fake stroke" (DisplayLabel)
#     - On-flash consts (micropython optimization)
# - Added examples
#
# v 2.1.1
# Changes @tunetown (Tom Weber):
# - Added mappings for Effect Buttons I-IIII (set only, sadly there is no state feedback possibility from Kemper)
#
# v 2.1.0
# Changes @tunetown (Tom Weber):
# - Bidirectional communication with the Kemper devices
# - Tuner Splash showing tuner note and deviation from the note visually
# - HoldAction to assign different actions on long press
# - ParameterAction: Supports different comparison modes now
# - Bug fixes / Unit Tests updated
# 
# v 2.0.0
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

from pyswitch.Memory import Memory # type: ignore
Memory.start()

from pyswitch.hardware.adafruit import AdafruitST7789DisplayDriver, AdafruitNeoPixelDriver, AdafruitFontLoader, AdafruitSwitch
from pyswitch.misc import get_option

# Initialize Display first to get console output on setup/config errors (for users who do not connect to the serial console)
_display_driver = AdafruitST7789DisplayDriver()
_display_driver.init()

# Load global config
from config import Config

# NeoPixel driver 
_led_driver = AdafruitNeoPixelDriver()

# Buffered font loader
_font_loader = AdafruitFontLoader()

if not get_option(Config, "exploreMode"):
    # Normal operation
    from pyswitch.controller.Controller import Controller
    from pyswitch.controller.MidiController import MidiController
    from pyswitch.ui.UiController import UiController

    # Load configuration files
    from display import Display
    from switches import Switches
    from communication import Communication

    # Controller instance (runs the processing loop and keeps everything together)
    _appl = Controller(
        led_driver = _led_driver, 
        communication = Communication, 
        midi = MidiController(
            routings = Communication["midi"]["routings"] if get_option(Communication, "midi") else [],
            debug  = get_option(Config, "debugMidi")
        ),
        config = Config, 
        switches = Switches, 
        ui = UiController(
            display_driver = _display_driver,
            font_loader = _font_loader,
            root = Display
        )
    )
    
    _appl.process()

else:
    # Explore mode: Just shows the pressed GPIO port. This can be used to determine switch assignment 
    # on unknown devices, to create layouts for the configuration.
    from pyswitch.controller.ExploreModeController import ExploreModeController
    from pyswitch.ui.UiController import UiController
    import board

    # Switch factory
    class _SwitchFactory:
        def create_switch(self, port):
            return AdafruitSwitch(port)

    _appl = ExploreModeController(
        board = board, 
        switch_factory = _SwitchFactory(), 
        led_driver = _led_driver, 
        ui = UiController(
            display_driver = _display_driver,
            font_loader = _font_loader
        )
    )

    _appl.process()
    
