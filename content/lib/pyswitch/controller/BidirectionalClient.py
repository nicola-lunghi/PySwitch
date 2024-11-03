from adafruit_midi.system_exclusive import SystemExclusive

from .Client import Client, ClientRequest
from ..misc import Updateable, Tools


# Base class for bidirectional protocols
#class BidirectionalProtocol:
#
#    # Called before usage, with a midi handler.
#    def init(self, midi):
#        pass
#
#    # Must return (boolean) if the passed mapping is handled in the bidirectional protocol
#    def is_bidirectional(self, mapping):
#        return False
#   
#    # Must return (boolean) if the passed mapping should feed back the set value immediately
#    # without waiting for a midi message.
#    def feedback_value(self, mapping):
#        return False
#
#    # Initialize the communication etc.
#    def update(self):
#        pass
#   
#    # Receive midi messages (for example for state sensing)
#    def receive(self, midi_message):
#        pass


####################################################################################################################


class BidirectionalClient(Client, Updateable):

    def __init__(self, midi, config, value_provider, protocol):
        Client.__init__(self, midi, config, value_provider)

        #if not isinstance(protocol, BidirectionalProtocol):
        #    raise Exception("Invalid protocol: " + repr(protocol))
        
        self.protocol = protocol
        self.protocol.debug = Tools.get_option(config, "debugBidirectionalProtocol")
        self.protocol.init(midi)

    # Register the mapping and listener in advance (only plays a role for bidirectional parameters)
    def register(self, mapping, listener):
        if not self.protocol.is_bidirectional(mapping):
            return

        self.register_mapping(mapping.set_and_receive_only, listener, False)

    # Filter the request messages from the mappings which are part of a bidirectional parameter set
    # (those cannot be requested anymore but get updates from the client automatically).
    def request(self, mapping, listener):        
        if self.protocol.is_bidirectional(mapping):
            super().request(mapping.set_and_receive_only, listener)
        
        super().request(mapping, listener)

    # Receive messages (init communication when not yet done)
    def receive(self, midi_message):
        Client.receive(self, midi_message)

        if not midi_message:
            return

        if not isinstance(midi_message, SystemExclusive):
            return
               
        self.protocol.receive(midi_message)

    # In case of bidirectional parammeters, "simulate" a parameter change directly after the MIDI message
    def set(self, mapping, value):
        Client.set(self, mapping, value)

        # Notify listeners of the mapping with the set value (we do not use echoing, so the actions
        # will not reflect the state change if we just do nothing)
        if self.protocol.feedback_value(mapping):
            req = self.get_matching_request(mapping)
            if not req:
                raise Exception("No request for mapping: " + repr(mapping))
            
            mapping.value = value
            req.notify_listeners()

    # Update the protocol state
    def update(self):
        self.protocol.update()

    # Create a new request
    def create_request(self, mapping):
        # For bidirectional parameters, do not set a request lifetime so the requests never get cleaned up
        if self.protocol.is_bidirectional(mapping):  
            return ClientRequest(              
                self,
                mapping
            )
        else:
            return super().create_request(mapping)
        