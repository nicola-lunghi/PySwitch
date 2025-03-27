from adafruit_midi.midi_message import MIDIUnknownEvent
from adafruit_midi.control_change import ControlChange
from adafruit_midi.program_change import ProgramChange
from adafruit_midi.system_exclusive import SystemExclusive

# Compare two MIDI messages
def compare_midi_messages(a, b):
    if isinstance(a, SystemExclusive) and isinstance(b, SystemExclusive):
        return a.data == b.data and a.manufacturer_id == b.manufacturer_id

    elif isinstance(a, ControlChange) and isinstance(b, ControlChange):
        return a.control == b.control
    
    elif isinstance(a, ProgramChange) and isinstance(b, ProgramChange):
        return a.patch == b.patch

    elif isinstance(a, MIDIUnknownEvent) and isinstance(b, MIDIUnknownEvent):
        return a.status == b.status

    else:
        return a == b
