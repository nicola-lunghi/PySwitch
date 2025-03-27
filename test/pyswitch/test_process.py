import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

class MockFont:
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return repr(self.path)
    

class MockProtocol:
    pass


class MockImports:

    class MockStats:
        class Memory:
            start_calls = 0

            def start():
                MockImports.MockStats.Memory.start_calls += 1


    class MockHardwareAdafruit:
        class AdafruitST7789DisplayDriver: 
            init_calls = 0

            def init(self):
                MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver.init_calls += 1

        class AdafruitNeoPixelDriver:
            pass

        class AdafruitFontLoader:
            pass

    class MockHardwareAdafruitSwitch:
        class AdafruitSwitch:
            def __init__(self, port):
                self.port = port


    class MockMisc:
        def get_option(self, config, name, default = False):
            if not config:
                return default
            if name not in config:
                return default        
            return config[name]
    
 
    class MockConfig:
        Config = None
    
 
    class MockController:
        controllers = []
        raise_on_process = None

        class Controller:
            def __init__(self,
                         led_driver, 
                         protocol,
                         midi,
                         config,                         
                         inputs,
                         ui
            ):
                self.led_driver = led_driver
                self.protocol = protocol
                self.midi = midi
                self.config = config
                self.inputs = inputs
                self.ui = ui

                self.init_calls = 0
                self.tick_calls = 0
                self.quit_after_ticks = 5

                MockImports.MockController.controllers.append(self)

            def init(self):
                self.init_calls += 1
    
                if MockImports.MockController.raise_on_process:
                    raise MockImports.MockController.raise_on_process
                
            def tick(self):
                self.tick_calls += 1

                if self.tick_calls >= self.quit_after_ticks:
                    return False
                else:
                    return True


    class MockMidiController:
        class MidiController:
            def __init__(self, routings):
                self.routings = routings
    

    class MockUiController:
        class UiController:
            def __init__(self,
                         display_driver,
                         font_loader,
                         splash_callback = None
            ):
                self.display_driver = display_driver
                self.font_loader = font_loader
                self.splash_callback = splash_callback
                
    
    class MockCommunication:
        Communication = {
            "protocol": MockProtocol(),
            "midi": {
                "routings": [
                    "routing1",
                    "routing2"
                ]
            }
        }
    

    class MockMidiBridgeWrapper:
        class MidiBridgeWrapper:
            def __init__(self, midi, temp_file_path):
                self.midi = midi
                self.temp_file_path = temp_file_path
                self.error_calls = []
    
            def error(self, e):
                self.error_calls.append(e)


    class MockDisplay:
        Splashes = "SplashCallback"
    
    
    class MockInputs:
        Inputs = [
            "someswitch"
        ]
    
    class MockExploreModeController:
        controllers = []

        class ExploreModeController:
            def __init__(self,
                         board, 
                         switch_factory, 
                         led_driver, 
                         ui
            ):
                self.board = board
                self.switch_factory = switch_factory
                self.led_driver = led_driver
                self.ui = ui
                
                self.init_calls = 0
                self.tick_calls = 0
                self.quit_after_ticks = 5

                MockImports.MockExploreModeController.controllers.append(self)

            def init(self):
                self.init_calls += 1

            def tick(self):
                self.tick_calls += 1

                if self.tick_calls >= self.quit_after_ticks:
                    return False
                else:
                    return True
        

    class MockBoard:
        pass


#######################################################################################################################################################


class TestProcessScript(unittest.TestCase):

    def test(self):
        with patch.dict(sys.modules, {
            "pyswitch.stats": MockImports.MockStats(),
            "pyswitch.hardware.adafruit": MockImports.MockHardwareAdafruit(),
            "pyswitch.misc": MockImports.MockMisc(),
            "config": MockImports.MockConfig(),
            "pyswitch.controller": MockImports.MockController(),
            "pyswitch.controller.midi": MockImports.MockMidiController(),
            "pyswitch.ui.UiController": MockImports.MockUiController(),
            "communication": MockImports.MockCommunication(),
            "pymidibridge.MidiBridgeWrapper": MockImports.MockMidiBridgeWrapper(),
            "display": MockImports.MockDisplay(),
            "inputs": MockImports.MockInputs()
        }):            
            MockImports.MockConfig.Config = { "some": "config" }
            MockImports.MockStats.Memory.start_calls = 0
            MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver.init_calls = 0
            MockImports.MockController.controllers = []
            MockImports.MockExploreModeController.controllers = []
            MockImports.MockController.raise_on_init = None

            import lib.pyswitch.process

            self.assertEqual(MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver.init_calls, 1)
            self.assertEqual(MockImports.MockStats.Memory.start_calls, 0)   # Ensure memory monitoring is off
            
            self.assertEqual(len(MockImports.MockController.controllers), 1)
            self.assertEqual(len(MockImports.MockExploreModeController.controllers), 0)

            controller = MockImports.MockController.controllers[0]

            self.assertEqual(controller.init_calls, 1)
            self.assertEqual(controller.tick_calls, 5)

            self.assertIsInstance(controller.led_driver, MockImports.MockHardwareAdafruit.AdafruitNeoPixelDriver)
            self.assertIsInstance(controller.protocol, MockProtocol)
            
            self.assertIsInstance(controller.midi, MockImports.MockMidiController.MidiController)
            self.assertEqual(controller.midi.routings, ["routing1", "routing2"])
        
            self.assertEqual(controller.config, { "some": "config" })
            self.assertEqual(controller.inputs, ["someswitch"])            
            
            self.assertIsInstance(controller.ui, MockImports.MockUiController.UiController)
            self.assertIsInstance(controller.ui.display_driver, MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver)
            self.assertIsInstance(controller.ui.font_loader, MockImports.MockHardwareAdafruit.AdafruitFontLoader)
            self.assertEqual(controller.ui.splash_callback, "SplashCallback")


    def test_with_bridge(self):
        with patch.dict(sys.modules, {
            "pyswitch.stats": MockImports.MockStats(),
            "pyswitch.hardware.adafruit": MockImports.MockHardwareAdafruit(),
            "pyswitch.misc": MockImports.MockMisc(),
            "config": MockImports.MockConfig(),
            "pyswitch.controller": MockImports.MockController(),
            "pyswitch.controller.midi": MockImports.MockMidiController(),
            "pyswitch.ui.UiController": MockImports.MockUiController(),
            "communication": MockImports.MockCommunication(),
            "pymidibridge.MidiBridgeWrapper": MockImports.MockMidiBridgeWrapper(),
            "display": MockImports.MockDisplay(),
            "inputs": MockImports.MockInputs()
        }):
            MockImports.MockConfig.Config = {
                "enableMidiBridge": True
            }
            MockImports.MockStats.Memory.start_calls = 0
            MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver.init_calls = 0
            MockImports.MockController.controllers = []
            MockImports.MockExploreModeController.controllers = []
            MockImports.MockController.raise_on_process = None

            import lib.pyswitch.process

            self.assertEqual(MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver.init_calls, 1)
            self.assertEqual(MockImports.MockStats.Memory.start_calls, 0)   # Ensure memory monitoring is off

            self.assertEqual(len(MockImports.MockController.controllers), 1)
            self.assertEqual(len(MockImports.MockExploreModeController.controllers), 0)

            controller = MockImports.MockController.controllers[0]

            self.assertEqual(controller.init_calls, 1)
            self.assertEqual(controller.tick_calls, 5)

            self.assertIsInstance(controller.led_driver, MockImports.MockHardwareAdafruit.AdafruitNeoPixelDriver)
            self.assertIsInstance(controller.protocol, MockProtocol)

            self.assertIsInstance(controller.midi, MockImports.MockMidiBridgeWrapper.MidiBridgeWrapper)
            self.assertIsInstance(controller.midi.midi, MockImports.MockMidiController.MidiController)
            self.assertEqual(controller.midi.midi.routings, ["routing1", "routing2"])

            self.assertEqual(controller.config, { "enableMidiBridge": True })
            self.assertEqual(controller.inputs, ["someswitch"])            
            
            self.assertIsInstance(controller.ui, MockImports.MockUiController.UiController)
            self.assertIsInstance(controller.ui.display_driver, MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver)
            self.assertIsInstance(controller.ui.font_loader, MockImports.MockHardwareAdafruit.AdafruitFontLoader)
            self.assertEqual(controller.ui.splash_callback, "SplashCallback")


    def test_error_handling(self):
        with patch.dict(sys.modules, {
            "pyswitch.stats": MockImports.MockStats(),
            "pyswitch.hardware.adafruit": MockImports.MockHardwareAdafruit(),
            "pyswitch.misc": MockImports.MockMisc(),
            "config": MockImports.MockConfig(),
            "pyswitch.controller": MockImports.MockController(),
            "pyswitch.controller.midi": MockImports.MockMidiController(),
            "pyswitch.ui.UiController": MockImports.MockUiController(),
            "communication": MockImports.MockCommunication(),
            "pymidibridge.MidiBridgeWrapper": MockImports.MockMidiBridgeWrapper(),
            "display": MockImports.MockDisplay(),
            "inputs": MockImports.MockInputs()
        }):
            MockImports.MockConfig.Config = { "some": "config" }
            MockImports.MockStats.Memory.start_calls = 0
            MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver.init_calls = 0
            MockImports.MockController.controllers = []
            MockImports.MockExploreModeController.controllers = []
            MockImports.MockController.raise_on_process = Exception()

            with self.assertRaises(Exception):
                import lib.pyswitch.process


    def test_error_handling_with_bridge(self):
        with patch.dict(sys.modules, {
            "pyswitch.stats": MockImports.MockStats(),
            "pyswitch.hardware.adafruit": MockImports.MockHardwareAdafruit(),
            "pyswitch.misc": MockImports.MockMisc(),
            "config": MockImports.MockConfig(),
            "pyswitch.controller": MockImports.MockController(),
            "pyswitch.controller.midi": MockImports.MockMidiController(),
            "pyswitch.ui.UiController": MockImports.MockUiController(),
            "communication": MockImports.MockCommunication(),
            "pymidibridge.MidiBridgeWrapper": MockImports.MockMidiBridgeWrapper(),
            "display": MockImports.MockDisplay(),
            "inputs": MockImports.MockInputs()
        }):
            MockImports.MockConfig.Config = { "enableMidiBridge": True }
            MockImports.MockStats.Memory.start_calls = 0
            MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver.init_calls = 0
            MockImports.MockController.controllers = []
            MockImports.MockExploreModeController.controllers = []
            MockImports.MockController.raise_on_process = Exception()
            
            import lib.pyswitch.process

            self.assertEqual(len(MockImports.MockController.controllers), 1)
            controller = MockImports.MockController.controllers[0]

            self.assertEqual(controller.midi.error_calls, [MockImports.MockController.raise_on_process])
            

################################################################################################################################################


    def test_explore_mode(self):
        with patch.dict(sys.modules, {
            "pyswitch.stats": MockImports.MockStats(),
            "pyswitch.hardware.adafruit": MockImports.MockHardwareAdafruit(),
            "pyswitch.hardware.adafruit.AdafruitSwitch": MockImports.MockHardwareAdafruitSwitch(),
            "pyswitch.misc": MockImports.MockMisc(),
            "config": MockImports.MockConfig(),
            "pyswitch.ui.UiController": MockImports.MockUiController(),
            "pyswitch.controller.explore": MockImports.MockExploreModeController(),
            "board": MockImports.MockBoard()
        }):
            MockImports.MockConfig.Config = {
                "exploreMode": True
            }
            MockImports.MockStats.Memory.start_calls = 0
            MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver.init_calls = 0
            MockImports.MockExploreModeController.controllers = []
            MockImports.MockController.controllers = []
            MockImports.MockController.raise_on_init = None

            import lib.pyswitch.process

            self.assertEqual(MockImports.MockHardwareAdafruit.AdafruitST7789DisplayDriver.init_calls, 1)
            self.assertEqual(MockImports.MockStats.Memory.start_calls, 0)   # Ensure memory monitoring is off

            self.assertEqual(len(MockImports.MockController.controllers), 0)
            self.assertEqual(len(MockImports.MockExploreModeController.controllers), 1)

            controller = MockImports.MockExploreModeController.controllers[0]

            self.assertEqual(controller.init_calls, 1)
            self.assertEqual(controller.tick_calls, 5)

            self.assertIsInstance(controller.led_driver, MockImports.MockHardwareAdafruit.AdafruitNeoPixelDriver)
            self.assertIsInstance(controller.ui, MockImports.MockUiController.UiController)
            self.assertIsInstance(controller.board, MockImports.MockBoard)

            switch_factory = controller.switch_factory

            switch = switch_factory.create_switch(456)

            self.assertIsInstance(switch, MockImports.MockHardwareAdafruitSwitch.AdafruitSwitch)
            self.assertEqual(switch.port, 456)