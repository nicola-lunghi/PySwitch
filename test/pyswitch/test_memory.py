import sys
import unittest
from unittest.mock import patch   # Necessary workaround! Needs to be separated.

from .mocks_lib import *

# Import subject under test
with patch.dict(sys.modules, {
    "adafruit_midi.control_change": MockAdafruitMIDIControlChange(),
    "adafruit_midi.system_exclusive": MockAdafruitMIDISystemExclusive(),
    "adafruit_midi.midi_message": MockAdafruitMIDIMessage(),
    "gc": MockGC()
}):
    from .mocks_misc import MockMisc

    with patch.dict(sys.modules, {
        "lib.pyswitch.misc": MockMisc()
    }):
        
        from lib.pyswitch.Memory import Memory


class TestMemory(unittest.TestCase):

    def test_watch(self):
        MockMisc.Tools.reset()

        MockGC.mock["memFreeReturn"] = 1000
        MockGC.mock["memAllocReturn"] = 3333
        
        Memory.start("foo")
        
        self.assertEqual(len(MockMisc.Tools.msgs), 1)
        self.assertIn("foo", MockMisc.Tools.latest_msg())     
        self.assertIn(MockMisc.Tools.format_size(1000), MockMisc.Tools.latest_msg())        # Free memory
        self.assertIn(MockMisc.Tools.format_size(1000 + 3333), MockMisc.Tools.latest_msg()) # Total memory

        # Use 333 bytes
        MockGC.mock["memFreeReturn"] = 777
        
        Memory.watch("bar")
        
        self.assertEqual(len(MockMisc.Tools.msgs), 2)
        self.assertIn("bar", MockMisc.Tools.latest_msg())     
        self.assertIn("Allocated", MockMisc.Tools.latest_msg())     
        self.assertIn(MockMisc.Tools.format_size(777), MockMisc.Tools.latest_msg())            # Free memory
        self.assertIn(MockMisc.Tools.format_size(1000 - 777), MockMisc.Tools.latest_msg())     # Total memory

        # Use 0 bytes
        MockGC.mock["memFreeReturn"] = 777
        
        Memory.watch("bar2")
        
        self.assertEqual(len(MockMisc.Tools.msgs), 3)
        self.assertIn("bar2", MockMisc.Tools.latest_msg())     
        self.assertNotIn("Allocated", MockMisc.Tools.latest_msg())     
        self.assertNotIn("Released", MockMisc.Tools.latest_msg())     
        self.assertIn(MockMisc.Tools.format_size(777), MockMisc.Tools.latest_msg())            # Free memory
        self.assertNotIn(MockMisc.Tools.format_size(1000 - 777), MockMisc.Tools.latest_msg())  # Total memory

        # Free 100 bytes
        MockGC.mock["memFreeReturn"] = 877
        
        Memory.watch("bar3")
        
        self.assertEqual(len(MockMisc.Tools.msgs), 4)
        self.assertIn("bar3", MockMisc.Tools.latest_msg())     
        self.assertIn("Released", MockMisc.Tools.latest_msg())     
        self.assertIn(MockMisc.Tools.format_size(877), MockMisc.Tools.latest_msg())            # Free memory
        self.assertNotIn(MockMisc.Tools.format_size(1000 - 877), MockMisc.Tools.latest_msg())  # Total memory

