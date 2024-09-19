from adafruit_midi.system_exclusive import SystemExclusive

from ...definitions import KemperMidi
from ..Tools import Tools
from ...config import Config

# Model for a request for a value
class KemperRequest:

    def __init__(self, midi, mapping):
        self.mapping = mapping        
        self._midi = midi

        if self.mapping.request == None:
            raise Exception("No REQUEST message prepared for this MIDI mapping")
        
        if self.mapping.response == None:
            raise Exception("No response template message prepared for this MIDI mapping")
        
        if not isinstance(self.mapping.request, SystemExclusive):
            raise Exception("Parameter requests do not work with ControlChange or other types. Use KemperNRPNMessage (or SystemExclusive directly) instead.")

        self._listeners = []

    # Adds a listener
    def add_listener(self, listener):
        if not isinstance(listener, KemperRequestListener):
            raise Exception("Listeners must be of type KemperRequestListener")
        
        self._listeners.append(listener)

    # Sends the request
    def send(self):
        self._print(" -> Send REQUEST message: " + Tools.stringify_midi_message(self.mapping.request))
        self._midi.send(self.mapping.request)

    # Returns if the request is finished
    def finished(self):
        return self._listeners == None

    # Parses an incoming MIDI message. If the message belongs to the mapping's request,
    # calls the listener with the received value.
    def parse(self, midi_message):
        if self.mapping.response == None:
            raise Exception("No response template message prepared for this MIDI mapping")

        if not isinstance(midi_message, SystemExclusive):
            return

        if not isinstance(self.mapping.response, SystemExclusive):
            return
        
        # Compare manufacturer IDs
        if midi_message.manufacturer_id != self.mapping.response.manufacturer_id:
            return 

        #self._print("RAW Receive : " + Tools.stringify_midi_message(midi_message))
        #self._print("RAW Template: " + Tools.stringify_midi_message(mapping.response))

        # Get data as integer list from both the incoming message and the response
        # template in the mapping
        response = list(midi_message.data)                        
        template = list(self.mapping.response.data)        

        # The first two values are ignored (the Kemper MIDI specification implies this would contain the product type
        # and device ID as for the request, however the device just sends two zeroes)

        # Check if the message belongs to the mapping. The following have to match:
        #   2: function code, 
        #   3: instance ID, 
        #   4: address page, 
        #   5: address nunber
        if response[2:6] != template[2:6]:
            return
        
        # The values starting from index 6 are the value of the response.
        if self.mapping.type == KemperMidi.NRPN_PARAMETER_TYPE_STRING:
            # Take as string
            self.mapping.value = ''.join(chr(int(c)) for c in response[6:-1])
        else:
            # Decode 14-bit value to int
            self.mapping.value = response[-2] * 128 + response[-1]
        
        self._print("   -> Received value " + repr(self.mapping.value) + ": " + Tools.stringify_midi_message(midi_message))

        # Call the listeners
        for listener in self._listeners:
            listener.parameter_changed(self.mapping)  # The mapping has the values set already

        # Clear listeners
        self._listeners = None

    # Debug console output
    def _print(self, msg):
        if Tools.get_option(Config, "debugKemper") != True:
            return
        
        Tools.print("Kemper: " + msg)


######################################################################################################################


# Base class for listeners to kemper parameter changes
class KemperRequestListener:

    # Called by the Kemper class when a parameter request has been answered.
    # The value received is already set on the mapping.
    def parameter_changed(self, mapping):
        pass
