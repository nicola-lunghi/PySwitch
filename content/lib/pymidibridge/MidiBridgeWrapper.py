# This is a class which can be used on CircuitPy boards, to manage files remotely via MIDI.
# The MidiBridgeWrapper class has the same send/receive methods like the adafruit MIDI handler, 
# so you can just put this in between: Create your adafruit MIDI handler, pass it to this class and
# use this in your application just like the adafruit handler, and the MIDI bridge will be able to
# communicate (as long as your application calls receive() regularily of course).

import json
from os import stat, rename, listdir
from time import sleep
import traceback

from adafruit_midi.system_exclusive import SystemExclusive
from .PyMidiBridge import PyMidiBridge


# This passes all MIDI through to/from the passed MIDI handler, plus the PyMidiBridge is 
# listening for commands to read/change the configuration files via SysEx.
class MidiBridgeWrapper:
    def __init__(self, 
                 midi, 
                 temp_file_path = None, 
                 storage_provider = None, 
                #  debug = False
        ):
        self._midi = midi

        # Storage wrapper to the filesystem
        if not storage_provider:
            storage_provider = MidiBridgeStorageProvider(          
                temp_file_path = temp_file_path
            )

        # MIDI bridge (sends and receives MIDI messages to transfer files)
        self._bridge = PyMidiBridge(
            storage = storage_provider,
            midi = self,                         # The bridge calls send_system_exclusive to send its data
            event_handler = self,                # handle errors and messages here directly 
            # debug = debug
        )

        # self._debug = debug

    # Called to send messages (this is directly forwarded to the MIDI handler)
    def send(self, midi_message):
        self._midi.send(midi_message)

    # Called to receive messages. All messages will be passed to the MIDI bridge first,
    # then returned to the caller.
    def receive(self):
        msg = self._midi.receive()
        
        if msg:
            if self._bridge.receive(msg):
                # Message handled by the bridge.

                # It is important to have some time between the MIDI receive calls,
                # else SysEx messages will not come in completely and will be parsed as unknown events
                # because the end status is not reached. We assume that after a bridge related message
                # has been parsed, there will come more, so we wait here, not interfering with your normal
                # communication.
                sleep(0.01)

                return None
            
        return msg
    
    # Sends the passed error message via MIDI and keeps receiving messages forever 
    # This method will never terminate!
    def error(self, messageOrException):
        # If it is an exception, convert to string
        if isinstance(messageOrException, Exception):
            messageOrException = self.get_trace(messageOrException)
        
        # Print error on console
        print(messageOrException)        

        # Send error message
        self._bridge.error(messageOrException)

        # Initiate a simple transmission loop to enable receiving files
        while True:
            self.receive()


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
        print(repr(message))

    # Called when the bridge received notice about a finished transfer on the other side
    def transfer_finished(self, file_id_bytes):
        pass
        # if self._debug:
        #     print("Transfer finished: " + repr(file_id_bytes))

    # Returns the trace of an exception
    def get_trace(self, exception):        
        return str(traceback.format_exception(None, exception, exception.__traceback__))


#########################################################################################################


# Access to storage (used by the bridge). Note that the storage must be mounted with write privileges
# if the write functionality should work, else an exception is raised.
class MidiBridgeStorageProvider:

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

            #print("Successfully saved " + self._final_path)


    #####################################################################################


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


    #####################################################################################


    # File handle for folder listing (used whenever the path is a directory)
    class _FileHandleListDir:
        def __init__(self, content):
            self._listing = content

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


    #####################################################################################


    # You have to provide a path for a temporary file, used to buffer contents before transmission finished.
    def __init__(self, temp_file_path):
        self._temp_file_path = temp_file_path
        

    # Must return file size. In case of directories, we return the size of the string to be sent.
    def size(self, path):
        try:
            if self._is_dir(path):
                return len(self._get_folder_listing(path))
            
            return stat(path)[6]
        
        except OSError as e:
            if e.errno == 2:
                return -1
            raise e
    

    # Must return an opened file handle
    def open(self, path, mode):
        if mode == "a":
            # Write a file
            return self._FileHandleWrite(
                temp_path = self._temp_file_path,
                final_path = path
            )
        elif mode == "r":
            if self._is_dir(path):
                # Return a folder listing
                return self._FileHandleListDir(
                    content = self._get_folder_listing(path)
                )
            else:
                # Read a file
                return self._FileHandleRead(
                    path = path
                )


    # Is path a folder?
    def _is_dir(self, path):
        return stat(path)[0] == 16384
    
    
    # Returns the string for folder listings.
    def _get_folder_listing(self, path):
        if not path[-1] == "/":
            path += "/"

        data = []
        for file in listdir(path):
            stats = stat(path + file)

            data.append([
                file,
                stats[0] == 16384,
                stats[6]
            ])
            
        return json.dumps(data)

