import json
from os import stat, rename, listdir
from adafruit_midi.system_exclusive import SystemExclusive
from pymidibridge import PyMidiBridge
from ..misc import do_print


# This passes all MIDI through to/from the passed MIDI handler, plus the PyMidiBridge is 
# listening for commands to read/change the configuration files via SysEx.
class MidiBridgeWrapper:
    def __init__(self, midi, temp_file_path):
        self._midi = midi

        # MIDI bridge (sends and receives MIDI messages to transfer files)
        self._bridge = PyMidiBridge(
            midi = self,                         # The bridge calls send_system_exclusive to send its data
            storage = _StorageProvider(          # Storage wrapper to the filesystem
                temp_file_path = temp_file_path
            ),
            event_handler = self                 # handle errors and messages here directly 
        )

    def send(self, midi_message):
        self._midi.send(midi_message)

    def receive(self):
        msg = self._midi.receive()
        
        if msg:
            self._bridge.receive(msg)

        return msg
    

    ## Callbacks ###################################################################################


    # Must send the passed data as MIDI system exclusive message (used by the bridge)
    def send_system_exclusive(self, manufacturer_id, data):
        self._midi.send(
            SystemExclusive(
                manufacturer_id = manufacturer_id,
                data = data
            )
        )

    # Called when the bridge received an error message
    def handle(self, message):
        do_print("MIDI Bridge error: " + repr(message))

    # Called when the bridge received notice about a finished transfer on the other side
    def transfer_finished(self, file_id_bytes):
        do_print("Transfer finished: " + repr(file_id_bytes))


#######################################################################################################


# Access to storage (used by the bridge). Note that the storage must be mounted with write privileges
# if the write functionality should work, else an exception is raised.
class _StorageProvider:

    # File handle for writing
    class _FileHandleWrite:
        def __init__(self, temp_path, final_path):
            self._temp_path = temp_path
            self._final_path = final_path
            
            # Clear before appending
            open(self._temp_path, "w").close()
            
            # Data is first stored into a temporary file path, then copied to the destination when finished.
            self._handle = open(self._temp_path, "a")

        # Must read from the file handle
        def read(self, amount_bytes):
            raise Exception()

        # Must append data to the passed file handle
        def write(self, data):
            self._handle.write(data)

        # Must close the file handle
        def close(self):
            self._handle.close()
            self._handle = None

            # Copy temp file to its destination
            rename(self._temp_path, self._final_path)

            do_print("Successfully saved " + self._final_path)

    # File handle for reading
    class _FileHandleRead:
        def __init__(self, path):
            self._handle = open(path, "r")

        # Must read from the file handle
        def read(self, amount_bytes):
            return self._handle.read(amount_bytes)

        # Must append data to the passed file handle
        def write(self, data):
            raise Exception()

        # Must close the file handle
        def close(self):
            self._handle.close()
            self._handle = None

    # File handle for reading folder listing
    class _FileHandleListDir:
        def __init__(self, path):
            self._listing = json.dumps(listdir(path))

        # Must read from the file handle
        def read(self, amount_bytes):
            ret = self._listing[:amount_bytes]
            self._listing = self._listing[amount_bytes:]
            return ret

        # Must append data to the passed file handle
        def write(self, data):
            raise Exception()

        # Must close the file handle
        def close(self):
            pass

    # You have to provide a path for a temporary file, used to buffer contents.
    def __init__(self, temp_file_path):
        self._temp_file_path = temp_file_path
        
    # Must return file size
    def size(self, path):
        if self._is_dir(path):
            return len(json.dumps(listdir(path)))
        
        return stat(path)[6]
    
    # Must return an opened file handle
    def open(self, path, mode):
        if mode == "a":
            return self._FileHandleWrite(
                temp_path = self._temp_file_path,
                final_path = path
            )
        elif mode == "r":
            if self._is_dir(path):
                return self._FileHandleListDir(
                    path = path
                )
            else:
                return self._FileHandleRead(
                    path = path
                )

    # Is path a folder?
    def _is_dir(self, path):
        return stat(path)[0] > 0