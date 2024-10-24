
class MockTime:
    mock = {
        "monotonicReturn": 0
    }

    def monotonic():
        return MockTime.mock["monotonicReturn"]


class MockUsbMidi:
    ports = [None, None]


class MockAdafruitMIDI:
    class MIDI:
        def __init__(self, midi_out = None, out_channel = None, midi_in = None, in_buf_size = None, debug = None):
            self.midi_out = midi_out
            self.midi_in = midi_in
            self.out_channel = out_channel
            self.in_buf_size = in_buf_size
            self.debug = debug

            self.messages_sent = []
            self.next_receive_messages = []

        def receive(self):
            if self.next_receive_messages:
                return self.next_receive_messages.pop(0)
            
            return None
        
        def send(self, midi_message):
            self.messages_sent.append(midi_message)
            

class MockAdafruitMIDIControlChange:
    class ControlChange:
        def __init__(self, control = 0, value = 0):
            self.control = control
            self.value = value


class MockAdafruitMIDISystemExclusive:    
    class SystemExclusive:
        def __init__(self, manufacturer_id = [0x00, 0x00, 0x00], data = []):
            self.manufacturer_id = manufacturer_id
            self.data = data


class MockGC:
    mock = {
        "collectCalls": 0,
        "memFreeReturn": 0,
        "memAllocReturn": 0
    }

    @staticmethod
    def collect():
        MockGC.mock["collectCalls"] += 1

    @staticmethod
    def mem_free():
        return MockGC.mock["memFreeReturn"]

    @staticmethod
    def mem_alloc():
        return MockGC.mock["memAllocReturn"]


class MockDisplayIO:
    class Group:
        def __init__(self, scale = 1, x = 0, y = 0):
            self.scale = scale
            self.x = x
            self.y = y

            self.mock_content = []

        def append(self, el):
            self.mock_content.append(el)

    #class FourWire:
    #    def __init__(self, spi, command, chip_select, reset):
    #        self.spi = spi
    #        self.command = command
    #        self.chip_select = chip_select
    #        self.reset = reset

        
class MockAdafruitDisplayText:
    class label:
        class Label:
            def __init__(self, font = None, anchor_point = None, anchored_position = None, text = None, color = None, line_spacing = None):
                self.font = font
                self.anchor_point = anchor_point
                self.anchored_position = anchored_position
                self.text = text
                self.color = color
                self.line_spacing = line_spacing

    def wrap_text_to_pixels(self, text, text_width, font):
        return [
            text,
            "(wrapped to " + repr(text_width) + " and font " + repr(font) + ")"
        ]
    

#class MockBitmapFont:
#    class MockFont:
#        def __init__(self, path):
#            self.path = path

#    class bitmap_font:
#        def load_font(self, path):
#            return self.MockFont(path)
        

class MockBoard:
    some_other = "nothing_of_interest"

    GP4 = "MockPort_4"
    GP6 = "MockPort_6"
    GP11 = "MockPort_11"
    GP23 = "MockPort_23"


#class MockBusIO:
#    class SPI:
#        def __init__(self, spi_clk, MOSI):
#            self.spi_clk = spi_clk
#            self.MOSI = MOSI


#class MockST7789:
#   class ST7789:
#        def __init__(self, display_bus, width, height, rowstart, rotation):
#            self.display_bus = display_bus
#            self.width = width
#            self.height = height
#            self.rowstart = rowstart
#            self.rotation = rotation


class MockDisplayShapes:
    class rect:
        class Rect:
            def __init__(self, x = 0, y = 0, w = 0, h = 0, fill = None, outline = None, stroke = 0):
                self.x = x 
                self.y = y
                self.width = w
                self.height = h
                self.fill = fill 
                self.outline = outline
                self.stroke = stroke

    class roundrect:
        class RoundRect:
            def __init__(self, x = 0, y = 0, w = 0, h = 0, fill = None, outline = None, stroke = 0, r = 0):
                self.x = x 
                self.y = y
                self.width = w
                self.height = h
                self.fill = fill 
                self.outline = outline
                self.stroke = stroke
                self.r = r

