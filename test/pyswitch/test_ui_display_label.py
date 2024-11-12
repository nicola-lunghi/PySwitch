import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "micropython": MockMicropython,
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
    "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
    "usb_midi": MockUsbMidi(),
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from lib.pyswitch.ui.ui import DisplayBounds
    from lib.pyswitch.ui.elements import DisplayLabel, DisplayLabelLayout    
    from lib.pyswitch.misc import Updater

    from .mocks_appl import *
    from .mocks_ui import *


#class CheckAreaColors:
#    def __init__(self, testcase):
#        self.case = testcase

#    # Checks if the passed parts (rects or round rects) fill up the area completely,
#    # split in rows
#    def run(self, area, parts, colors):
#        part_height = int(area.height / len(colors))

#        # Check one pixel in the middle of each expected color area
#        for i in range(len(colors)):
#            x = area.x + int(area.width / 2)
#            y = int(part_height / 2) + i * part_height

#            exp_color = colors[i]
#            act_color = self._render_color(parts, x, y)#

#            self.case.assertEqual(act_color, exp_color)

#    # Returns the color at a given pixel position
#    def _render_color(self, parts, x, y):
#        ret = None
        
#        for part in parts:
#            if (part.x <= x and part.x + part.width >= x and
#                part.y <= y and part.y + part.height >= y):
                
#                ret = part.fill

#        return ret


###############################################################################################


class TestDisplayLabel(unittest.TestCase):

    def test_layout_condition(self):
        layout_def_1 = {
            "font": "foo",
            "maxTextWidth": 222,
            "lineSpacing": 0.6,
            "text": "footext",
            "textColor": (2, 3, 4),
            "backColor": (20, 30, 40),
            "stroke": 4
        }

        layout_def_2 = {
            "font": "bar",
            "maxTextWidth": 223,
            "lineSpacing": 0.7,
            "text": "bartext",
            "textColor": (3, 4, 5),
            "backColor": (30, 40, 50),
            "stroke": 5
        }

        condition_1 = MockCondition(
            yes = layout_def_1,
            no = layout_def_2,
        )

        label = DisplayLabel(
            layout = condition_1,
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        ui = MockDisplaySplash()
        u = Updater()
        u.low_memory_warning = False

        label.init(ui, u)

        self.assertTrue(self._compare_layouts(label.layout, DisplayLabelLayout(layout_def_1)))
        self.assertEqual(label.text, "footext")

        condition_1.bool_value = False
        u.update()
        
        self.assertTrue(self._compare_layouts(label.layout, DisplayLabelLayout(layout_def_2)))
        self.assertEqual(label.text, "footext")

        # Set identical layout (shall not change anything)
        layout_def_2["text"] = "footext"
        label.layout = DisplayLabelLayout(layout_def_2)

        self.assertTrue(self._compare_layouts(label.layout, DisplayLabelLayout(layout_def_2)))
        self.assertEqual(label.text, "footext")


    def test_layout_no_font(self):
        with self.assertRaises(Exception):            
            DisplayLabel(
                layout = {},
                bounds = DisplayBounds(20, 21, 200, 210)
            )


    def test_layout_defaults(self):
        label = DisplayLabel(
            layout = {
                "font": "foo"
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        self.assertTrue(
            self._compare_layouts(
                label.layout,
                DisplayLabelLayout({
                    "font": "foo",
                    "maxTextWidth": False,
                    "lineSpacing": 1,
                    "text": "",
                    "textColor": None,
                    "backColor": None,
                    "stroke": 0
                })
            )
        )

    # Helper to compare two layouts
    def _compare_layouts(self, a, b):
        return (a.font_path == b.font_path and 
                a.max_text_width == b.max_text_width and
                a.line_spacing == b.line_spacing and
                #a.text == b.text and
                a.text_color == b.text_color and
                a.back_color == b.back_color and 
                a.stroke == b.stroke)
    
    
    #def _stringify_layout(self, layout):
    #    return repr(layout.__dict__)
    

###############################################################################################


    def test_label(self):
        self._test_label(20, 21, 200, 210, None, 0, "hey", (255, 255, 255), None)
        self._test_label(20, 21, 200, 210, None, 0, "hey", (200, 255, 255), (200, 255, 255))

        self._test_label(20, 21, 200, 210, (3, 4, 5), 0, "hey", (255, 200, 255), (255, 200, 255))
        self._test_label(20, 21, 200, 210, (3, 4, 5), 0, "", (255, 255, 255), None)
        self._test_label(20, 21, 200, 210, (3, 4, 5), 2, "bar", (255, 255, 200), (255, 255, 200))
        self._test_label(20, 21, 200, 210, (3, 4, 5), 3, "foo", (255, 255, 255), None)

        self._test_label(20, 21, 200, 210, (200, 240, 250), 3, "foo", (0, 0, 0), None)
        self._test_label(20, 21, 200, 210, (200, 140, 250), 3, "foo", (0, 0, 0), None)
        self._test_label(20, 21, 200, 210, (0, 0, 0), 3, "foo", (255, 255, 255), None)
        self._test_label(20, 21, 200, 210, (30, 50, 100), 3, "foo", (255, 255, 255), None)


    def _test_label(self, x, y, w, h, fill, stroke, text, text_color_exp, text_color_set):
        layout_def_1 = {
            "font": "foo",
            "backColor": fill,
            "textColor": text_color_set,
            "text": text,
            "stroke": stroke
        }

        label = DisplayLabel(
            layout = layout_def_1,
            bounds = DisplayBounds(x, y, w, h)
        )

        ui = MockDisplaySplash()
        u = Updater()
        u.low_memory_warning = False

        label.init(ui, u)
        
        index = 0

        if fill:
            rect = ui.splash[index]
            index += 1

            self.assertIsInstance(rect, MockDisplayShapes.rect.Rect)

            self.assertEqual(rect.x, x + stroke)
            self.assertEqual(rect.y, y + stroke)
            self.assertEqual(rect.width, w - stroke * 2)
            self.assertEqual(rect.height, h - stroke * 2)
            self.assertEqual(rect.fill, fill)
            self.assertEqual(rect.outline, None)
            self.assertEqual(rect.stroke, 0)
            
        group = ui.splash[index]
        label = ui.splash[index].mock_content[0]

        self.assertIsInstance(group, MockDisplayIO.Group)
        self.assertIsInstance(label, MockAdafruitDisplayText.label.Label)

        self.assertEqual(group.x, x)
        self.assertEqual(group.y, y)
        self.assertEqual(group.scale, 1)

        self.assertEqual(label.text, text)
        self.assertEqual(label.color, text_color_exp)


###############################################################################################


    def test_properties_uninitialized(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "maxTextWidth": 222,
                "lineSpacing": 0.6,
                "text": "footext",
                "textColor": (2, 3, 4),
                "backColor": (20, 30, 40),
                "stroke": 4
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        # Must not throw without init being called before
        label.layout = DisplayLabelLayout({
            "font": "foo2",
            "maxTextWidth": 212,
            "lineSpacing": 0.5,
            "text": "footext2",
            "textColor": (1, 3, 4),
            "backColor": (21, 30, 40),
            "stroke": 5
        })


###############################################################################################


    def test_back_color(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "backColor": (3, 4, 6)
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        self.assertEqual(label.back_color, (3, 4, 6))

        label.back_color = (200, 230, 240)
        self.assertEqual(label.back_color, (200, 230, 240))

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "backColor": (3, 4, 7)
        })
        self.assertEqual(label.back_color, (3, 4, 7))

        # Check background(s)
        ui = MockDisplaySplash()
        u = Updater()
        u.low_memory_warning = False

        label.init(ui, u)
        
        self.assertEqual(ui.splash[0].fill, (3, 4, 7))

        label.back_color = (200, 230, 240)
        self.assertEqual(label.back_color, (200, 230, 240))

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "backColor": (3, 4, 7)
        })
        self.assertEqual(label.back_color, (3, 4, 7))

        self.assertEqual(ui.splash[0].fill, (3, 4, 7))


###############################################################################################


    def test_text_color(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "textColor": (3, 4, 6)
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        self.assertEqual(label.text_color, (3, 4, 6))

        label.text_color = (5, 6, 7)
        self.assertEqual(label.text_color, (5, 6, 7))

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "textColor": (3, 4, 8)
        })
        self.assertEqual(label.text_color, (3, 4, 8))

        # Check elements
        ui = MockDisplaySplash()
        u = Updater()
        u.low_memory_warning = False

        label.init(ui, u)
        
        self.assertEqual(ui.splash[0].mock_content[0].color, (3, 4, 8))

        label.text_color = None
        self.assertEqual(ui.splash[0].mock_content[0].color, (255, 255, 255))

        label.text_color = (5, 6, 7)
        self.assertEqual(label.text_color, (5, 6, 7))

        label.layout = DisplayLabelLayout({
            "font": "foo"
        })
        self.assertEqual(ui.splash[0].mock_content[0].color, (255, 255, 255))

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "textColor": (3, 4, 8)
        })
        self.assertEqual(label.text_color, (3, 4, 8))
        self.assertEqual(ui.splash[0].mock_content[0].color, (3, 4, 8))


###############################################################################################


    def test_text(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "text": "foo"
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        self.assertEqual(label.text, "foo")

        label.text = "bar"
        self.assertEqual(label.text, "bar")

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "text": "mustbeset"
        })
        self.assertEqual(label.text, "mustbeset")

        # Check elements
        ui = MockDisplaySplash()
        u = Updater()
        u.low_memory_warning = False

        label.init(ui, u)
        
        self.assertEqual(ui.splash[0].mock_content[0].text, "mustbeset")

        label.text = "foo"
        self.assertEqual(label.text, "foo")
        self.assertEqual(ui.splash[0].mock_content[0].text, "foo")

        label.text = "bar1"
        self.assertEqual(label.text, "bar1")
        self.assertEqual(ui.splash[0].mock_content[0].text, "bar1")

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "text": "mustnotbeset"
        })
        self.assertEqual(label.text, "bar1")
        self.assertEqual(ui.splash[0].mock_content[0].text, "bar1")


    def test_text_wrapped(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "text": "foo",
                "maxTextWidth": 12
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        # Check elements
        ui = MockDisplaySplash()
        u = Updater()
        u.low_memory_warning = False

        label.init(ui, u)
        
        self.assertEqual(ui.splash[0].mock_content[0].text, "foo\n(wrapped to 12 and font 'foo')")

        label.text = "bar1"
        self.assertEqual(label.text, "bar1")
        self.assertEqual(ui.splash[0].mock_content[0].text, "bar1\n(wrapped to 12 and font 'foo')")

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "text": "mustnotbeset"
        })
        self.assertEqual(label.text, "bar1")
        self.assertEqual(ui.splash[0].mock_content[0].text, "bar1")

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "text": "mustnotbeset",
            "maxTextWidth": 22
        })
        self.assertEqual(label.text, "bar1")
        self.assertEqual(ui.splash[0].mock_content[0].text, "bar1\n(wrapped to 22 and font 'foo')")


    def test_text_low_memory_warning(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "text": "foo"
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        ui = MockDisplaySplash()
        u = Updater()
        u.low_memory_warning = True

        label.init(ui, u)
        
        self.assertIn("Memory", ui.splash[0].mock_content[0].text)
        self.assertIn("Memory", label.text)

        label.text = "foo2"
        self.assertIn("Memory", ui.splash[0].mock_content[0].text)
        self.assertIn("Memory", label.text)
        
