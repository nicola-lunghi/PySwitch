from lib.pyswitch.misc import *

class MockMisc:
    Tools = Tools
    Colors = Colors
    Defaults = Defaults
    Updater = Updater
    Updateable = Updateable
    EventEmitter = EventEmitter
    Memory = Memory
    PeriodCounter = PeriodCounter

    ret_current_millis = 0

    @staticmethod
    def mock_get_current_millis():
        return MockMisc.ret_current_millis

MockMisc.Tools.get_current_millis = MockMisc.mock_get_current_millis
