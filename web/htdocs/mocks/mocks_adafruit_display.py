from adafruit_bitmap_font import bitmap_font


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

