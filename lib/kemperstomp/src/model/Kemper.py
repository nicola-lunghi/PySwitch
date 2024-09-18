from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive

from .KemperNRPNMessage import KemperNRPNMessage
from ..Tools import Tools
from ...config import Config
from ...definitions import KemperMidi

# Implements all MIDI communication to and from the Kemper
class Kemper:

    def __init__(self, midi):
        self._midi = midi        
        
    # Sends the SET message of a mapping
    def set(self, mapping, value):
        if mapping.set == None:
            raise Exception("No SET message prepared for this MIDI mapping")
        
        if isinstance(mapping.set, ControlChange):
            # Set value
            mapping.set.value = value

        if isinstance(mapping.set, SystemExclusive):
            raise Exception("Setting Kemper parameters by SysEx is not implemented yet")

        if isinstance(mapping.set, KemperNRPNMessage):
            raise Exception("Setting Kemper parameters by NRPN is not implemented yet")
        
        self._print("Send SET message: " + Tools.stringify_midi_message(mapping.set))

        self._midi.send(mapping.set)

    # Send the request message of a mapping
    def request(self, mapping):
        if mapping.request == None:
            raise Exception("No REQUEST message prepared for this MIDI mapping")
        
        if mapping.response == None:
            raise Exception("No response template message prepared for this MIDI mapping")
        
        if isinstance(mapping.request, ControlChange):
            raise Exception("Parameter requests do not work with ControlChange. Use KemperNRPNMessage (or SystemExclusive) instead.")

        self._print(" -> Send REQUEST message: " + Tools.stringify_midi_message(mapping.request))

        self._midi.send(mapping.request)

    # Parses an incoming MIDI message. If the message belongs to the mapping's request,
    # returns the received value. If not, returns None.
    def parse(self, mapping, midi_message):
        if mapping.response == None:
            raise Exception("No response template message prepared for this MIDI mapping")

        if not isinstance(midi_message, SystemExclusive):
            return None

        if not isinstance(mapping.response, SystemExclusive):
            return None
        
        # Compare manufacturer IDs
        if midi_message.manufacturer_id != mapping.response.manufacturer_id:
            return None

        #self._print("RAW Receive : " + Tools.stringify_midi_message(midi_message))
        #self._print("RAW Template: " + Tools.stringify_midi_message(mapping.response))

        # Get data as integer list from both the incoming message and the response
        # template in the mapping
        response = list(midi_message.data)                        
        template = list(mapping.response.data)        

        # The first two values are ignored (the Kemper MIDI specification implies this would contain the product type
        # and device ID as for the request, however the device just sends two zeroes)

        # Check if the message belongs to the mapping. The following have to match:
        #   2: function code, 
        #   3: instance ID, 
        #   4: address page, 
        #   5: address nunber
        if response[2:6] != template[2:6]:
            return None
        
        # The values starting from index 6 are the value of the response.
        if mapping.type == KemperMidi.NRPN_PARAMETER_TYPE_STRING:
            # Take as string
            value = ''.join(chr(int(c)) for c in response[6:-1])
        else:
            # Decode 14-bit value to int
            value = response[-2] * 128 + response[-1]
        
        self._print("   -> Received value " + repr(value) + ": " + Tools.stringify_midi_message(midi_message))

        return value
            
    # Debug console output
    def _print(self, msg):
        if Tools.get_option(Config, "debugKemper") != True:
            return
        
        Tools.print("Kemper: " + msg)