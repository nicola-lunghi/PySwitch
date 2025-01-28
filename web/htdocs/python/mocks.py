class MockGC:
    def collect(self):
        pass

    def mem_free(self):
        return 1024 * 1024 * 1024    # Some huge number to not get a low memory warning ;)

    def mem_alloc(self):
        return 0
        
class MockMicropython:
    def const(a):
        return a

class MockNeoPixel:
    class NeoPixel:
        pass

class MockBusIO:
    class SPI:
        def __init__(self, clk, MOSI):
            pass

        def try_lock(self):
            return True
        
        def unlock(self):
            pass
        
        def configure(self, baudrate):
            pass


class MockAdafruit_ST7789:
    class ST7789:
        def __init__(self, display_bus, width, height, rowstart, rotation):
            pass


class MockAdafruitBitmapFont:
    class bitmap_font:
        pass


class MockFontIO:
    class FontProtocol:
        pass
