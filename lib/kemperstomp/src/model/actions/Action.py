# Base class for actions. All functionality is encapsulated in a class for each, 
# inheriting from Action.
class Action:
    
    # config: See FootSwitch    
    def __init__(self, appl, switch, config):
        self.appl = appl
        self.switch = switch
        self.config = config

    # Will be called once to trigger the action (this is not necessarily 
    # on the down press, you can assign actions to different types of events).
    # event is one of the ActionEvent constants (for example ActionEvent.SWITCH_DOWN).
    def trigger(self, event):
        pass

    # Will be called on every tick, whether a MIDI message has been received or not
    # (in the latter case None is passed).
    def process(self, midi_message):
        pass

    # Returns if the action is registered for a given event 
    # (for example ActionEvent.SWITCH_DOWN)
    def has_event(self, event):
        for config_event in self.config["events"]:
            if config_event == event:
                return True
        return False
