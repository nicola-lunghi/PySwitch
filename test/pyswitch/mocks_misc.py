import lib.pyswitch.misc as misc


class MockMisc:
    class Tools(misc.Tools):
        msgs = []
        msgs_str = ""

        @staticmethod
        def reset():
            MockMisc.Tools.msgs = []
            MockMisc.Tools.msgs_str = ""
        
        @staticmethod
        def print(msg):
            MockMisc.Tools.msgs.append(msg)
            MockMisc.Tools.msgs_str += msg

        @staticmethod
        def latest_msg():  
            if not MockMisc.Tools.msgs:
                return None
            return MockMisc.Tools.msgs[len(MockMisc.Tools.msgs)-1]

    Colors = misc.Colors
    Defaults = misc.Defaults    
    Updater = misc.Updater
    Updateable = misc.Updateable
    EventEmitter = misc.EventEmitter
    PeriodCounter = misc.PeriodCounter
