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
    from lib.pyswitch.controller.pager import *
    from lib.pyswitch.ui.elements import DisplayLabel
    
    from .mocks_appl import *


class MockController2:
    def __init__(self, inputs = []):
        self.inputs = inputs


class MockFootswitch:
    def __init__(self, pixels = [0, 1, 2], actions = []):
        self.pixels = pixels
        self.actions = actions

        self._colors = [(0, 0, 0) for i in pixels]
        self._brightnesses = [0 for i in pixels]

    @property
    def color(self):
        return self._colors[0]

    @property
    def colors(self):
        return self._colors
    
    @colors.setter
    def colors(self, colors):
        self._colors = colors

    @property
    def brightness(self):
        return self._brightnesses[0]

    @property
    def brightnesses(self):
        return self._brightnesses
    
    @brightnesses.setter
    def brightnesses(self, brightnesses):
        self._brightnesses = brightnesses


######################################################


class TestPagerAction(unittest.TestCase):

    def test_without_label(self):
        pager = PagerAction(
            pages = [
                {
                    "id": 1, 
                    "color": (3, 4, 5),
                    "text": "foo"
                },
                {
                    "id": 2, 
                    "color": (3, 6, 8),
                    "text": "bar"
                },
            ],
            led_brightness = 0.4
        )

        action_1 = MockAction({ "enableCallback": pager.enable_callback, "id": 1 })
        action_2 = MockAction({ "enableCallback": pager.enable_callback, "id": 2 })

        switch = MockFootswitch(
            actions = [
                action_1, 
                action_2
            ]
        )
        
        switch_pager = MockFootswitch(
            pixels = [0],
            actions = [
                pager
            ]
        )
        
        appl = MockController2(
            inputs = [
                switch, 
                switch_pager
            ]
        )
        
        pager.init(appl, switch_pager)
        pager.update_displays()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        self.assertEqual(switch_pager.color, (3, 4, 5))
        self.assertEqual(switch_pager.brightness, 0.4)

        # Select page 2
        pager.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), False)
        self.assertEqual(pager.enable_callback.enabled(action_2), True)

        self.assertEqual(switch_pager.color, (3, 6, 8))
        self.assertEqual(switch_pager.brightness, 0.4)

        # Select page 1 again
        pager.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        self.assertEqual(switch_pager.color, (3, 4, 5))
        self.assertEqual(switch_pager.brightness, 0.4)


    def test_no_leds(self):
        pager = PagerAction(
            pages = [
                {
                    "id": 1
                },
                {
                    "id": 2
                },
            ],
            use_leds = False
        )

        action_1 = MockAction({ "enableCallback": pager.enable_callback, "id": 1 })
        action_2 = MockAction({ "enableCallback": pager.enable_callback, "id": 2 })

        switch = MockFootswitch(
            actions = [
                action_1, 
                action_2
            ]
        )
        
        switch_pager = MockFootswitch(
            pixels = [0],
            actions = [
                pager
            ]
        )
        
        appl = MockController2(
            inputs = [
                switch, 
                switch_pager
            ]
        )
        
        pager.init(appl, switch_pager)
        pager.update_displays()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        self.assertEqual(switch_pager.color, (0, 0, 0))
        self.assertEqual(switch_pager.brightness, 0)

        # Select page 2
        pager.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), False)
        self.assertEqual(pager.enable_callback.enabled(action_2), True)

        self.assertEqual(switch_pager.color, (0, 0, 0))
        self.assertEqual(switch_pager.brightness, 0)

        # Select page 1 again
        pager.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        self.assertEqual(switch_pager.color, (0, 0, 0))
        self.assertEqual(switch_pager.brightness, 0)

        
    def test_with_label(self):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        pager = PagerAction(
            pages = [
                {
                    "id": 1, 
                    "color": (3, 4, 5),
                    "text": "foo"
                },
                {
                    "id": 2, 
                    "color": (3, 6, 8),
                    "text": "bar"
                },
            ],
            display = display,
            led_brightness = 0.4
        )

        action_1 = MockAction({ "enableCallback": pager.enable_callback, "id": 1 })
        action_2 = MockAction({ "enableCallback": pager.enable_callback, "id": 2 })

        switch = MockFootswitch(
            actions = [
                action_1, 
                action_2
            ]
        )
        
        switch_pager = MockFootswitch(
            pixels = [0],
            actions = [
                pager
            ]
        )
        
        appl = MockController2(
            inputs = [
                switch, 
                switch_pager
            ]
        )
        
        # These calls shall do nothing before init!
        pager.push()
        pager.update_displays()

        pager.init(appl, switch_pager)
        pager.update_displays()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        self.assertEqual(switch_pager.color, (3, 4, 5))
        self.assertEqual(switch_pager.brightness, 0.4)

        self.assertEqual(pager.label.text, "foo")
        self.assertEqual(pager.label.back_color, (3, 4, 5))

        # Select page 2
        pager.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), False)
        self.assertEqual(pager.enable_callback.enabled(action_2), True)

        self.assertEqual(switch_pager.color, (3, 6, 8))
        self.assertEqual(switch_pager.brightness, 0.4)

        self.assertEqual(pager.label.text, "bar")
        self.assertEqual(pager.label.back_color, (3, 6, 8))

        # Select page 1 again
        pager.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        self.assertEqual(switch_pager.color, (3, 4, 5))
        self.assertEqual(switch_pager.brightness, 0.4)

        self.assertEqual(pager.label.text, "foo")
        self.assertEqual(pager.label.back_color, (3, 4, 5))


    def test_select_page(self):
        display = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        pager = PagerAction(
            pages = [
                {
                    "id": 1, 
                    "color": (3, 4, 5),
                    "text": "foo"
                },
                {
                    "id": 2, 
                    "color": (3, 6, 8),
                    "text": "bar"
                },
            ],
            display = display,
            led_brightness_on = 0.4,
            led_brightness_off = 0.3,
            display_dim_factor_on = 1,
            display_dim_factor_off = 0.5,
            select_page = 2
        )

        action_1 = MockAction({ "enableCallback": pager.enable_callback, "id": 1 })
        action_2 = MockAction({ "enableCallback": pager.enable_callback, "id": 2 })

        switch = MockFootswitch(
            actions = [
                action_1, 
                action_2
            ]
        )
        
        switch_pager = MockFootswitch(
            pixels = [0],
            actions = [
                pager
            ]
        )
        
        appl = MockController2(
            inputs = [
                switch, 
                switch_pager
            ]
        )
        
        # These calls shall do nothing before init!
        pager.push()
        pager.update_displays()

        pager.init(appl, switch_pager)
        pager.update_displays()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        self.assertEqual(switch_pager.color, (3, 6, 8))
        self.assertEqual(switch_pager.brightness, 0.3)

        self.assertEqual(pager.label.text, "bar")
        self.assertEqual(pager.label.back_color, (1, 3, 4))

        # Select page 2
        pager.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), False)
        self.assertEqual(pager.enable_callback.enabled(action_2), True)

        self.assertEqual(switch_pager.color, (3, 6, 8))
        self.assertEqual(switch_pager.brightness, 0.4)

        self.assertEqual(pager.label.text, "bar")
        self.assertEqual(pager.label.back_color, (3, 6, 8))

        # Select page 2 again
        pager.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), False)
        self.assertEqual(pager.enable_callback.enabled(action_2), True)

        self.assertEqual(switch_pager.color, (3, 6, 8))
        self.assertEqual(switch_pager.brightness, 0.4)

        self.assertEqual(pager.label.text, "bar")
        self.assertEqual(pager.label.back_color, (3, 6, 8))


    def test_no_pages(self):
        pager = PagerAction(
            pages = []
        )

        action_1 = MockAction({ "enableCallback": pager.enable_callback, "id": 1 })
        action_2 = MockAction({ "enableCallback": pager.enable_callback, "id": 2 })

        proxy = pager.proxy(
            page_id = 10
        )

        switch = MockFootswitch(
            actions = [
                action_1, 
                action_2
            ]
        )

        switch_proxy = MockFootswitch(
            actions = [
                proxy
            ]
        )
        
        switch_pager = MockFootswitch(
            pixels = [0],
            actions = [
                pager
            ]
        )
        
        appl = MockController2(
            inputs = [
                switch, 
                switch_pager
            ]
        )
        
        pager.init(appl, switch_pager)
        proxy.init(appl, switch_proxy)
        
        pager.update_displays()
        proxy.update_displays()

        self.assertEqual(pager.enable_callback.enabled(action_1), False)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        pager.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), False)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        proxy.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), False)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)


    ###########################################################################################


    def test_proxy(self):
        pager = PagerAction(
            pages = [
                {
                    "id": 1, 
                    "color": (3, 4, 5),
                    "text": "foo"
                },
                {
                    "id": 2, 
                    "color": (3, 6, 8),
                    "text": "bar"
                },
            ],
            led_brightness_on = 0.4,
            led_brightness_off = 0.3,
            display_dim_factor_on = 1,
            display_dim_factor_off = 0.5
        )

        display_1 = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        proxy_1 = pager.proxy(
            page_id = 1,
            use_leds = True,
            display = display_1
        )

        display_2 = DisplayLabel(layout = {
            "font": "foo",
            "backColor": (0, 0, 0)
        })

        proxy_2 = pager.proxy(
            page_id = 2,
            use_leds = True,
            display = display_2
        )

        action_1 = MockAction({ "enableCallback": pager.enable_callback, "id": 1 })
        action_2 = MockAction({ "enableCallback": pager.enable_callback, "id": 2 })

        switch = MockFootswitch(
            actions = [
                action_1, 
                action_2
            ]
        )
        
        switch_pager = MockFootswitch(
            pixels = [0],
            actions = [
                pager
            ]
        )
        
        switch_proxy_1 = MockFootswitch(
            pixels = [0],
            actions = [
                proxy_1
            ]
        )

        switch_proxy_2 = MockFootswitch(
            pixels = [0],
            actions = [
                proxy_2
            ]
        )

        appl = MockController2(
            inputs = [
                switch, 
                switch_pager,
                switch_proxy_1,
                switch_proxy_2
            ]
        )
        
        pager.init(appl, switch_pager)
        proxy_1.init(appl, switch_proxy_1)
        proxy_2.init(appl, switch_proxy_2)

        pager.update_displays()
        proxy_1.update_displays()
        proxy_2.update_displays()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        self.assertEqual(switch_proxy_1.color, (3, 4, 5))
        self.assertEqual(switch_proxy_2.color, (3, 6, 8))
        self.assertEqual(switch_proxy_1.brightness, 0.4)
        self.assertEqual(switch_proxy_2.brightness, 0.3)

        self.assertEqual(proxy_1.label.text, "foo")
        self.assertEqual(proxy_2.label.text, "bar")
        self.assertEqual(proxy_1.label.back_color, (3, 4, 5))
        self.assertEqual(proxy_2.label.back_color, (1, 3, 4))

        # Select page 2
        proxy_2.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), False)
        self.assertEqual(pager.enable_callback.enabled(action_2), True)

        self.assertEqual(switch_proxy_1.color, (3, 4, 5))
        self.assertEqual(switch_proxy_2.color, (3, 6, 8))
        self.assertEqual(switch_proxy_1.brightness, 0.3)
        self.assertEqual(switch_proxy_2.brightness, 0.4)

        self.assertEqual(proxy_1.label.text, "foo")
        self.assertEqual(proxy_2.label.text, "bar")
        self.assertEqual(proxy_1.label.back_color, (1, 2, 2))
        self.assertEqual(proxy_2.label.back_color, (3, 6, 8))

        # Select page 1
        proxy_1.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        self.assertEqual(switch_proxy_1.color, (3, 4, 5))
        self.assertEqual(switch_proxy_2.color, (3, 6, 8))
        self.assertEqual(switch_proxy_1.brightness, 0.4)
        self.assertEqual(switch_proxy_2.brightness, 0.3)

        self.assertEqual(proxy_1.label.text, "foo")
        self.assertEqual(proxy_2.label.text, "bar")
        self.assertEqual(proxy_1.label.back_color, (3, 4, 5))
        self.assertEqual(proxy_2.label.back_color, (1, 3, 4))

    
    def test_proxy_invalid_page(self):
        pager = PagerAction(
            pages = [
                {
                    "id": 1, 
                    "color": (3, 4, 5),
                    "text": "foo"
                },
                {
                    "id": 2, 
                    "color": (3, 6, 8),
                    "text": "bar"
                },
            ],
            led_brightness_on = 0.4,
            led_brightness_off = 0.3,
            display_dim_factor_on = 1,
            display_dim_factor_off = 0.5
        )

        proxy_1 = pager.proxy(
            page_id = 30
        )

        action_1 = MockAction({ "enableCallback": pager.enable_callback, "id": 1 })
        action_2 = MockAction({ "enableCallback": pager.enable_callback, "id": 2 })

        switch = MockFootswitch(
            actions = [
                action_1, 
                action_2
            ]
        )
        
        switch_pager = MockFootswitch(
            pixels = [0],
            actions = [
                pager
            ]
        )
        
        switch_proxy_1 = MockFootswitch(
            pixels = [0],
            actions = [
                proxy_1
            ]
        )

        appl = MockController2(
            inputs = [
                switch, 
                switch_pager,
                switch_proxy_1
            ]
        )
        
        pager.init(appl, switch_pager)
        proxy_1.init(appl, switch_proxy_1)

        pager.update_displays()
        proxy_1.update_displays()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)

        # Select page 2
        proxy_1.push()

        self.assertEqual(pager.enable_callback.enabled(action_1), True)
        self.assertEqual(pager.enable_callback.enabled(action_2), False)
