from js import externalRefs

class WrapUsbHid:
    def __init__(self):
        self.devices = []

class WrapUsbHidKeyboard:
    class Keyboard:
        def __init__(self, devices):
            pass

        def send(self, code):
            msg = "HID: Keycode " + str(code) + " sent"

            if hasattr(externalRefs, "messageHandler"):
                externalRefs.messageHandler.message(msg, "S")
            else:
                print(msg)