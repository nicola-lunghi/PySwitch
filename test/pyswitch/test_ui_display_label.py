import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

with patch.dict(sys.modules, {
    "displayio": MockDisplayIO(),
    "adafruit_display_text": MockAdafruitDisplayText(),
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


class CheckAreaColors:
    def __init__(self, testcase):
        self.case = testcase

    # Checks if the passed parts (rects or round rects) fill up the area completely,
    # split in rows
    def run(self, area, parts, colors):
        part_height = int(area.height / len(colors))

        # Check one pixel in the middle of each expected color area
        for i in range(len(colors)):
            x = area.x + int(area.width / 2)
            y = int(part_height / 2) + i * part_height

            exp_color = colors[i]
            act_color = self._render_color(parts, x, y)

            self.case.assertEqual(act_color, exp_color)

    # Returns the color at a given pixel position
    def _render_color(self, parts, x, y):
        ret = None
        
        for part in parts:
            if (part.x <= x and part.x + part.width >= x and
                part.y <= y and part.y + part.height >= y):
                
                ret = part.fill

        return ret


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
            "cornerRadius": 3,
            "stroke": 4
        }

        layout_def_2 = {
            "font": "bar",
            "maxTextWidth": 223,
            "lineSpacing": 0.7,
            "text": "bartext",
            "textColor": (3, 4, 5),
            "backColor": (30, 40, 50),
            "cornerRadius": 3,
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

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect()
        }):
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
                    "cornerRadius": 0,
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
                a.corner_radius == b.corner_radius and 
                a.stroke == b.stroke)
    
    
    #def _stringify_layout(self, layout):
    #    return repr(layout.__dict__)
    

###############################################################################################


    def test_label(self):
        self._test_label(20, 21, 200, 210, None, 0, 0, "hey", (255, 255, 255), None)
        self._test_label(20, 21, 200, 210, None, 0, 0, "hey", (200, 255, 255), (200, 255, 255))

        self._test_label(20, 21, 200, 210, (3, 4, 5), 0, 0, "hey", (255, 200, 255), (255, 200, 255))
        self._test_label(20, 21, 200, 210, (3, 4, 5), 3, 0, "", (255, 255, 255), None)
        self._test_label(20, 21, 200, 210, (3, 4, 5), 0, 2, "bar", (255, 255, 200), (255, 255, 200))
        self._test_label(20, 21, 200, 210, (3, 4, 5), 6, 3, "foo", (255, 255, 255), None)

        self._test_label(20, 21, 200, 210, (200, 240, 250), 6, 3, "foo", (0, 0, 0), None)
        self._test_label(20, 21, 200, 210, (200, 140, 250), 6, 3, "foo", (0, 0, 0), None)
        self._test_label(20, 21, 200, 210, (0, 0, 0), 6, 3, "foo", (255, 255, 255), None)
        self._test_label(20, 21, 200, 210, (30, 50, 100), 6, 3, "foo", (255, 255, 255), None)

        # 2 back colors
        self._test_label(0, 0, 250, 250, ((3, 4, 5), (6, 7, 8)), 0, 0, "hey", (255, 255, 255), None)
        self._test_label(0, 0, 250, 250, ((200, 200, 220), (6, 7, 8)), 0, 0, "hey", (0, 0, 0), None)

        self._test_label(0, 0, 250, 250, ((3, 4, 5), (6, 7, 8)), 2, 0, "hey", (255, 255, 255), None)
        self._test_label(0, 0, 250, 250, ((200, 200, 220), (6, 7, 8)), 0, 4, "hey", (0, 0, 0), None)
        self._test_label(0, 0, 250, 250, ((200, 200, 220), (200, 244, 233)), 6, 4, "hey", (0, 0, 0), None)

        # 3 back colors
        self._test_label(0, 0, 250, 250, ((3, 4, 5), (6, 7, 8), (9, 10, 11)), 0, 0, "hey", (255, 255, 255), None)
        self._test_label(0, 0, 250, 250, ((200, 200, 220), (6, 7, 8), (9, 10, 11)), 0, 0, "hey", (0, 0, 0), None)

        self._test_label(0, 0, 250, 250, ((3, 4, 5), (6, 7, 8), (9, 10, 11)), 2, 0, "hey", (255, 255, 255), None)
        self._test_label(0, 0, 250, 250, ((3, 4, 5), (6, 7, 8), (200, 200, 220)), 0, 4, "hey", (0, 0, 0), None)
        self._test_label(0, 0, 250, 250, ((200, 200, 220), (200, 244, 233), (9, 10, 11)), 6, 4, "hey", (0, 0, 0), None)

        # 4 back colors
        self._test_label(0, 0, 250, 250, ((3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14)), 0, 0, "hey", (255, 255, 255), None)
        self._test_label(0, 0, 250, 250, ((200, 200, 220), (6, 7, 8), (9, 10, 11), (12, 13, 14)), 0, 0, "hey", (0, 0, 0), None)

        self._test_label(0, 0, 250, 250, ((3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14)), 2, 0, "hey", (255, 255, 255), None)
        self._test_label(0, 0, 250, 250, ((3, 4, 5), (6, 7, 8), (200, 200, 220), (12, 13, 14)), 0, 4, "hey", (0, 0, 0), None)
        self._test_label(0, 0, 250, 250, ((200, 200, 220), (200, 244, 233), (9, 10, 11), (12, 13, 14)), 6, 4, "hey", (0, 0, 0), None)


    def _test_label(self, x, y, w, h, fill, corner_radius, stroke, text, text_color_exp, text_color_set):
        layout_def_1 = {
            "font": "foo",
            "backColor": fill,
            "textColor": text_color_set,
            "cornerRadius": corner_radius,
            "text": text,
            "stroke": stroke
        }

        label = DisplayLabel(
            layout = layout_def_1,
            bounds = DisplayBounds(x, y, w, h)
        )

        ui = MockDisplaySplash()
        u = Updater()

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect()
        }):            
            label.init(ui, u)
            
            index = 0

            if fill and isinstance(fill[0], tuple):
                area_parts = []
                for i in range(len(fill)):
                    rect = ui.splash[index]
                    index += 1
                    area_parts.append(rect)

                check = CheckAreaColors(self)
                check.run(DisplayBounds(x, y, w, h), area_parts, fill)

            elif fill: # Single back color
                rect = ui.splash[index]
                index += 1

                self.assertIsInstance(rect, MockDisplayShapes.rect.Rect if corner_radius == 0 else MockDisplayShapes.roundrect.RoundRect)

                self.assertEqual(rect.x, x)
                self.assertEqual(rect.y, y)
                self.assertEqual(rect.width, w)
                self.assertEqual(rect.height, h)
                self.assertEqual(rect.fill, fill)
                self.assertEqual(rect.outline, None)
                self.assertEqual(rect.stroke, 0)

                if corner_radius > 0:
                    self.assertEqual(rect.r, corner_radius)

            if stroke > 0:
                frame = ui.splash[index]
                index += 1

                self.assertIsInstance(frame, MockDisplayShapes.rect.Rect if corner_radius == 0 else MockDisplayShapes.roundrect.RoundRect)    

                self.assertEqual(frame.x, x)
                self.assertEqual(frame.y, y)
                self.assertEqual(frame.width, w)
                self.assertEqual(frame.height, h)
                self.assertEqual(frame.fill, None)
                self.assertEqual(frame.outline, (0, 0, 0))
                self.assertEqual(frame.stroke, stroke)

                if corner_radius > 0:
                    self.assertEqual(frame.r, corner_radius)                

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
                "cornerRadius": 3,
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
            "cornerRadius": 3,   # Cannot be changed
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

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect()
        }):            
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


    def test_back_two_colors(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "backColor": ((3, 4, 6), (7, 8, 9))
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        self.assertEqual(label.back_color, ((3, 4, 6), (7, 8, 9)))

        label.back_color = ((200, 230, 240), (30, 40, 50))
        self.assertEqual(label.back_color, ((200, 230, 240), (30, 40, 50)))

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "backColor": ((3, 4, 7), (6, 7, 8))
        })
        self.assertEqual(label.back_color,((3, 4, 7), (6, 7, 8)))

        # Check background(s)
        ui = MockDisplaySplash()
        u = Updater()

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect()
        }):            
            label.init(ui, u)
            
            self.assertEqual(ui.splash[0].fill, (3, 4, 7))
            self.assertEqual(ui.splash[1].fill, (6, 7, 8))

            label.back_color = ((200, 230, 240), (30, 40, 50))
            self.assertEqual(label.back_color, ((200, 230, 240), (30, 40, 50)))

            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": ((3, 4, 7), (6, 7, 8))
            })
            self.assertEqual(label.back_color,((3, 4, 7), (6, 7, 8)))

            self.assertEqual(ui.splash[0].fill, (3, 4, 7))
            self.assertEqual(ui.splash[1].fill, (6, 7, 8))


    def test_three_back_colors(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "backColor": ((3, 4, 6), (7, 8, 9), (10, 11, 12))
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        self.assertEqual(label.back_color, ((3, 4, 6), (7, 8, 9), (10, 11, 12)))

        label.back_color = ((200, 230, 240), (30, 40, 50), (12, 12, 12))
        self.assertEqual(label.back_color, ((200, 230, 240), (30, 40, 50), (12, 12, 12)))

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "backColor": ((3, 4, 7), (6, 7, 8), (12, 12, 11))
        })
        self.assertEqual(label.back_color, ((3, 4, 7), (6, 7, 8), (12, 12, 11)))

        # Check background(s)
        ui = MockDisplaySplash()
        u = Updater()

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect()
        }):            
            label.init(ui, u)
            
            parts = [
                ui.splash[0],
                ui.splash[1],
                ui.splash[2]
            ]

            label.back_color = ((200, 230, 240), (30, 40, 50), (12, 12, 12))
            self.assertEqual(label.back_color, ((200, 230, 240), (30, 40, 50), (12, 12, 12)))

            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": ((3, 4, 7), (6, 7, 8), (12, 12, 13))
            })
            self.assertEqual(label.back_color, ((3, 4, 7), (6, 7, 8), (12, 12, 13)))

            check = CheckAreaColors(self)
            check.run(DisplayBounds(20, 21, 200, 210), parts, ((3, 4, 7), (6, 7, 8), (12, 12, 13)))
            
    
    def test_back_color_errors_no_color(self):
        label = DisplayLabel(
            layout = {
                "font": "foo"
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        # Must not throw
        label.back_color = None

        label.layout = DisplayLabelLayout({
            "font": "foo2"
        })

        with self.assertRaises(Exception):            
            label.back_color = (200, 230, 240)

        with self.assertRaises(Exception):            
            label.back_color = ((200, 230, 240), (3, 4, 5))

        with self.assertRaises(Exception):            
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": (3, 4, 7)
            })
        
        with self.assertRaises(Exception):            
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": ((200, 230, 240), (3, 4, 5))
            })


    def test_back_color_errors_one_color(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "backColor": (2, 3, 4)
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        with self.assertRaises(Exception):            
            label.back_color = None

        with self.assertRaises(Exception):            
            label.back_color = [(3, 4, 5)]

        with self.assertRaises(Exception):            
            label.back_color = ((3, 4, 5), (6, 7 ,8))

        with self.assertRaises(Exception):            
            label.layout = DisplayLabelLayout({
                "font": "foo"
            })

        with self.assertRaises(Exception):            
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": ((200, 230, 240))
            })

        with self.assertRaises(Exception):            
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": ((200, 230, 240), (3, 4, 5))
            })


    def test_back_color_errors_three_colors(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "backColor": ((2, 3, 4), (6, 3, 7), (3, 4, 5))
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        with self.assertRaises(Exception):            
            label.back_color = None

        with self.assertRaises(Exception):            
            label.back_color = (6, 7, 8)

        with self.assertRaises(Exception):            
            label.back_color = [(3, 4, 5)]

        with self.assertRaises(Exception):            
            label.back_color = ((3, 4, 5), (6, 7 ,8))

        with self.assertRaises(Exception):            
            label.back_color = ((3, 4, 5), (6, 7 ,8), (3, 4, 5), (6, 7 ,8))

        with self.assertRaises(Exception):            
            label.layout = DisplayLabelLayout({
                "font": "foo"
            })

        with self.assertRaises(Exception):            
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": (200, 230, 240)
            })

        with self.assertRaises(Exception):            
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": [(200, 230, 240)]
            })

        with self.assertRaises(Exception):            
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": ((200, 230, 240), (3, 4, 5))
            })

        with self.assertRaises(Exception):            
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": ((200, 230, 240), (3, 4, 5), (200, 230, 240), (3, 4, 5))
            })


###############################################################################################


    def test_corner_radius(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "backColor": (3, 4, 6),
                "cornerRadius": 3
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        self.assertEqual(label.corner_radius, 3)

        with self.assertRaises(Exception):
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": (3, 4, 6),
                "cornerRadius": 5
            })

        # Check elements
        ui = MockDisplaySplash()
        u = Updater()

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect()
        }):            
            label.init(ui, u)
            
            self.assertEqual(ui.splash[0].r, 5)


    def test_corner_radius_errors(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "backColor": (3, 4, 6)
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        self.assertEqual(label.corner_radius, 0)

        with self.assertRaises(Exception):
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": (3, 4, 6),
                "cornerRadius": 5
            })


###############################################################################################


    def test_stroke(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "backColor": (3, 4, 6),
                "stroke": 3
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        self.assertEqual(label.stroke, 3)

        label.stroke = 7
        self.assertEqual(label.stroke, 7)

        label.layout = DisplayLabelLayout({
            "font": "foo",
            "backColor": (3, 4, 6),
            "stroke": 5
        })
        self.assertEqual(label.stroke, 5)

        # Check elements
        ui = MockDisplaySplash()
        u = Updater()

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect()
        }):            
            label.init(ui, u)
            
            self.assertEqual(ui.splash[1].stroke, 5)

            label.stroke = 7
            self.assertEqual(label.stroke, 7)

            label.stroke = 7
            self.assertEqual(label.stroke, 7)

            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": (3, 4, 6),
                "stroke": 5
            })
            self.assertEqual(label.stroke, 5)

            self.assertEqual(ui.splash[1].stroke, 5)

            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": (3, 4, 6),
                "stroke": 5
            })
            self.assertEqual(label.stroke, 5)


    def test_stroke_errors_with_stroke(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "backColor": (3, 4, 6),
                "stroke": 3
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        with self.assertRaises(Exception):
            label.stroke = 0

        with self.assertRaises(Exception):
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": (3, 4, 6),
                "stroke": 0
            })


    def test_stroke_errors_no_stroke(self):
        label = DisplayLabel(
            layout = {
                "font": "foo",
                "backColor": (3, 4, 6)
            },
            bounds = DisplayBounds(20, 21, 200, 210)
        )

        with self.assertRaises(Exception):
            label.stroke = 3

        with self.assertRaises(Exception):
            label.layout = DisplayLabelLayout({
                "font": "foo",
                "backColor": (3, 4, 6),
                "stroke": 3
            })


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

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect()
        }):            
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

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect()
        }):            
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

        with patch.dict(sys.modules, {
            "adafruit_display_shapes.rect": MockDisplayShapes().rect(),
            "adafruit_display_shapes.roundrect": MockDisplayShapes().roundrect()
        }):            
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



