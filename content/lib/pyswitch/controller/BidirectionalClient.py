from .Client import Client, ClientRequest
from ..misc import Updateable


# Base class for bidirectional protocols
class BidirectionalProtocol:

    # Must return (boolean) if the passed mapping is handled in the bidirectional protocol
    def is_bidirectional(self, mapping):
        return False
    

####################################################################################################################


class BidirectionalClient(Client, Updateable):
    def __init__(self, midi, config, value_provider, protocol):
        Client.__init__(self, midi, config, value_provider)

        if not isinstance(protocol, BidirectionalProtocol):
            raise Exception("Invalid protocol: " + repr(protocol))
        
        self.protocol = protocol        

    # Filter the request messages from the mappings which are part of a bidirectional parameter set
    # (those cannot be requested anymore but get updates from the client automatically).
    def request(self, mapping, listener):
        m = mapping
        if self.protocol.is_bidirectional(mapping):
            m = mapping.set_and_receive_only
        
        super().request(m, listener)

    def receive(self, midi_message):
        Client.receive(self, midi_message)

        if not midi_message:
            return
        
        # TODO Init when active sensing comes and state is still initial (send beacon with init = 1 to get initial values)

        # TODO Receive sensing messages and re-init (with init = 1 again) when they stop appearing for longer then 1 second

    # In case of bidirectional parammeters, "simulate" a parameter change directly after the MIDI message
    def set(self, mapping, value):
        Client.set(self, mapping, value)

        # TODO Notify listeners of the mapping with the set value (we do not use echoing)

    # This must be updated at last, after all requests have been done at least one time!
    def update(self):
        pass

        # TODO Re-send init beacon at 80% of the time lease with init = 0

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
