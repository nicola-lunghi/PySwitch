###################################################################################################################
# 
# This script can transfer file (or other) data from/to a MIDI connection on CircuitPy boards.
#
###################################################################################################################

from sys import exit
from math import ceil

####################################################################################################################
 
# Bridge version
PMB_VERSION = "0.3.1"

# Manufacturer ID of PyMidiBridge
PMB_MANUFACTURER_ID = b'\x00\x7c\x7d' 

# Command prefix to request a file to be transfered.
# Syntax: [
#     *PMB_REQUEST_MESSAGE,
#     <CRC-16, 3 half-bytes (only first 16 bits used, calculated over the rest of the message)>,
#     <Requested chunk size, 4 half-bytes>
#     <Path name as utf-8 bytes with no null termination>
# ]
PMB_REQUEST_MESSAGE = b'\x01'

# Command prefix to signal start of transfer. The file ID is a random requence used to identify 
# the file during the transfer, and is not used afterwards.
#
# Syntax: [
#     *PMB_START_MESSAGE,
#     <CRC-16, 3 half-bytes (only first 16 bits used, calculated over the rest of the message)>,
#     <Transmission id, 2 half-bytes>,
#     <Amount of chunks to be expected, 4 half-bytes>
#     <Path name as utf-8 bytes with no null termination>
# ]
PMB_START_MESSAGE = b'\x02'

# Command prefix for sending data chunks
# Syntax: [
#     *PMB_DATA_MESSAGE,
#     <CRC-16, 3 half-bytes (only first 16 bits used, calculated over the rest of the message)>,
#     <Transmission id, 2 half-bytes>,
#     <Chunk index, 4 half-bytes>,
#     <Payload, variable length>
# ]
PMB_DATA_MESSAGE = b'\x03'

# Command prefix for the acknowledge message, which is sent after receiving a file successfully
# Syntax: [
#     *PMB_ACK_MESSAGE,
#     <CRC-16, 3 half-bytes (only first 16 bits used, calculated over the rest of the message)>,
#     <File id, 2 half-bytes>
# ]
PMB_ACK_MESSAGE = b'\x04'

# Command prefix for error messages
# Syntax: [
#     *PMB_ERROR_MESSAGE,
#     <Error message as utf-8 bytes with no null termination>
# ]
PMB_ERROR_MESSAGE = b'\x7f'

# Message to reboot the device (calls sys.exit() which on CircuitPy triggers a reboot)
PMB_REBOOT_MESSAGE = b'\x66'


####################################################################################################################


# All command prefixes above have to be exactly this long
_PMB_PREFIXES_LENGTH_HALFBYTES = 1 

# Size of the chunk index (BEFORE packing! Therefore, 3 bytes will use 4 bytes in the end.)
_PMB_NUMBER_SIZE_FULLBYTES = 3
_PMB_NUMBER_SIZE_HALFBYTES = 4

# Length of the transmission id. This ID will be counted up to distinguish between transmissions. 
# (BEFORE packing! Therefore, 3 bytes will use 4 bytes in the end.)
_PMB_TRANSMISSION_ID_LENGTH_FULLBYTES = 3
_PMB_TRANSMISSION_ID_LENGTH_HALFBYTES = 4

# Length of the checksum in the message. Must fit for 16 bits, so we need at least 3 MIDI half-bytes.
_PMB_CHECKSUM_LENGTH_FULLBYTES = 2
_PMB_CHECKSUM_LENGTH_HALFBYTES = 3

# Endianess for conversion of numbers (not for the data itself!)
_PMB_NUMBER_ENC_ENDIANESS = "big"

# Encoding for strings during transfer
_PMB_STRING_ENCODING = "utf-8"

####################################################################################################################
    

# Use an instance of this to use the functionality.
class PyMidiBridge:

    # Next transmission ID
    _NEXT_ID = 1   

    # midi_send:        Object to send SystemExclusive messages. See MidiSender.
    # storage:          Object to interact with storage. See StorageProvider.
    # event_handler:    Optional event handler, used to handle incoming errors as well as other stuff. 
    #                   See EventHaldler definition below. 
    #
    def __init__(self, midi, storage, event_handler = None):
        self._midi = midi
        self._storage = storage
        self._event_handler = event_handler

        self._receive_transmission_id = None       # Internal file ID currently received.
        self._receive_handle = None        # Write file handle (as returned by storage.open())
        self._receive_amount_chunks = -1   # Amount of chunks to be received
        self._receive_last_chunk = -1      # Counts received chunks


    ## Send Messages ##########################################################################################################


    # Open a file, and send it in chunks (also called internally when a request comes in)
    def send(self, path, chunk_size):
        if not path:
            raise Exception("No path")

        if chunk_size < 1:
            raise Exception("Invalid chunk size: " + repr(chunk_size))

        # Generate new file ID (internally used)
        transmission_id_bytes = self._generate_transmission_id()                  

        # Check if file exists and see how many chunks we will need
        data_size = self._storage.size(path)
        if data_size < 0:
            raise Exception(repr(path) + " not found")
        
        if data_size == 0:
            raise Exception(repr(path) + " is empty")
        
        amount_chunks = ceil(data_size / chunk_size)

        # Open file for reading
        handle = self._storage.open(path, "r")

        # Send start message
        self._send_start_message(
            path = path, 
            transmission_id_bytes = transmission_id_bytes,
            amount_chunks = amount_chunks
        )

        # Transfer in chunks
        chunk_index = 0
        while(True):
            chunk = handle.read(chunk_size)
            if not chunk:
                break

            self._send_chunk(transmission_id_bytes, chunk, chunk_index)
            chunk_index += 1

        handle.close()


    # Sends a MIDI message to request a file
    def request(self, path, chunk_size):
        if not path:
            raise Exception() #"No path")
        
        payload = self._number_2_bytes(chunk_size, _PMB_NUMBER_SIZE_FULLBYTES) + self._string_2_bytes(path)
        checksum = self._get_checksum(payload)

        self._midi.send_system_exclusive(
            manufacturer_id = PMB_MANUFACTURER_ID,
            data = PMB_REQUEST_MESSAGE + checksum + payload            
        )


    # Send the "Start of transmission" message
    def _send_start_message(self, path, transmission_id_bytes, amount_chunks):     
        amount_chunks_bytes = self._number_2_bytes(amount_chunks, _PMB_NUMBER_SIZE_FULLBYTES)   
        
        payload = transmission_id_bytes + amount_chunks_bytes + self._string_2_bytes(path)
        checksum = self._get_checksum(payload)
        
        self._midi.send_system_exclusive(
            manufacturer_id = PMB_MANUFACTURER_ID,
            data = PMB_START_MESSAGE + checksum + payload            
        )


    # Sends one chunk of data
    def _send_chunk(self, transmission_id_bytes, chunk, chunk_index):
        data_bytes = self._string_2_bytes(chunk)
        chunk_index_bytes = self._number_2_bytes(chunk_index, _PMB_NUMBER_SIZE_FULLBYTES)
        
        payload = transmission_id_bytes + chunk_index_bytes + data_bytes
        checksum = self._get_checksum(payload)
        
        self._midi.send_system_exclusive(
            manufacturer_id = PMB_MANUFACTURER_ID,
            data = PMB_DATA_MESSAGE + checksum + payload
        )


    # Generate a file ID (4 bytes)
    def _generate_transmission_id(self):
        result = self._number_2_bytes(self._NEXT_ID, _PMB_TRANSMISSION_ID_LENGTH_FULLBYTES)        
        self._NEXT_ID += 1        
        return result
    

    ## Receive Messages ##########################################################################################################


    # Must be called for every incoming MIDI message to receive data. This class only uses SysEx, so the incoming messages
    # have to feature the attributes "manufacturer_id" and "data" (both bytearrays) to be regarded
    def receive(self, midi_message):
        # Check if the message has the necessary attributes
        if not hasattr(midi_message, "manufacturer_id") or not hasattr(midi_message, "data"):
            return
        
        # Is the message for us?
        if midi_message.manufacturer_id != PMB_MANUFACTURER_ID:
            return
        
        # This determines what the sender of the message wants to do
        command_id = midi_message.data[:_PMB_PREFIXES_LENGTH_HALFBYTES]

        # Receive: Reboot
        if command_id == PMB_REBOOT_MESSAGE:
            exit()

        # Next there is the checksum for all messages
        checksum_bytes = midi_message.data[_PMB_PREFIXES_LENGTH_HALFBYTES:_PMB_PREFIXES_LENGTH_HALFBYTES + _PMB_CHECKSUM_LENGTH_HALFBYTES]
        payload = midi_message.data[_PMB_PREFIXES_LENGTH_HALFBYTES + _PMB_CHECKSUM_LENGTH_HALFBYTES:]

        try:
            # Checksum test
            if self._get_checksum(payload) != checksum_bytes:
                raise Exception("Checksum mismatch")

            # Receive: Message to request sending a file
            if command_id == PMB_REQUEST_MESSAGE:
                # Send file
                self._receive_request(payload)
                return
            
            elif command_id == PMB_ERROR_MESSAGE:
                # Handle incoming error messages if an error handler is given
                if self._event_handler:
                    error = self._bytes_2_string(payload)
                    self._event_handler.handle(error)
                return

            # All other messages have a file ID coming next, so we split that off the payload
            transmission_id_bytes = payload[:_PMB_TRANSMISSION_ID_LENGTH_HALFBYTES]
            payload = payload[_PMB_TRANSMISSION_ID_LENGTH_HALFBYTES:]

            # Receive: Start of transmission
            if command_id == PMB_START_MESSAGE:
                self._receive_start(transmission_id_bytes, payload)

            # Receive: Data
            elif command_id == PMB_DATA_MESSAGE:            
                if transmission_id_bytes == self._receive_transmission_id:
                    self._receive_data(payload)

            # Ack message
            elif command_id == PMB_ACK_MESSAGE:
                if self._event_handler:
                    self._event_handler.transfer_finished(transmission_id_bytes)

        except Exception as e:
            self.error(repr(e))


    # Request message received
    def _receive_request(self, payload):
        chunk_size = self._bytes_2_number(payload[:_PMB_NUMBER_SIZE_HALFBYTES])
        path = self._bytes_2_string(payload[_PMB_NUMBER_SIZE_HALFBYTES:])

        self.send(path, chunk_size)


    # Start receiving file data
    def _receive_start(self, transmission_id_bytes, payload):
        # Reset state
        self._receive_last_chunk = -1
        self._receive_transmission_id = transmission_id_bytes
        
        # Amount of chunks overall
        self._receive_amount_chunks = self._bytes_2_number(payload[:_PMB_NUMBER_SIZE_HALFBYTES])

        # Path to write to
        write_path = self._bytes_2_string(payload[_PMB_NUMBER_SIZE_HALFBYTES:])
                                
        # Open file for appending
        self._receive_handle = self._storage.open(write_path, "a")


    # Receive file data
    def _receive_data(self, payload):        
        # Index of the chunk
        index = self._bytes_2_number(payload[:_PMB_NUMBER_SIZE_HALFBYTES])

        # Chunk data
        str_data = self._bytes_2_string(payload[_PMB_NUMBER_SIZE_HALFBYTES:])
    
        # Only accept if the chunk index is the one expected
        if index != self._receive_last_chunk + 1:
            raise Exception("Invalid chunk") #"Invalid chunk " + repr(index) + ", expected " + repr(self._receive_last_chunk + 1))
        
        self._receive_last_chunk = index

        # Append to file
        self._receive_handle.write(str_data)

        # If this has been the last chunk, close the file handle and send ack message
        if index == self._receive_amount_chunks - 1:
            self._receive_finish()


    # Finish receiving and send acknowledge message
    def _receive_finish(self):
        # Finished (last chunk received)
        self._receive_handle.close()
        self._receive_handle = None
        
        self._send_ack_message(self._receive_transmission_id)
        self._receive_transmission_id = None


    # Sends the "acknowledge successful transfer" message
    def _send_ack_message(self, transmission_id_bytes):
        payload = transmission_id_bytes
        checksum = self._get_checksum(payload)
        
        self._midi.send_system_exclusive(
            manufacturer_id = PMB_MANUFACTURER_ID,
            data = PMB_ACK_MESSAGE + checksum + payload
        )


    # Sends an error message
    def error(self, msg):
        print(len(msg))
        payload = self._string_2_bytes(msg)
        checksum = self._get_checksum(payload)

        self._midi.send_system_exclusive(
            manufacturer_id = PMB_MANUFACTURER_ID,
            data = PMB_ERROR_MESSAGE + checksum + payload
        )


    ## Checksum ###########################################################################################################


    # Get checksum of bytes (only returns MIDI half-bytes)
    def _get_checksum(self, data):
        if not data:
            return bytes([0x00 for i in range(_PMB_CHECKSUM_LENGTH_HALFBYTES)])
        
        crc = self._crc16(data)
        return self._number_2_bytes(crc, _PMB_CHECKSUM_LENGTH_FULLBYTES) 


    # CRC-16-CCITT Algorithm
    # Taken from https://gist.github.com/oysstu/68072c44c02879a2abf94ef350d1c7c6
    def _crc16(self, data, poly = 0x6756):
        crc = 0xFFFF
        for b in data:
            cur_byte = 0xFF & b
            for _ in range(0, 8):
                if (crc & 0x0001) ^ (cur_byte & 0x0001):
                    crc = (crc >> 1) ^ poly
                else:
                    crc >>= 1
                cur_byte >>= 1
        crc = (~crc & 0xFFFF)
        crc = (crc << 8) | ((crc >> 8) & 0xFF)

        return crc & 0xFFFF


    ## Conversions ##########################################################################################################


    # String to bytearray conversion (only returns MIDI half-bytes)
    def _string_2_bytes(self, str):        
        return self._pack_bytes(str.encode(_PMB_STRING_ENCODING))

    # Bytearray to string conversion 
    def _bytes_2_string(self, data):
        return ''.join(self._unpack_bytes(data).decode(_PMB_STRING_ENCODING))    

    # Number to bytearray conversion (only returns MIDI half-bytes)
    def _number_2_bytes(self, num, num_bytes):
        return self._pack_bytes(num.to_bytes(num_bytes, _PMB_NUMBER_ENC_ENDIANESS))

    # Bytes to number conversion
    def _bytes_2_number(self, data):
        return int.from_bytes(self._unpack_bytes(data), _PMB_NUMBER_ENC_ENDIANESS)
    

    #########################################################################################################################


    # Packs full bytes into MIDI compatible half-bytes
    def _pack_bytes(self, data):
        return self._convert_bitlength(data, 8, 7, True)
    

    # Unpacks full bytes from MIDI compatible half-bytes
    def _unpack_bytes(self, data):
        return self._convert_bitlength(data, 7, 8, False)
    

    # Change bit length per byte
    def _convert_bitlength(self, data, bitlength_from, bitlength_to, append_leftovers):
        result = []
        buffer = []

        def flush():
            new_entry = 0x00
            
            while(len(buffer) < bitlength_to):
                buffer.append(False)

            for i in range(len(buffer)):
                e = buffer[i]
                if not e:
                    continue

                mask = (1 << (bitlength_to - 1 - i))
                new_entry |= mask

            result.append(new_entry)
            buffer.clear()

        for b in data:
            for i in range(bitlength_from):
                mask = (1 << (bitlength_from - 1 - i))
                buffer.append(b & mask == mask)

                if len(buffer) == bitlength_to:
                    flush()

        if append_leftovers and len(buffer) > 0:
            flush()

        return bytes(result)


# class EventHandler:
#
#     # Called when the bridge received an error message
#     def handle(self, message):
#         pass
#
#     # Called when the bridge received notice about a finished transfer on the other side
#     def transfer_finished(self, transmission_id_bytes):
#         pass


# class MidiSender:
#     # Must send the passed data as MIDI system exclusive message
#     def send_system_exclusive(self, manufacturer_id, data):
#         pass


# class StorageProvider:
#
#     # Must return file size, or any negative number if the file does not exist
#     def size(self, path):
#         return 0
# 
#     # Must return an opened file handle. See StorageFileHandle class.
#     def open(self, path, mode):
#         return None


# class StorageFileHandle:
#
#     # Must write data to the file
#     def write(self, data):
#         pass
#
#     # Must read the specified amount of data from the file, return None if finished.
#     def read(self, amount_bytes):
#         return ""
#
#     # Must close the file handle
#     def close(self):
#         pass
