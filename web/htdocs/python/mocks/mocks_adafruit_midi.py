from js import midiWrapper

class MockMidiInput:
    def read(self, num_bytes):
        cnt = 0
        buf = []
        while len(midiWrapper.messageQueue) > 0:
            m = midiWrapper.messageQueue.pop(0)
            msg = list(m)

            if cnt + len(msg) > num_bytes:
                return buf
            
            buf += msg

        return buf


class MockMidiOutput:
    def write(self, packet, length):
        midiWrapper.send(packet)

