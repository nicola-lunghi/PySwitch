import time as orig_time


class MockMicropython:
    def const(a):
        return a

class MockTime:
    mock = {
        "monotonicReturn": 0,
        "localtimeReturn": 0
    }

    def monotonic():
        return MockTime.mock["monotonicReturn"]

    def localtime():
        return MockTime.mock["localtimeReturn"]
    
    struct_time = orig_time.struct_time


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

class MockAdafruitMIDIProgramChange:
    class ProgramChange:
        def __init__(self, patch = 0):
            self.patch = patch

class MockAdafruitMIDISystemExclusive:    
    class SystemExclusive:
        def __init__(self, manufacturer_id = [0x00, 0x00, 0x00], data = []):
            self.manufacturer_id = manufacturer_id
            self.data = data

#class MockAdafruitMIDIStart:
#    class Start:
#        pass
    

class MockAdafruitMIDIMessage:
    class MIDIUnknownEvent:
        def __init__(self, status = 0):
            self.status = status

    class MIDIMessage:
        @staticmethod
        def register_message_type():
            pass


class MockGC:
    class MockData:
        def __init__(self):
            self.reset()

        def reset(self):
            self.collect_calls = 0
            self._output_mem_free = 1024 * 20  # 20kB
            self.output_mem_alloc = 0

        @property
        def output_mem_free(self):
            return self._output_mem_free
        
        @output_mem_free.setter
        def output_mem_free(self, value):
            # Shall not be lower than 20k
            if value < 1024 * 20:
                value = 1024 * 20

            self._output_mem_free = value

        def output_mem_free_override(self, value):
            self._output_mem_free = value

    def __init__(self):
        self.mock = MockGC.MockData()

    def gc_mock_data(self):
        return self.mock

    def collect(self):
        self.mock.collect_calls += 1

    def mem_free(self):
        return self.mock.output_mem_free

    def mem_alloc(self):
        return self.mock.output_mem_alloc


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
            def __init__(self, font = None, anchor_point = None, anchored_position = None, text = None, color = None, line_spacing = None, scale = 1):
                self.font = font
                self.anchor_point = anchor_point
                self.anchored_position = anchored_position
                self.text = text
                self.color = color
                self.line_spacing = line_spacing
                self.scale = scale

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
            def __init__(self, x = 0, y = 0, width = 0, height = 0, fill = None, outline = None, stroke = 0):
                self.x = x 
                self.y = y
                self.width = width
                self.height = height
                self.fill = fill 
                self.outline = outline
                self.stroke = stroke

    #class roundrect:
    #    class RoundRect:
    #        def __init__(self, x = 0, y = 0, width = 0, height = 0, fill = None, outline = None, stroke = 0, r = 0):
    #            self.x = x 
    #            self.y = y
    #            self.width = width
    #            self.height = height
    #            self.fill = fill 
    #            self.outline = outline
    #            self.stroke = stroke
    #            self.r = r

    #class circle:
    #    class Circle:
    #        def __init__(self, x0 = 0, y0 = 0, r = 0, fill = None):
    #            self.x0 = x0 
    #            self.y0 = y0
    #            self.fill = fill 
    #            self.r = r


class MockMidiBridge:
    class PyMidiBridge:
        def __init__(self, midi, storage, event_handler = None, read_chunk_size = 1024):
            self.messages_received = []

        def receive(self, msg):
            self.messages_received.append(msg)


class MockOs:
        
    RENAME_CALLS = []
    STAT_SIZE_OUTPUTS = {}

    def rename(source, target):
        MockOs.RENAME_CALLS.append({
            "source": source,
            "target": target
        })

    class _StatMock:
        def __init__(self, output):
            self.st_size = output

    def stat(path):
        return MockOs._StatMock(MockOs.STAT_SIZE_OUTPUTS[path] if path in MockOs.STAT_SIZE_OUTPUTS else -1)
