# import sys
# from unittest.mock import patch

# from mocks.mocks_adafruit import *

# class MockAdafruitDisplayTextInternal:
#     pass

# with patch.dict(sys.modules, {
#     "displayio": MockDisplayIO(),
#     "fontio": MockFontIO(),
# }):
#     from .adafruit.adafruit_display_text.label import Label as _Label
#     from .adafruit.adafruit_display_text import wrap_text_to_pixels as _wrap_text_to_pixels


# class MockAdafruitDisplayText:
#     class label:
#         Label = _Label

#     def wrap_text_to_pixels(self, text, text_width, font):
#         return _wrap_text_to_pixels(text, text_width, font)
    

# class MockAdafruitDisplayText:
#     class label:
#         class Label:
#             def __init__(self, font = None, anchor_point = None, anchored_position = None, text = None, color = None, line_spacing = None, scale = 1):
#                 self.font = font
#                 self.anchor_point = anchor_point
#                 self.anchored_position = anchored_position
#                 self.text = text
#                 self.color = color
#                 self.line_spacing = line_spacing
#                 self.scale = scale

#             def render(self, canvas, x, y):
#                 pass
#                 #ctx = canvas.getContext('2d')
#                 #ctx.fillStyle = "red"
#                 #ctx.fillRect(
#                 #    self.x,
#                 #    self.y,
#                 #    self.width,
#                 #    self.height
#                 #)

#     def wrap_text_to_pixels(self, text, text_width, font):
#         return [
#             text,
#             "(wrapped to " + repr(text_width) + " and font " + repr(font) + ")"
#         ]
    

class MockDisplayShapes:
    class rect:
        class Rect:
            def __init__(self, x = 0, y = 0, width = 0, height = 0, fill = None): #, outline = None, stroke = 0):
                self.x = x 
                self.y = y
                self.width = width
                self.height = height
                self.fill = fill 
                #self.outline = outline
                #self.stroke = stroke

            def render(self, canvas, x, y):
                ctx = canvas.getContext('2d')
                ctx.fillStyle = "red" #f"rgb({ self.fill[0] }, { self.fill[1] }, { self.fill[2] })"
                ctx.fillRect(
                    self.x + x,
                    self.y + y,
                    self.width,
                    self.height
                )


# Buffered font loader
class MockAdafruitFontLoader:
    __fonts = {}

    # Returns a font (buffered)
    def get(self, path):
        if path in self.__fonts:
            return self.__fonts[path]
        
        font = bitmap_font.load_font(path)
        self.__fonts[path] = font

        return font

