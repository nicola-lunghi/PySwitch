#################################################################################################################################
# 
# Custom Firmware for CircuitPi based devices such as the PaintAudio MIDICaptain series, to control devices like 
# the Kemper Profiler Player, including display of Rig Name, Effect type feedback etc. which is not implemented by the PaintAudio 
# Kemper firmware (yet). The firmware has been created for Kemper devices but can easily be adapted to others (all Kemper
# specific definitions and code is located in the files beneath this one, the src folder is generic)
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
    from display import Splashes
    from switches import Switches
    from communication import Communication

    # Controller instance (runs the processing loop and keeps everything together)
    _appl = Controller(
        led_driver = _led_driver, 
        protocol = Communication["protocol"],
        midi = MidiController(
            routings = Communication["midi"]["routings"]
        ),
        config = Config, 
        switches = Switches, 
        ui = UiController(
            display_driver = _display_driver,
            font_loader = _font_loader,
            splash_callback = Splashes
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
    
