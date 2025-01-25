import unittest
import sys
from unittest.mock import patch

from mocks import *

with patch.dict(sys.modules, {
	"micropython": MockMicropython,
	"gc": MockGC(),
	"board": MockBoard,
    "adafruit_midi": MockAdafruitMIDI(),
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.program_change": MockAdafruitMIDIProgramChange(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
}):
	import pyswitch.process