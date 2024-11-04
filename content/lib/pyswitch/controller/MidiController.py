from ..misc import Tools

from adafruit_midi.midi_message import MIDIUnknownEvent

# Describes a routing from source to target, which must be MidiDevices definitions.
class MidiRouting:
    def __init__(self, source, target):
        # Source MIDI device (can be either a AdafruitXXXMidiDevice or 
        # MidiController.PYSWITCH for the application itself)
        self.source = source    

        # Target MIDI device (can be either a AdafruitXXXMidiDevice or 
        # MidiController.PYSWITCH for the application itself)
        self.target = target    
        

##################################################################################################


# MIDI Communication wrapper
class MidiController:

    # Used as source/target for routings to/from the application itself
    PYSWITCH = "pyswitch"

    def __init__(self, config, debug = False):
        self._config = config
        self._debug = debug
        self._routings = Tools.get_option(self._config, "routings", [])

    def send(self, midi_message):
        # Send to all routings which have PYSWITCH as source
        for r in self._routings:
            if r.source == self.PYSWITCH:
                if self._debug:
                    self._print("Send " + Tools.stringify_midi_message(midi_message) + " to " + repr(r.target))

                r.target.send(midi_message)

    def receive(self):
        # Process routings without PYSWITCH involved
        for r in self._routings:
            if r.target == self.PYSWITCH or r.source == self.PYSWITCH:
                continue

            msg = r.source.receive()
            if msg:
                if isinstance(msg, MIDIUnknownEvent):
                    continue
            
                if self._debug:
                    self._print("Forwarding " + Tools.stringify_midi_message(msg) + " from " + repr(r.source) + " to " + repr(r.target))

                r.target.send(msg)

        # Process routings targeting PYSWITCH
        for r in self._routings:
            if r.target != self.PYSWITCH:
                continue

            msg = r.source.receive()

            if msg:
                # Return first message for PYSWITCH in the queue
                if self._debug:
                    self._print("Received " + Tools.stringify_midi_message(msg) + " from " + repr(r.source))

                return msg                
    
    def _print(self, msg):
        Tools.print("MIDI " + msg)
        
        