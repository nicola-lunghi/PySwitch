from js import externalRefs

class WrapMidiInput:
    def read(self, num_bytes):
        if not "midiWrapper" in externalRefs.to_py() or not externalRefs.midiWrapper:
            return None
        
        cnt = 0
        buf = []
        while len(externalRefs.midiWrapper.messageQueue) > 0:
            m = externalRefs.midiWrapper.messageQueue.pop(0)
            msg = list(m)

            if cnt + len(msg) > num_bytes:
                return buf
            
            buf += msg

        return buf


class WrapMidiOutput:
    def write(self, packet, length):
        if not "midiWrapper" in externalRefs.to_py() or not externalRefs.midiWrapper:
            return
        
        externalRefs.midiWrapper.send(packet)

