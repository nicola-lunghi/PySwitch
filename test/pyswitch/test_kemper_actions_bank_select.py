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

    from lib.pyswitch.clients.kemper.actions.bank_select import *
    

class MockController2(Updater):
   def __init__(self):
       Updater.__init__(self)
       self.client = MockClient()
       self.config = {}
       self.shared = {}


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


class TestKemperActionDefinitionsBankSelect(unittest.TestCase):

    def test_bank_colors(self):
        # Current
        self._test_bank_colors(mapping_value = None,  display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        
        self._test_bank_colors(mapping_value = 0,     display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(mapping_value = 1,     display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(mapping_value = 2,     display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(mapping_value = 3,     display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(mapping_value = 4,     display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        
        self._test_bank_colors(mapping_value = 5,     display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(mapping_value = 6,     display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(mapping_value = 7,     display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(mapping_value = 8,     display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)
        self._test_bank_colors(mapping_value = 9,     display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)

        self._test_bank_colors(mapping_value = 10,    display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)

        self._test_bank_colors(mapping_value = NUM_BANKS * NUM_RIGS_PER_BANK - 1,  display_mode = RIG_SELECT_DISPLAY_CURRENT_RIG)

        # Target
        self._test_bank_colors(mapping_value = None,  display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        
        self._test_bank_colors(mapping_value = 0,     display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(mapping_value = 1,     display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(mapping_value = 2,     display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(mapping_value = 3,     display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(mapping_value = 4,     display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        
        self._test_bank_colors(mapping_value = 5,     display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(mapping_value = 6,     display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(mapping_value = 7,     display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(mapping_value = 8,     display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)
        self._test_bank_colors(mapping_value = 9,     display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)

        self._test_bank_colors(mapping_value = 10,    display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)

        self._test_bank_colors(mapping_value = NUM_BANKS * NUM_RIGS_PER_BANK - 1,    display_mode = RIG_SELECT_DISPLAY_TARGET_RIG)


    def _test_bank_colors(self, mapping_value, display_mode):
        # With label but no text callback 
        self._do_test_bank_colors_with_label(
            mapping_value = mapping_value,
            display_mode = display_mode,
            bank = mapping_value // 5 + 2 if mapping_value != None else 0,
            bank_off = None,
            exp_enlightened = False
        )

        self._do_test_bank_colors_with_label(
            mapping_value = mapping_value,
            display_mode = display_mode,
            bank = mapping_value // 5 + 1 if mapping_value != None else 0,
            bank_off = None,
            exp_enlightened = (mapping_value != None) and (display_mode == RIG_SELECT_DISPLAY_TARGET_RIG)
        )

        self._do_test_bank_colors_with_label(
            mapping_value = mapping_value,
            display_mode = display_mode,
            bank = mapping_value // 5 + 1 if mapping_value != None else 0,
            bank_off = mapping_value // 5 + 2 if mapping_value != None else None,
            exp_enlightened = (mapping_value != None) and (display_mode == RIG_SELECT_DISPLAY_TARGET_RIG)
        )

        # Without text callback and label
        self._do_test_bank_colors_without_label(
            mapping_value = mapping_value,
            display_mode = display_mode,
            bank = mapping_value // 5 + 2 if mapping_value != None else 0,
            bank_off = None,
            exp_enlightened = False
        )

        self._do_test_bank_colors_without_label(
            mapping_value = mapping_value,
            display_mode = display_mode,
            bank = mapping_value // 5 + 1 if mapping_value != None else 0,
            bank_off = None,
            exp_enlightened = (mapping_value != None) and (display_mode == RIG_SELECT_DISPLAY_TARGET_RIG)
        )

        self._do_test_bank_colors_without_label(
            mapping_value = mapping_value,
            display_mode = display_mode,
            bank = mapping_value // 5 + 1 if mapping_value != None else 0,
            bank_off = mapping_value // 5 + 2 if mapping_value != None else None,
            exp_enlightened = (mapping_value != None) and (display_mode == RIG_SELECT_DISPLAY_TARGET_RIG)
        )

        # With text callback and label
        if mapping_value != None:
            self._test_bank_colors_with_label_and_cb(
                mapping_value = mapping_value,
                display_mode = display_mode,
                bank = mapping_value // 5 + 2 if mapping_value != None else 0,
                bank_off = None,
                exp_enlightened = False
            )

            self._test_bank_colors_with_label_and_cb(
                mapping_value = mapping_value,
                display_mode = display_mode,
                bank = mapping_value // 5 + 1 if mapping_value != None else 0,
                bank_off = None,
                exp_enlightened = (mapping_value != None) and (display_mode == RIG_SELECT_DISPLAY_TARGET_RIG)
            )

            self._test_bank_colors_with_label_and_cb(
                mapping_value = mapping_value,
                display_mode = display_mode,
                bank = mapping_value // 5 + 1 if mapping_value != None else 0,
                bank_off = mapping_value // 5 + 2 if mapping_value != None else None,
                exp_enlightened = (mapping_value != None) and (display_mode == RIG_SELECT_DISPLAY_TARGET_RIG)
            )


    def _get_exp_color(self, mapping_value, display_mode, bank, bank_off):
        if mapping_value == None:
            return Colors.WHITE
        
        if display_mode == RIG_SELECT_DISPLAY_TARGET_RIG:
            if bank_off != None and (int(mapping_value / 5) == bank - 1):
                return BANK_COLORS[(bank_off - 1) % 5]
            else:
                return BANK_COLORS[(bank - 1) % 5]
        
        return BANK_COLORS[int(mapping_value / 5) % 5]
    
        
    def _do_test_bank_colors_without_label(self, mapping_value, bank, bank_off, display_mode, exp_enlightened):    
        ecb = MockEnabledCallback(output = True)

        exp_color = self._get_exp_color(mapping_value, display_mode, bank, bank_off)

        action = BANK_SELECT(
            bank = bank, 
            bank_off = bank_off,
            display_mode = display_mode, 
            id = 45, 
            use_leds = True, 
            enable_callback = ecb
        )
        
        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)

        mapping = mapping = action.callback._BinaryParameterCallback__mapping 
        mapping.value = mapping_value

        action.update_displays()

        self.assertEqual(switch.color, exp_color)
        self.assertEqual(switch.brightness, 0.3 if exp_enlightened else 0.02)
        

    def _do_test_bank_colors_with_label(self, mapping_value, bank, bank_off, display_mode, exp_enlightened):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        exp_color = self._get_exp_color(mapping_value, display_mode, bank, bank_off)

        ecb = MockEnabledCallback(output = True)

        action = BANK_SELECT(
            display = display,
            bank = bank, 
            bank_off = bank_off,
            display_mode = display_mode, 
            id = 45, 
            use_leds = True, 
            enable_callback = ecb
        )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)

        mapping = mapping = action.callback._BinaryParameterCallback__mapping 
        mapping.value = mapping_value

        action.update_displays()

        self.assertEqual(switch.color, exp_color)
        self.assertEqual(switch.brightness, 0.3 if exp_enlightened else 0.02)

        factor = 1 if exp_enlightened else 0.2

        self.assertEqual(display.back_color, (
            int(exp_color[0] * factor),
            int(exp_color[1] * factor),
            int(exp_color[2] * factor)
        ))

        if mapping_value != None:
            if display_mode == RIG_SELECT_DISPLAY_CURRENT_RIG:
                self.assertEqual(display.text, "Bank " + repr(int(mapping_value / 5) + 1))
            else:
                if bank_off != None and mapping_value // 5 + 1 != bank_off:                
                    self.assertEqual(display.text, "Bank " + repr(bank_off))
                else:
                    self.assertEqual(display.text, "Bank " + repr(bank))             


    def _test_bank_colors_with_label_and_cb(self, mapping_value, bank, bank_off, display_mode, exp_enlightened):
        self._do_test_bank_colors_with_label_and_text_cb(
            mapping_value = mapping_value,
            bank = bank, 
            bank_off = bank_off,
            display_mode = display_mode,
            exp_enlightened = exp_enlightened
        )

        self._do_test_bank_colors_with_label_and_color_cb(
            mapping_value = mapping_value,
            bank = bank, 
            bank_off = bank_off,
            display_mode = display_mode,
            exp_enlightened = exp_enlightened
        )


    def _do_test_bank_colors_with_label_and_text_cb(self, mapping_value, bank, bank_off, display_mode, exp_enlightened):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        exp_color = self._get_exp_color(mapping_value, display_mode, bank, bank_off)

        ecb = MockEnabledCallback(output = True)

        def text_cb(action_paramater, bank, rig):
            self.assertEqual(action, action_paramater)
            return repr(bank) + "|" + repr(rig)

        action = BANK_SELECT(
            display = display,
            bank = bank, 
            bank_off = bank_off,
            display_mode = display_mode, 
            id = 45, 
            use_leds = True, 
            enable_callback = ecb,
            text_callback = text_cb
        )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)

        mapping = mapping = action.callback._BinaryParameterCallback__mapping 
        mapping.value = mapping_value

        action.update_displays()

        self.assertEqual(switch.color, exp_color)
        self.assertEqual(switch.brightness, 0.3 if exp_enlightened else 0.02)

        factor = 1 if exp_enlightened else 0.2

        self.assertEqual(display.back_color, (
            int(exp_color[0] * factor),
            int(exp_color[1] * factor),
            int(exp_color[2] * factor)
        ))

        if mapping_value != None:
            if display_mode == RIG_SELECT_DISPLAY_CURRENT_RIG:
                self.assertEqual(display.text, repr(int(mapping_value / 5)) + "|" + repr(mapping_value % 5))
            else:
                if bank_off != None and mapping_value // 5 + 1 != bank_off:                
                    self.assertEqual(display.text, repr(int(bank_off - 1)) + "|" + repr(mapping_value % 5))
                else:
                    self.assertEqual(display.text, repr(int(bank - 1)) + "|" + repr(mapping_value % 5))    
 

    def _do_test_bank_colors_with_label_and_color_cb(self, mapping_value, bank, bank_off, display_mode, exp_enlightened):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        ecb = MockEnabledCallback(output = True)

        def color_cb(action_paramater, bank, rig):
            self.assertEqual(action, action_paramater)
            self.assertEqual(rig, mapping_value % 5)
            self.assertEqual(bank, int(mapping_value / 5))

            return (3, 4, 5)

        action = BANK_SELECT(
            display = display,
            bank = bank, 
            bank_off = bank_off,
            display_mode = display_mode, 
            id = 45, 
            use_leds = True, 
            enable_callback = ecb,
            color_callback = color_cb
        )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)

        mapping = mapping = action.callback._BinaryParameterCallback__mapping 
        mapping.value = mapping_value

        action.update_displays()

        self.assertEqual(switch.color, (3, 4, 5))
        self.assertEqual(switch.brightness, 0.3 if exp_enlightened else 0.02)

        factor = 1 if exp_enlightened else 0.2

        self.assertEqual(display.back_color, (
            int((3, 4, 5)[0] * factor),
            int((3, 4, 5)[1] * factor),
            int((3, 4, 5)[2] * factor)
        ))
            

 ###################################################################################################################


    def test_overrides(self):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        ecb = MockEnabledCallback(output = True)

        action = BANK_SELECT(
            display = display,
            bank = 1, 
            id = 45, 
            use_leds = True, 
            display_mode = RIG_SELECT_DISPLAY_TARGET_RIG,
            enable_callback = ecb,
            text = "foo",
            color = (5, 6, 7)
        )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)

        mapping = mapping = action.callback._BinaryParameterCallback__mapping 
        
        # On state
        mapping.value = 3
        action.update_displays()
        self.assertEqual(action.state, True)

        self.assertEqual(switch.color, (5, 6, 7))
        self.assertEqual(switch.brightness, 0.3)

        self.assertEqual(display.back_color, (5, 6, 7))

        self.assertEqual(display.text, "foo")

        # Off state
        mapping.value = 22
        action.update_displays()
        self.assertEqual(action.state, False)

        self.assertEqual(switch.color, (5, 6, 7))
        self.assertEqual(switch.brightness, 0.02)

        self.assertEqual(display.back_color, (
            int((5, 6, 7)[0] * 0.2),
            int((5, 6, 7)[1] * 0.2),
            int((5, 6, 7)[2] * 0.2)
        ))

        self.assertEqual(display.text, "foo")


###################################################################################################################


    def test_invalid_display_mode(self):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        ecb = MockEnabledCallback(output = True)

        action = BANK_SELECT(
            display = display,
            bank = 1,
            display_mode = self,                   # Invalid value ;)
            id = 45, 
            use_leds = True, 
            enable_callback = ecb
        )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)

        mapping = mapping = action.callback._BinaryParameterCallback__mapping 
        mapping.value = 0

        with self.assertRaises(Exception):            
            action.update_displays()


###################################################################################################################


    def test_messages(self):
        self._test_messages(0)
        self._test_messages(1)
        self._test_messages(2)
        self._test_messages(3)
        self._test_messages(4)


    def _test_messages(self, rig):
        action = BANK_SELECT(
            bank = 1            
        )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)
        
        mapping = action.callback._BinaryParameterCallback__mapping 
        
        mapping.value = 10 + rig   # Not matching
        action.update_displays()
        self.assertEqual(action.state, False)
        
        # Select rig the first time
        action.push()
        action.release()

        self.assertEqual(len(appl.client.set_calls), 1)
        self.assertEqual(appl.client.set_calls[0], {
            "mapping": KemperMappings.BANK_AND_RIG_SELECT(rig),
            "value": [0, 1, 0]
        })

        mapping.value = rig   # On rig
        action.update_displays()
        self.assertEqual(action.state, True)

        # Select rig again 
        action.push()
        action.release()

        self.assertEqual(len(appl.client.set_calls), 1)

        # self.assertEqual(len(appl.client.set_calls), 2)
        # self.assertEqual(appl.client.set_calls[1], {
        #     "mapping": KemperMappings.BANK_AND_RIG_SELECT(rig),
        #     "value": [0, 1, 0]
        # })

        action.update_displays()
        self.assertEqual(action.state, True)

        # Receive other rig
        mapping.value = rig + 20  # Not matching
        action.update_displays()

        self.assertEqual(action.state, False)

        self.assertEqual(len(appl.client.set_calls), 1)


###################################################################################################################


    def test_messages_bank_off(self):
        self._test_messages_bank_off(0)
        self._test_messages_bank_off(1)
        self._test_messages_bank_off(2)
        self._test_messages_bank_off(3)
        self._test_messages_bank_off(4)


    def _test_messages_bank_off(self, rig):
        action = BANK_SELECT(
            bank = 2,
            bank_off = 4           
        )

        appl = MockController2()
        switch = MockFootswitch(actions = [action])
        action.init(appl, switch)
        
        mapping = action.callback._BinaryParameterCallback__mapping 
        
        mapping.value = 10 + rig   # Not matching
        action.update_displays()
        self.assertEqual(action.state, False)
        
        # Select rig the first time
        action.push()
        action.release()

        self.assertEqual(len(appl.client.set_calls), 1)
        self.assertEqual(appl.client.set_calls[0], {
            "mapping": KemperMappings.BANK_AND_RIG_SELECT(rig),
            "value": [1, 1, 0]
        })

        mapping.value = 5 + rig   # On rig
        action.update_displays()
        self.assertEqual(action.state, True)

        # Receive other rig
        mapping.value = rig + 20  # Not matching
        action.update_displays()

        self.assertEqual(action.state, False)

        self.assertEqual(len(appl.client.set_calls), 1)

        # Select rig again 
        action.push()
        action.release()

        self.assertEqual(len(appl.client.set_calls), 2)
        self.assertEqual(appl.client.set_calls[1], {
            "mapping": KemperMappings.BANK_AND_RIG_SELECT(rig),
            "value": [1, 1, 0]
        })

        mapping.value = 5 + rig   # On rig
        action.update_displays()
        self.assertEqual(action.state, True)

        # Select off rig
        action.push()
        action.release()

        self.assertEqual(len(appl.client.set_calls), 3)
        self.assertEqual(appl.client.set_calls[2], {
            "mapping": KemperMappings.BANK_AND_RIG_SELECT(rig),
            "value": [3, 1, 0]
        })

        mapping.value = 15 + rig   # Off rig
        action.update_displays()
        self.assertEqual(action.state, False)

        action.update_displays()
        self.assertEqual(action.state, False)

        self.assertEqual(len(appl.client.set_calls), 3)


