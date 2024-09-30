from adafruit_bitmap_font import bitmap_font


# Buffered font loader
class AdafruitFontLoader:
    _fonts = {}

    # Returns a font (buffered)
    def get(self, path):
        if path in self._fonts:
            return self._fonts[path]
        
        font = bitmap_font.load_font(path)
        self._fonts[path] = font

        return font
