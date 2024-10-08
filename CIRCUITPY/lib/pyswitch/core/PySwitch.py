from .misc.Tools import Tools
from .misc.Memory import Memory

from ..hardware.AdafruitST7789DisplayDriver import AdafruitST7789DisplayDriver
from ..hardware.AdafruitNeoPixelDriver import AdafruitNeoPixelDriver
from ..hardware.AdafruitFontLoader import AdafruitFontLoader

Memory.watch("Import adafruit drivers")

from ..ui.UserInterface import UserInterface

Memory.watch("Import UserInterface")

# Runs the application
class PySwitch:

    @staticmethod
    def run():
        Memory.watch("Run")

        # Initialize Display first to get console output on setup/config errors (for users who do not connect to the serial console)
        display_driver = AdafruitST7789DisplayDriver()
        display_driver.init()

        Memory.watch("Display")

        # Load global config
        from ..config import Config

        Memory.watch("Global Config")

        # NeoPixel driver 
        led_driver = AdafruitNeoPixelDriver()

        # Buffered font loader
        font_loader = AdafruitFontLoader()

        Memory.watch("LED/Font")

        # Create User interface
        gui = UserInterface(display_driver, font_loader)

        Memory.watch("GUI")

        if Tools.get_option(Config, "exploreMode"):
            # Explore mode: Just shows the pressed GPIO port. This can be used to determine switch assignment 
            # on unknown devices, to create layouts for the configuration.
            from .controller.ExploreModeController import ExploreModeController

            Memory.watch("Controller Import")

            appl = ExploreModeController(led_driver, gui)

            Memory.watch("Controller")

            appl.process()
            
        else:
            # Normal mode
            from .controller.Controller import Controller

            Memory.watch("Controller Import")

            # Load configuration files
            from ..displays import Displays

            Memory.watch("Display Config")

            from ..switches import Switches

            Memory.watch("Switches Config")

            # Controller instance (runs the processing loop and keeps everything together)
            appl = Controller(led_driver, Config, Switches, Displays, gui)

            Memory.watch("Controller")

            appl.process()
