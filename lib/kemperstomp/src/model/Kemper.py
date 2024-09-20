import math

from adafruit_midi.control_change import ControlChange
from adafruit_midi.system_exclusive import SystemExclusive

from .KemperRequest import KemperRequest, KemperRequestListener
from ..Tools import Tools
from ...definitions import KemperDefinitions

# Implements all MIDI communication to and from the Kemper
class Kemper(KemperRequestListener):

    _requests = []   # List of KemperRequest objects

    def __init__(self, midi, config):
        self._midi = midi
        self._config = config
        self._debug = Tools.get_option(self._config, "debugKemper")

        # Buffer for mappings. Whenever possible, existing mappings are used
        # so values can be buffered.
        self._mappings_buffer = []     

        self._max_request_lifetime = Tools.get_option(self._config, "maxRequestLifetimeMillis", KemperDefinitions.DEFAULT_MAX_REQUEST_LIFETIME_MILLIS)
        
    # Receive MIDI messages
    def receive(self, midi_message):
        # See if one of the waiting requests matches        
        for request in self._requests:
            request.parse(midi_message)            

        # Check for finished requests
        self._cleanup_requests()

    # Sends the SET message of a mapping
    def set(self, mapping, value):
        if mapping.set == None:
            raise Exception("No SET message prepared for this MIDI mapping")
        
        if isinstance(mapping.set, ControlChange):
            # Set value
            mapping.set.value = value
        elif isinstance(mapping.set, SystemExclusive):
            data = list(mapping.set.data)
            while len(data) < 8:
                data.append(0)
            
            data[6] = int(math.floor(value / 128))
            data[7] = int(value % 128)

            mapping.set.data = bytes(data)
        else:
            raise Exception("Invalid mapping.set message")
                
        if self._debug == True:
            self._print("Send SET message: " + Tools.stringify_midi_message(mapping.set))

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

            req = KemperRequest(                
                self._midi,
                m,
                self._config
            )
            
            req.add_listener(self)          # Listen to fill the buffer
            req.add_listener(listener)

            # Add to list
            self._requests.append(req)
            
            if self._debug == True:
                self._print("Add new request. Number of open requests: " + str(len(self._requests)))

            # Send
            req.send()            
        else:
            if self._debug == True:
                self._print("Add new listener to existing request. Number of open requests: " + str(len(self._requests)))

            # Existing request: Add listener
            req.add_listener(listener)

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
                self._print("Added new mapping to buffer, num of buffer entries: " + str(len(self._mappings_buffer)))
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

    # Remove all finished requests
    def _cleanup_requests(self):
        # Terminate requests if they waited too long
        current_time = Tools.get_current_millis()        
        for request in self._requests:
            diff = current_time - request.start_time
            if diff > self._max_request_lifetime:
                request.terminate()

                if self._debug == True:
                    self._print("Terminated request, took " + str(diff) + "ms")

        # Remove finished requests
        self._requests = [i for i in self._requests if i.finished() == False]
            
    # Debug console output
    def _print(self, msg):
        Tools.print("Kemper: " + msg)
