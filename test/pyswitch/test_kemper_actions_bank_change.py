import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "gc": MockGC()
}):
    from .mocks_appl import *
    from .mocks_callback import *

    from lib.pyswitch.clients.kemper import *
    from lib.pyswitch.ui.elements import DisplayLabel
    from lib.pyswitch.misc import Updater, Colors


class MockController2(Updater):
   def __init__(self):
       Updater.__init__(self)
       self.client = MockClient()


class MockFootswitch:
    def __init__(self, pixels = [0, 1, 2], actions = []):
        self.pixels = pixels
        self.actions = actions

        self.colors = [(0, 0, 0) for i in pixels]
        self.brightnesses = [0 for i in pixels]

    @property
    def color(self):
        return self.colors[0]
    
    @color.setter
    def color(self, color):
        self.colors = [color for i in self.colors]


    @property
    def brightness(self):
        return self.brightnesses[0]
    
    @brightness.setter
    def brightness(self, brightness):
        self.brightnesses = [brightness for i in self.brightnesses]


####################################################################################################


class TestKemperActionDefinitionsBankChange(unittest.TestCase):

    def test_bank_colors(self):
        self.assertEqual(NUM_RIGS_PER_BANK, 5)
        self.assertEqual(len(BANK_COLORS), NUM_RIGS_PER_BANK)

        self._test_bank_colors_dir(True)
        self._test_bank_colors_dir(False)


    def _test_bank_colors_dir(self, up):
        # Current
        self._test_bank_colors(up = up, mapping_value = None,  exp_color = Colors.WHITE, display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        
        self._test_bank_colors(up = up, mapping_value = 0,     exp_color = BANK_COLORS[0], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(up = up, mapping_value = 1,     exp_color = BANK_COLORS[0], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(up = up, mapping_value = 2,     exp_color = BANK_COLORS[0], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(up = up, mapping_value = 3,     exp_color = BANK_COLORS[0], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(up = up, mapping_value = 4,     exp_color = BANK_COLORS[0], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        
        self._test_bank_colors(up = up, mapping_value = 5,     exp_color = BANK_COLORS[1], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(up = up, mapping_value = 6,     exp_color = BANK_COLORS[1], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(up = up, mapping_value = 7,     exp_color = BANK_COLORS[1], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(up = up, mapping_value = 8,     exp_color = BANK_COLORS[1], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(up = up, mapping_value = 9,     exp_color = BANK_COLORS[1], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)

        self._test_bank_colors(up = up, mapping_value = 10,    exp_color = BANK_COLORS[2], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)

        self._test_bank_colors(up = up, mapping_value = NUM_BANKS * NUM_RIGS_PER_BANK - 1,  exp_color = BANK_COLORS[0], display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)

        # Target
        self._test_bank_colors(up = up, mapping_value = None,  exp_color = Colors.WHITE, display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        
        self._test_bank_colors(up = up, mapping_value = 0,     exp_color = BANK_COLORS[1 if up else 4], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(up = up, mapping_value = 1,     exp_color = BANK_COLORS[1 if up else 4], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(up = up, mapping_value = 2,     exp_color = BANK_COLORS[1 if up else 4], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(up = up, mapping_value = 3,     exp_color = BANK_COLORS[1 if up else 4], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(up = up, mapping_value = 4,     exp_color = BANK_COLORS[1 if up else 4], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        
        self._test_bank_colors(up = up, mapping_value = 5,     exp_color = BANK_COLORS[2 if up else 0], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(up = up, mapping_value = 6,     exp_color = BANK_COLORS[2 if up else 0], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(up = up, mapping_value = 7,     exp_color = BANK_COLORS[2 if up else 0], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(up = up, mapping_value = 8,     exp_color = BANK_COLORS[2 if up else 0], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(up = up, mapping_value = 9,     exp_color = BANK_COLORS[2 if up else 0], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)

        self._test_bank_colors(up = up, mapping_value = 10,    exp_color = BANK_COLORS[3 if up else 1], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)

        self._test_bank_colors(up = up, mapping_value = NUM_BANKS * NUM_RIGS_PER_BANK - 1,    exp_color = BANK_COLORS[1 if up else 4], display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)


    def _test_bank_colors(self, up, mapping_value, exp_color, display_mode):
        # Without text callback and label
        self._do_test_bank_colors_with_label(
            up = up,
            mapping_value = mapping_value,
            exp_color = exp_color,
            display_mode = display_mode
        )

        # With label but no text callback (which makes no sense there anyway)
        self._do_test_bank_colors_without_label(
            up = up,
            mapping_value = mapping_value,
            exp_color = exp_color,
            display_mode = display_mode
        )

        # With text callback and label
        if mapping_value != None:
            self._do_test_bank_colors_with_label_and_cb(
                up = up,
                mapping_value = mapping_value,
                display_mode = display_mode,
                exp_color = exp_color
            )


    def _do_test_bank_colors_without_label(self, up, mapping_value, display_mode, exp_color):    
        ecb = MockEnabledCallback(output = True)

        if up:
            action = KemperActionDefinitions.BANK_UP(
                display_mode = display_mode, 
                id = 45, 
                use_leds = True, 
                enable_callback = ecb
            )
        else:
            action = KemperActionDefinitions.BANK_DOWN(
                display_mode = display_mode, 
                id = 45, 
                use_leds = True, 
                enable_callback = ecb
            )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)

        mapping = appl.client.register_calls[0]["mapping"]
        mapping.value = mapping_value

        action.update_displays()

        self.assertEqual(switch.color, exp_color)
        self.assertEqual(switch.brightness, 0.02)


    def _do_test_bank_colors_with_label(self, up, mapping_value, display_mode, exp_color):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        ecb = MockEnabledCallback(output = True)

        if up:
            action = KemperActionDefinitions.BANK_UP(
                display = display, 
                text = "foo", 
                display_mode = display_mode, 
                id = 45, 
                use_leds = True, 
                enable_callback = ecb
            )
        else:
            action = KemperActionDefinitions.BANK_DOWN(
                display = display, 
                text = "foo", 
                display_mode = display_mode, 
                id = 45, 
                use_leds = True, 
                enable_callback = ecb
            )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)

        mapping = appl.client.register_calls[0]["mapping"]
        mapping.value = mapping_value

        action.update_displays()

        self.assertEqual(switch.color, exp_color)
        self.assertEqual(switch.brightness, 0.02)

        self.assertEqual(display.back_color, (
            int(exp_color[0] * 0.2),
            int(exp_color[1] * 0.2),
            int(exp_color[2] * 0.2)
        ))

        self.assertEqual(display.text, "foo")        


    def _do_test_bank_colors_with_label_and_cb(self, up, mapping_value, display_mode, exp_color):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        ecb = MockEnabledCallback(output = True)

        if display_mode == RIG_SELECT_DISPLAY_CURRENT_RIG:
            exp_bank = int(mapping_value / 5) 
            exp_rig = mapping_value % 5
        else:
            exp_bank = int(mapping_value / 5) 

            if up:
                exp_bank += 1
                if exp_bank >= NUM_BANKS:
                    exp_bank = 0
            else:
                exp_bank -= 1
                if exp_bank < 0:
                    exp_bank = NUM_BANKS - 1

            exp_rig = mapping_value % 5

        that = self
        def text_cb(bank, rig):
            that.assertEqual(bank, exp_bank)
            that.assertEqual(rig, exp_rig)
            return repr(bank) + "|" + repr(rig)

        if up:
            action = KemperActionDefinitions.BANK_UP(
                display = display, 
                text = "foo", 
                display_mode = display_mode, 
                id = 45, 
                use_leds = True, 
                enable_callback = ecb,
                text_callback = text_cb
            )
        else:
            action = KemperActionDefinitions.BANK_DOWN(
                display = display, 
                text = "foo", 
                display_mode = display_mode, 
                id = 45, 
                use_leds = True, 
                enable_callback = ecb,
                text_callback = text_cb
            )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)

        mapping = appl.client.register_calls[0]["mapping"]
        mapping.value = mapping_value

        action.update_displays()

        self.assertEqual(switch.color, exp_color)
        self.assertEqual(switch.brightness, 0.02)

        self.assertEqual(display.back_color, (
            int(exp_color[0] * 0.2),
            int(exp_color[1] * 0.2),
            int(exp_color[2] * 0.2)
        ))

        self.assertEqual(display.text, repr(exp_bank) + "|" + repr(exp_rig))


    def test_invalid_display_mode(self):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        ecb = MockEnabledCallback(output = True)
        
        def text_cb(bank, rig):
            pass

        action = KemperActionDefinitions.BANK_UP(
            display = display, 
            display_mode = self,   # Just some value guaranteed to not be equal to one of the valid modes ;)
            id = 45, 
            use_leds = True, 
            enable_callback = ecb,
            text_callback = text_cb
        )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)

        mapping = appl.client.register_calls[0]["mapping"]
        mapping.value = 1

        with self.assertRaises(Exception):            
            action.update_displays()

