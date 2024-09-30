
# Base class for event distributors (who call listeners)
class EventEmitter:
    def __init__(self, listener_type):
        self.listener_type = listener_type
        self.listeners = []

     # Adds a listener, and returns True if added, False if already existed.
    def add_listener(self, listener):
        if not isinstance(listener, self.listener_type):
            raise Exception("Listeners must be of type " + self.listener_type.__name__)
        
        if listener in self.listeners:
            return False
        
        self.listeners.append(listener)
        return True