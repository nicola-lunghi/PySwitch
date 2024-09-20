from adafruit_midi.system_exclusive import SystemExclusive

from ...definitions import KemperMidi
from ..Tools import Tools
from ..EventEmitter import EventEmitter

# Model for a request for a value
class KemperRequest(EventEmitter):

    def __init__(self, midi, mapping, config):
        super().__init__(KemperRequestListener)
        
        self.mapping = mapping        
        self._config = config
        self._midi = midi
        
        self._debug = Tools.get_option(self._config, "debugKemper")
        self._debug_raw_midi = Tools.get_option(self._config, "debugKemperRawMidi")

        if self.mapping.request == None:
            raise Exception("No REQUEST message prepared for this MIDI mapping")
        
        if self.mapping.response == None:
            raise Exception("No response template message prepared for this MIDI mapping")
        
        if not isinstance(self.mapping.request, SystemExclusive):
            raise Exception("Parameter requests do not work with ControlChange or other types. Use KemperNRPNMessage (or SystemExclusive directly) instead.")

        self.start_time = Tools.get_current_millis()            

    # Sends the request
    def send(self):
        if self._debug == True:
            self._print(" -> Send REQUEST message: " + Tools.stringify_midi_message(self.mapping.request))

        self._midi.send(self.mapping.request)

    # Returns if the request is finished
    def finished(self):
        return self.listeners == None

    # Send the terminate signal to all listeners and finished it, so it will be
    # cleared up next time.
    def terminate(self):
        if self.finished() == True:
            return
        
        # Call the listeners
        for listener in self.listeners:
            listener.request_terminated(self.mapping)

        # Clear listeners
        self.listeners = None

    # Parses an incoming MIDI message. If the message belongs to the mapping's request,
    # calls the listener with the received value.
    def parse(self, midi_message):
        if self.finished() == True:
            return
        
        if self.mapping.response == None:
            raise Exception("No response template message prepared for this MIDI mapping")

        if not isinstance(midi_message, SystemExclusive):
            return

        if not isinstance(self.mapping.response, SystemExclusive):
            return
        
        if self._debug_raw_midi == True:
            self._print("RAW Receive : " + Tools.stringify_midi_message(midi_message))
            self._print("RAW Template: " + Tools.stringify_midi_message(self.mapping.response))

        # Compare manufacturer IDs
        if midi_message.manufacturer_id != self.mapping.response.manufacturer_id:
            return 

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
        
        if self._debug == True:
            self._print("   -> Received value " + repr(self.mapping.value) + ": " + Tools.stringify_midi_message(midi_message))

        # Call the listeners
        for listener in self.listeners:
            listener.parameter_changed(self.mapping)  # The mapping has the values set already

        # Clear listeners
        self.listeners = None

    # Debug console output
    def _print(self, msg):
        Tools.print("KemperRequest: " + msg)


######################################################################################################################


# Base class for listeners to kemper parameter changes
class KemperRequestListener:

    # Called by the Kemper class when a parameter request has been answered.
    # The value received is already set on the mapping.
    def parameter_changed(self, mapping):
        pass

    # Called when the Kemper is offline (requests took too long)
    def request_terminated(self, mapping):
        pass
