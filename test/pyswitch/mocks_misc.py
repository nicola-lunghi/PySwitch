import lib.pyswitch.misc as misc


class MockMisc:
    class Tools(misc.Tools):
        msgs = []

        @staticmethod
        def print(msg):
            MockMisc.Tools.msgs.append(msg)

    Colors = misc.Colors
    Defaults = misc.Defaults    
    Updater = misc.Updater
    Updateable = misc.Updateable
    EventEmitter = misc.EventEmitter
    Memory = misc.Memory
    PeriodCounter = misc.PeriodCounter
