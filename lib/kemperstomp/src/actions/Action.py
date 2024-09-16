
# Base class for actions
class Action:
    def __init__(self, appl, switch, config):
        self.appl = appl
        self.switch = switch
        self.config = config

    # Abstract: This will be called when the footswitch has been pressed down.
    def down(self):
        pass

    # Abstract: This will be called when the footswitch has been released.
    def up(self):
        pass

    # Will be called on every tick, whether a MIDI message has been received or not
    # (in the latter case None is passed).
    def receive(self, midi_message):
        pass
