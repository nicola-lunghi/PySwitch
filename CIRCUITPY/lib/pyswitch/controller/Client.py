from adafruit_midi.system_exclusive import SystemExclusive
from adafruit_midi.control_change import ControlChange

from ..misc import Tools, EventEmitter


# Base class for listeners to client parameter changes
class ClientRequestListener:

    # Called by the Client class when a parameter request has been answered.
    # The value received is already set on the mapping.
    def parameter_changed(self, mapping):
        pass

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        pass


######################################################################################################################


# Must implement preparation of MIDI messages for sending as well as parsing the received ones.
class ClientValueProvider:
    # Must parse the incoming MIDI message and return the value contained.
    # If the response template does not match, must return None.
    # Must return True to notify the listeners of a value change.
    def parse(self, mapping, midi_message):
        return False
    
    # Must set the passed value on the SET message of the mapping.
    def set_value(self, mapping, value):
        pass


######################################################################################################################


# Implements all MIDI communication to and from the client device
class Client(ClientRequestListener):

    def __init__(self, midi, config, value_provider):
        self._midi = midi
        self._config = config

        self._debug = Tools.get_option(self._config, "debugClient")
        self._debug_mapping = Tools.get_option(self._config, "clientDebugMapping", None)

        self._value_provider = value_provider

        # Buffer for mappings. Whenever possible, existing mappings are used
        # so values can be buffered.
        self._mappings_buffer = []     

        # List of ClientRequest objects    
        self._requests = []

        self._max_request_lifetime = Tools.get_option(self._config, "maxRequestLifetimeMillis", 2000)
        
    # Sends the SET message of a mapping
    def set(self, mapping, value):
        if not mapping.set:
            raise Exception("No SET message prepared for this MIDI mapping")
        
        self._value_provider.set_value(mapping, value)
                
        if self._debug:
            self._print("Send SET message (" + mapping.name + "): " + Tools.stringify_midi_message(mapping.set), mapping)

        self._midi.send(mapping.set)

    # Send the request message of a mapping. Calls the passed listener when the answer has arrived.
    def request(self, mapping, listener):
        # Add request to the list and send it
        req = self._get_matching_request(mapping)
        if not req:
            # New request
            m = self._get_buffered_mapping(mapping)
            if not m:
                m = mapping

            req = ClientRequest(                
                self._midi,
                m,
                self._config,
                self._value_provider
            )
            
            req.add_listener(self)          # Listen to fill the buffer
            req.add_listener(listener)

            # Add to list
            self._requests.append(req)
            
            if self._debug:
                self._print("Added new request for " + mapping.name + ". Open requests: " + str(len(self._requests)), mapping)

            # Send
            req.send()            
        else:
            # Existing request: Add listener
            req.add_listener(listener)

            if self._debug:
                self._print("Added new listener to existing request for " + mapping.name + ". Open requests: " + str(len(self._requests)) + ", Listeners: " + str(len(req.listeners)), mapping)

    # Receive MIDI messages
    def receive(self, midi_message):
        # See if one of the waiting requests matches        
        for request in self._requests:
            request.parse(midi_message)            

        # Check for finished requests
        self._cleanup_requests()

    # Gets the buffered value (or None) for a formerly requested mapping.
    def get(self, mapping):
        m = self._get_buffered_mapping(mapping)

        return m.value

    # Returns a buffered mapping that equals the given one, or None
    def _get_buffered_mapping(self, mapping):
        for m in self._mappings_buffer:
            if m == mapping:
                return m
            
        return None

    # This always listens to the requests, too, to fill the buffer
    def parameter_changed(self, mapping):
        m = self._get_buffered_mapping(mapping)
        if m == None:
            # Add to buffer
            self._mappings_buffer.append(mapping)

            if self._debug:
                self._print("Added new mapping for " + mapping.name + " to buffer, num of buffer entries: " + str(len(self._mappings_buffer)), mapping)
        else:
            # Update value
            m.value = mapping.value

    # Returns a matching request from the list if any, or None if no matching
    # request has been found.
    def _get_matching_request(self, mapping):
        if not isinstance(mapping.request, SystemExclusive):
            return None
        
        for request in self._requests:
            if request.mapping == mapping:
                return request
            
        return None

    # Remove all finished requests, and terminate the ones which took too long already
    def _cleanup_requests(self):
        # Terminate requests if they waited too long
        current_time = Tools.get_current_millis()
        for request in self._requests:
            diff = current_time - request.start_time
            if diff > self._max_request_lifetime:
                request.terminate()

                if self._debug:
                    self._print("Terminated request for " + request.mapping.name + ", took " + str(diff) + "ms")

        # Remove finished requests
        self._requests = [i for i in self._requests if not i.finished]
            
    # Debug console output
    def _print(self, msg, mapping = None):
        if self._debug_mapping != None and mapping != None and self._debug_mapping != mapping:
            return
        
        Tools.print("Client: " + msg)


#######################################################################################################################


# Midi mapping for a client command. Contains commands to set or request a parameter
class ClientParameterMapping:
    # Takes MIDI messages as argument (ControlChange or SystemExclusive)
    def __init__(self, name = "", set = None, request = None, response = None, type = None, value = None):
        self.name = name          # Mapping name (used for debug output only)
        self.set = set            # MIDI Message to set the parameter
        self.request = request    # MIDI Message to request the value
        self.response = response  # Response template MIDI message for parsing the received answer        
        self.type = type          # Type of mapping
        self.value = value        # Value of the parameter (buffer). After receiving an answer, the value 
                                  # is buffered here.                                  

    def __eq__(self, other):
        if not other:
            return False
        
        if self.request != None:
            if other.request != None:
                return self._compare_messages(self.request, other.request)
            else:
                return False
        elif self.set != None:
            if other.set != None:
                return self._compare_messages(self.set, other.set)
            else:
                return False
        return False

    # Compare two MIDI messages
    def _compare_messages(self, a, b):
        if a.__class__.__name__ != b.__class__.__name__:
            return False

        if isinstance(a, SystemExclusive):            
            return a.data == b.data

        if isinstance(a, ControlChange):
            return a.control == b.control
        
        return a == b

    @property
    def can_set(self):
        return self.set != None

    @property
    def can_receive(self):
        return self.request != None
    
    # Returns a copy of the mapping with no request/response and value. Use this
    # if you have performance issues with too much requests.
    @property
    def set_only(self):
        return ClientParameterMapping(
            name = self.name,
            set = self.set,
            type = self.type
        )


############################################################################################################


# Model for a request for a value
class ClientRequest(EventEmitter):

    def __init__(self, midi, mapping, config, value_provider):
        super().__init__(ClientRequestListener)
        
        self.mapping = mapping        
        self._config = config
        self._midi = midi
        
        self._debug = Tools.get_option(self._config, "debugClient")
        self._debug_raw_midi = Tools.get_option(self._config, "debugClientRawMidi")
        self._debug_mapping = Tools.get_option(self._config, "clientDebugMapping", None)

        self._value_provider = value_provider

        if not self.mapping.request:
            raise Exception("No REQUEST message prepared for this MIDI mapping (" + self.mapping.name + ")")
        
        if not self.mapping.response:
            raise Exception("No response template message prepared for this MIDI mapping (" + self.mapping.name + ")")
        
        if not isinstance(self.mapping.request, SystemExclusive):
            raise Exception("Parameter requests do not work with ControlChange or other types. Use SystemExclusive instead. (" + self.mapping.name + ")")

        self.start_time = Tools.get_current_millis()            

    # Sends the request
    def send(self):
        if self._debug:
            self._print(" -> Send REQUEST message for " + self.mapping.name + ": " + Tools.stringify_midi_message(self.mapping.request))

        self._midi.send(self.mapping.request)

    # Returns if the request is finished
    @property
    def finished(self):
        return self.listeners == None

    # Send the terminate signal to all listeners and finished it, so it will be
    # cleared up next time.
    def terminate(self):
        if self.finished:
            return
        
        # Call the listeners
        for listener in self.listeners:
            listener.request_terminated(self.mapping)

        # Clear listeners
        self.listeners = None

    # Parses an incoming MIDI message. If the message belongs to the mapping's request,
    # calls the listener with the received value.
    def parse(self, midi_message):
        if self.finished:
            return
        
        if not self.mapping.response:
            raise Exception("No response template message prepared for this MIDI mapping")

        if not isinstance(midi_message, SystemExclusive):
            return

        if not isinstance(self.mapping.response, SystemExclusive):
            return
        
        if self._debug_raw_midi:
            self._print("RAW Receive : " + Tools.stringify_midi_message(midi_message))
            self._print("RAW Template: " + Tools.stringify_midi_message(self.mapping.response))

        if not self._value_provider.parse(self.mapping, midi_message):
            return
        
        if self._debug:
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


