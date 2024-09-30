from adafruit_midi.system_exclusive import SystemExclusive

from .ClientRequest import ClientRequest, ClientRequestListener
from ..misc.Tools import Tools
from ...definitions import ProcessingConfig

# Implements all MIDI communication to and from the client device
class Client(ClientRequestListener):

    _requests = []   # List of ClientRequest objects

    def __init__(self, midi, config):
        self._midi = midi
        self._config = config

        self._debug = Tools.get_option(self._config, "debugClient")
        self._debug_mapping = Tools.get_option(self._config, "clientDebugMapping", None)

        self._value_provider = self._config["valueProvider"]

        # Buffer for mappings. Whenever possible, existing mappings are used
        # so values can be buffered.
        self._mappings_buffer = []     

        self._max_request_lifetime = Tools.get_option(self._config, "maxRequestLifetimeMillis", ProcessingConfig.DEFAULT_MAX_REQUEST_LIFETIME_MILLIS)
        
    # Sends the SET message of a mapping
    def set(self, mapping, value):
        if mapping.set == None:
            raise Exception("No SET message prepared for this MIDI mapping")
        
        self._value_provider.set_value(mapping, value)
                
        if self._debug == True:
            self._print("Send SET message (" + mapping.name + "): " + Tools.stringify_midi_message(mapping.set), mapping)

        self._midi.send(mapping.set)

    # Send the request message of a mapping. Calls the passed listener when the answer has arrived.
    def request(self, mapping, listener):
        # Add request to the list and send it
        req = self._get_matching_request(mapping)
        if req == None:
            # New request
            m = self._get_buffered_mapping(mapping)
            if m == None:
                m = mapping

            req = ClientRequest(                
                self._midi,
                m,
                self._config
            )
            
            req.add_listener(self)          # Listen to fill the buffer
            req.add_listener(listener)

            # Add to list
            self._requests.append(req)
            
            if self._debug == True:
                self._print("Added new request for " + mapping.name + ". Open requests: " + str(len(self._requests)), mapping)

            # Send
            req.send()            
        else:
            # Existing request: Add listener
            req.add_listener(listener)

            if self._debug == True:
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

            if self._debug == True:
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

                if self._debug == True:
                    self._print("Terminated request for " + request.mapping.name + ", took " + str(diff) + "ms")

        # Remove finished requests
        self._requests = [i for i in self._requests if i.finished() == False]
            
    # Debug console output
    def _print(self, msg, mapping = None):
        if self._debug_mapping != None and mapping != None and self._debug_mapping != mapping:
            return
        
        Tools.print("Client: " + msg)


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
