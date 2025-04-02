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
            
            self._monitor(msg)
            buf += msg

        return buf
            
    def _monitor(self, msg):
        if not "midiMonitor" in externalRefs.to_py():
            return

        externalRefs.midiMonitor.monitorInput(msg)


class WrapMidiOutput:
    def write(self, packet, length):
        if not "midiWrapper" in externalRefs.to_py() or not externalRefs.midiWrapper:
            return
        
        self._monitor(packet)
        externalRefs.midiWrapper.send(packet)

    def _monitor(self, msg):
        if not "midiMonitor" in externalRefs.to_py():
            return
         
        externalRefs.midiMonitor.monitorOutput(msg)


