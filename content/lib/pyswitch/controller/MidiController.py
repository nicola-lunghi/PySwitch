#from ..misc import stringify_midi_message, do_print


# MIDI Message types: These are all needed to be imported, despite not used: If not, no messages
# will go through the MIDI routings. If you encounter that messages are not forwarded, the type 
# might perhaps miss here. (not all are enabled by default to minimize RAM usage).
# If the message type (status) is not known by the adafruit_midi library at all, you can implement
# the type yourself (see MidiClockMessage below)
from adafruit_midi.midi_message import MIDIMessage
from adafruit_midi.midi_message import MIDIUnknownEvent
from adafruit_midi.control_change import ControlChange
from adafruit_midi.program_change import ProgramChange
from adafruit_midi.system_exclusive import SystemExclusive
#from adafruit_midi.mtc_quarter_frame import MtcQuarterFrame
#from adafruit_midi.channel_pressure import ChannelPressure
#from adafruit_midi.note_off import NoteOff
#from adafruit_midi.note_on import NoteOn
#from adafruit_midi.pitch_bend import PitchBend
#from adafruit_midi.timing_clock import TimingClock
#from adafruit_midi.start import Start
#from adafruit_midi.stop import Stop


# MIDI Clock custom message type
#class MidiClockMessage(MIDIMessage):
#    _STATUS = 0xF8
#    _STATUSMASK = 0xFF
#    LENGTH = 1
#    _slots = []

#MidiClockMessage.register_message_type()


##################################################################################################


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
    APPLICATION = 1

    # routings must be a list of MidiRouting instances
    def __init__(self, routings):
        self._routings_from_appl = [x for x in routings if x.source == MidiController.APPLICATION]
        self._routings_to_appl = [x for x in routings if x.target == MidiController.APPLICATION]
        self._routings_external = [x for x in routings if x.source != MidiController.APPLICATION and x.target != MidiController.APPLICATION]

    def send(self, midi_message):
        # Send to all routings which have APPLICATION as source
        for r in self._routings_from_appl:        
            #if self._debug:   # pragma: no cover
            #    self._print("Send " + stringify_midi_message(midi_message) + " to " + repr(r.target))

            r.target.send(midi_message)

    def receive(self):
        # Process routings without APPLICATION involved 
        self._process_external_routings()

        # Process routings targeting APPLICATION
        for r in self._routings_to_appl:
            msg = r.source.receive()

            if msg:
                # Return first message for APPLICATION in the queue (next ticks will deliver the next messages)
                #if self._debug:   # pragma: no cover
                #    self._print("Received " + stringify_midi_message(msg) + " from " + repr(r.source))

                return msg                
    
    # Process all routings where APPLICATION is not involved (this processes one message of each source every time)
    def _process_external_routings(self):
        routings = self._routings_external
        if not routings:
            return
        
        # Get all sources messages
        sources = []
        results = []

        for r in routings:
            if r.source in sources:
                continue

            sources.append(r.source)
            results.append(r.source.receive())
            
        # Distribute messages
        for r in routings:
            for i in range(len(sources)):
                if sources[i] != r.source:
                    continue

                msg = results[i]
        
                if not msg:
                    continue
                
                if isinstance(msg, MIDIUnknownEvent):
                    continue
                
                #if self._debug:   # pragma: no cover
                #    self._print("Forwarding " + stringify_midi_message(msg) + " from " + repr(r.source) + " to " + repr(r.target))

                r.target.send(msg)

                break

    #def _print(self, msg):  # pragma: no cover
    #    do_print("MIDI " + msg)
        
        