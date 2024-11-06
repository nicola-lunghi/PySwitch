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


# MIDI Communication wrapper. Can distribute/merge from/to application and external MIDI
# controllers, as defined ba routings. Remember that you have to define routes from and to
# the application manually!
class MidiController:

    # Used as source/target for routings to/from the application itself
    APPLICATION = "appl"

    # config:
    # {
    #      "routings": [                # List of routings to be performed.
    #          MidiRouting(...),
    #          ...
    #      ]
    # }
    def __init__(self, config = {}, debug = False):
        self._config = config
        self._debug = debug
        
        routings = Tools.get_option(self._config, "routings", [])

        self._routings_from_appl = [x for x in routings if x.source == MidiController.APPLICATION]
        self._routings_to_appl = [x for x in routings if x.target == MidiController.APPLICATION]
        self._routings_external = [x for x in routings if x.source != MidiController.APPLICATION and x.target != MidiController.APPLICATION]

    def send(self, midi_message):
        # Send to all routings which have APPLICATION as source
        for r in self._routings_from_appl:        
            if self._debug:   # pragma: no cover
                self._print("Send " + Tools.stringify_midi_message(midi_message) + " to " + repr(r.target))

            r.target.send(midi_message)

    def receive(self):
        # Process routings without APPLICATION involved 
        self._process_external_routings()

        # Process routings targeting APPLICATION
        for r in self._routings_to_appl:
            msg = r.source.receive()

            if msg:
                # Return first message for APPLICATION in the queue (next ticks will deliver the next messages)
                if self._debug:   # pragma: no cover
                    self._print("Received " + Tools.stringify_midi_message(msg) + " from " + repr(r.source))

                return msg                
    
    # Process all routings where APPLICATION is not involved (this processes one message of each source every time)
    def _process_external_routings(self):
        if not self._routings_external:
            return
        
        # Get all sources messages
        sources = []
        results = []

        for r in self._routings_external:
            if r.source in sources:
                continue

            sources.append(r.source)
            results.append(r.source.receive())
            
        # Distribute messages
        for r in self._routings_external:
            for i in range(len(sources)):
                if sources[i] != r.source:
                    continue

                msg = results[i]
        
                if not msg:
                    continue

                if isinstance(msg, MIDIUnknownEvent):
                    continue
                
                if self._debug:   # pragma: no cover
                    self._print("Forwarding " + Tools.stringify_midi_message(msg) + " from " + repr(r.source) + " to " + repr(r.target))

                r.target.send(msg)

                break

    def _print(self, msg):  # pragma: no cover
        Tools.print("MIDI " + msg)
        
        