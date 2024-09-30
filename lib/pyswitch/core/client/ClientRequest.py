from adafruit_midi.system_exclusive import SystemExclusive

from ..misc.Tools import Tools
from ..misc.EventEmitter import EventEmitter

# Model for a request for a value
class ClientRequest(EventEmitter):

    def __init__(self, midi, mapping, config):
        super().__init__(ClientRequestListener)
        
        self.mapping = mapping        
        self._config = config
        self._midi = midi
        
        self._debug = Tools.get_option(self._config, "debugClient")
        self._debug_raw_midi = Tools.get_option(self._config, "debugClientRawMidi")
        self._debug_mapping = Tools.get_option(self._config, "clientDebugMapping", None)

        self._value_provider = self._config["valueProvider"]

        if self.mapping.request == None:
            raise Exception("No REQUEST message prepared for this MIDI mapping (" + self.mapping.name + ")")
        
        if self.mapping.response == None:
            raise Exception("No response template message prepared for this MIDI mapping (" + self.mapping.name + ")")
        
        if not isinstance(self.mapping.request, SystemExclusive):
            raise Exception("Parameter requests do not work with ControlChange or other types. Use SystemExclusive instead. (" + self.mapping.name + ")")

        self.start_time = Tools.get_current_millis()            

    # Sends the request
    def send(self):
        if self._debug == True:
            self._print(" -> Send REQUEST message for " + self.mapping.name + ": " + Tools.stringify_midi_message(self.mapping.request))

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

        if self._value_provider.parse(self.mapping, midi_message) != True:
            return
        
        if self._debug == True:
            self._print("   -> Received value " + repr(self.mapping.value) + " for " + self.mapping.name + ": " + Tools.stringify_midi_message(midi_message))

        # Call the listeners
        for listener in self.listeners:
            listener.parameter_changed(self.mapping)  # The mapping has the values set already

        # Clear listeners
        self.listeners = None

    # Debug console output
    def _print(self, msg):
        if self._debug_mapping != None and self._debug_mapping != self.mapping:
            return

        Tools.print("ClientRequest: " + msg)


######################################################################################################################


# Base class for listeners to client parameter changes
class ClientRequestListener:

    # Called by the Client class when a parameter request has been answered.
    # The value received is already set on the mapping.
    def parameter_changed(self, mapping):
        pass

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        pass


