
class MockUsbMidi:
    ports = [None, None]

class MockAdafruitMIDI:
    class MIDI:
        def __init__(self, midi_out, out_channel, midi_in, in_buf_size, debug):
            pass

        def receive(self):
            return None
        
        def send(self, midi_message):
            pass
            
class MockAdafruitMIDIControlChange:    
    class ControlChange:
        def __init__(self, control, value):
            self.control = control
            self.value = value

class MockAdafruitMIDISystemExclusive:    
    class SystemExclusive:
        def __init__(self, manufacturer_id = [0x00, 0x00, 0x00], data = []):
            self.manufacturer_id = manufacturer_id
            self.data = data

class MockGC:
    def collect():
        pass

    def mem_free():
        return 0

    def mem_alloc():
        return 0


class MockDisplayIO:
    class Group:
        def __init__(self, scale = 1, x = 0, y = 0):
            self.scale = scale
            self.x = x
            self.y = y

        
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

    def wrap_text_to_pixels(text, text_width, font):
        return text + " (wrapped to " + repr(text_width) + ")"