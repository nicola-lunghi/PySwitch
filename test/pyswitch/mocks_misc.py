import lib.pyswitch.misc as misc


class MockMisc:
    msgs = []
    msgs_str = ""

    @staticmethod
    def reset_mock():
        MockMisc.msgs = []
        MockMisc.msgs_str = ""
    
    @staticmethod
    def do_print(msg):
        MockMisc.msgs.append(msg)
        MockMisc.msgs_str += msg

    @staticmethod
    def latest_msg():  
        if not MockMisc.msgs:
            return None
        return MockMisc.msgs[len(MockMisc.msgs)-1]

    compare_midi_messages = misc.compare_midi_messages
    stringify_midi_message = misc.stringify_midi_message
    format_size = misc.format_size
    get_option = misc.get_option
    fill_up_to = misc.fill_up_to
    get_current_millis = misc.get_current_millis

    DEFAULT_SWITCH_COLOR = misc.DEFAULT_SWITCH_COLOR
    DEFAULT_LABEL_COLOR = misc.DEFAULT_LABEL_COLOR
        
    Colors = misc.Colors
    Updater = misc.Updater
    Updateable = misc.Updateable
    EventEmitter = misc.EventEmitter
    PeriodCounter = misc.PeriodCounter

    PYSWITCH_VERSION = misc.PYSWITCH_VERSION
