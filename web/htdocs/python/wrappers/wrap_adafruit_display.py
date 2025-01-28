import re
from .WrapDisplayDriver import WrapTFT

class WrapDisplayIO:
    class Group(list):
        def __init__(self, x = 0, y = 0, scale = 1):
            self.x = x
            self.y = y
            self.__scale = scale

        @property
        def scale(self):        
            return self.__scale
        
        @scale.setter
        def scale(self, s):
            self.__scale = s
            
        def __add__(self, *args, **kwargs):
            return WrapDisplayIO.Group(super().__add__(*args, **kwargs))
        
        def render(self, canvas, x, y):
            for item in self:
                item.render(canvas, x + self.x, y + self.y)

    class FourWire:
        def __init__(self, spi, command, chip_select, reset):
            pass

    def release_displays():
        pass
  
  
#####################################################################################################################################


class WrapAdafruitDisplayText:
    class label:
        class Label:
            def __init__(self, font = None, anchor_point = None, anchored_position = None, text = None, color = None, line_spacing = None, scale = 1):
                self.font = font
                self.anchor_point = anchor_point
                self.anchored_position = anchored_position
                self.text = text
                self.color = color
                self.line_spacing = line_spacing
                self.scale = scale

            def render(self, canvas, x, y):
                ctx = canvas.getContext('2d')
                ctx.font = self.font.css(self.scale)
                ctx.fillStyle = _color_2_css(self.color)

                lines = self.text.splitlines()
                if len(lines) < 1: 
                    return
                
                font_size = self.font.size(self.scale)                
                line_spacing = self.line_spacing * font_size * 0.1
                height = len(lines) * font_size + (len(lines) - 1) * line_spacing
                for i in range(len(lines)):
                    line = lines[i]
                    measure = ctx.measureText(line)
                    
                    dx = self.anchor_point[0] * measure.width
                    dy = - self.anchor_point[1] * height + (i + 1) * font_size + i * line_spacing
                
                    ctx.fillText(
                        line,
                        self.anchored_position[0] + x - dx + self.font.offset_x(self.scale),
                        self.anchored_position[1] + y + dy + self.font.offset_y(self.scale)
                    )

    def __init__(self, dom_namespace):
        self.dom_namespace = dom_namespace
    
    def wrap_text_to_pixels(
        self,
        string,
        max_width,
        font = None,
        indent0 = "",   # Ignored!
        indent1 = "",   # Ignored!
    ):
        canvas = WrapTFT.get_canvas(self.dom_namespace)
        ctx = canvas.getContext('2d')
        ctx.font = font.css(1)

        words = string.split()

        out = []
        line = ""
        for word in words:
            tmp_line = line + " " + word
            width = ctx.measureText(tmp_line).width
            if width > max_width:
                out.append(line)
                line = word
            else:
                line = tmp_line

        if line:
            out.append(line)

        return out


class WrapFont:
    def __init__(self, path):
        self.path = path

    def size(self, scale = 1):
        nums = re.findall(r'\d+', self.path)
        if not nums:
            return 20 * scale
        return int(nums[0]) * scale
    
    def css(self, scale):
        return "bold " + str(self.size(scale) * 0.9) + "px \"Arial\", sans-serif"

    def offset_x(self, scale):
        return 0

    def offset_y(self, scale):
        return - self.size(scale) * 0.15   # Empirically determined offset


class WrapFontLoader:
    def get(self, path):
        return WrapFont(path)


#####################################################################################################################################


class WrapDisplayShapes:
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
                ctx.fillStyle = _color_2_css(self.fill)
                ctx.fillRect(
                    self.x + x,
                    self.y + y,
                    self.width,
                    self.height
                )


def _color_2_css(color):
    return f"rgb({ color[0] }, { color[1] }, { color[2] })"