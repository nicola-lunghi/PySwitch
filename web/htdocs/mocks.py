
class MockMicropython:
    def const(a):
        return a

        
class MockGC:
    def collect(self):
        pass

    def mem_free(self):
        return 0

    def mem_alloc(self):
        return 0
        
        
class MockAdafruitMIDI:
    class MIDI:
        def __init__(self, midi_out = None, out_channel = None, midi_in = None, in_buf_size = None, debug = None):
            self.midi_out = midi_out
            self.midi_in = midi_in
            self.out_channel = out_channel
            self.in_buf_size = in_buf_size

        def receive(self):
            return None
        
        def send(self, midi_message):
            pass
            

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


class MockAdafruitMIDIMessage:
    class MIDIUnknownEvent:
        def __init__(self, status = 0):
            self.status = status

    class MIDIMessage:
        @staticmethod
        def register_message_type():
            pass
            
            
class MockBoard:
    GP4 = "MockPort_4"
    GP6 = "MockPort_6"
    GP11 = "MockPort_11"
    GP23 = "MockPort_23"


 