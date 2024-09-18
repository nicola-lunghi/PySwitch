
# Midi mapping for a Kemper command. Contains commands to set or request a parameter
class KemperParameterMapping:
    # Takes MIDI messages as argument (ControlChange or (Kemper)SystemExclusive)
    def __init__(self, set = None, request = None):
        self.set = set
        self.request = request

    @property
    def can_set(self):
        return self.set != None

    @property
    def can_receive(self):
        return self.request != None

