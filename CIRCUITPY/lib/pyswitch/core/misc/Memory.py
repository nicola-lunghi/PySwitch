from gc import collect, mem_free
from .Tools import Tools

# Size for visualizations (num of characters. Best is an odd number)
VISUALIZATION_SIZE = 15


# Memory monitoring tools
class Memory:

    # Padding for the prefix string
    PREFIX_LENGTH = 60

    # Free space at first and last call of watch()
    STARTING_FREE_BYTES = -1
    LAST_FREE_BYTES = -1

    # Zoom facor for allocated bytes
    ALLOCATED_BYTES_ZOOM = None

    # Initialize memory watching. Must be called for any measurements to take place.
    @staticmethod
    def init(prefix = None, zoom = 3):
        free_bytes = Memory._get_free_bytes()
        prefix_out = Memory._convert_prefix(prefix)
    
        # Initialize
        Memory.LAST_FREE_BYTES = free_bytes
        Memory.STARTING_FREE_BYTES = free_bytes

        Memory.ALLOCATED_BYTES_ZOOM = zoom

        Tools.print(prefix_out + Tools.fill_up_to("Starting with " + Tools.format_size(free_bytes) + " of free memory", 58) + Memory._visualize_free_bytes(free_bytes))

    # Prints the memory allocated since the last call
    @staticmethod
    def watch(prefix = None):
        if Memory.STARTING_FREE_BYTES < 0:
            return

        free_bytes = Memory._get_free_bytes()
        allocated_bytes = Memory.LAST_FREE_BYTES - free_bytes        
        Memory.LAST_FREE_BYTES = free_bytes
        prefix_out = Memory._convert_prefix(prefix)
        
        if allocated_bytes >= 0:
            Tools.print(prefix_out + "Allocated " + Tools.format_size(allocated_bytes, fill_up_to = 12) + " " + Memory._visualize_allocated_bytes(allocated_bytes) + " -> " + Tools.format_size(free_bytes, fill_up_to = 15) + " " + Memory._visualize_free_bytes(free_bytes))
        else:
            Tools.print(prefix_out + "Released  " + Tools.format_size(-allocated_bytes, fill_up_to = 12) + " " + Memory._visualize_allocated_bytes(allocated_bytes) + " -> " + Tools.format_size(free_bytes, fill_up_to = 15) + " " + Memory._visualize_free_bytes(free_bytes))

    # Returns free bytes of memory
    @staticmethod
    def _get_free_bytes():
        collect()
        return mem_free()

    # Output formatting for the prefixes
    @staticmethod
    def _convert_prefix(prefix):
        return Tools.fill_up_to((prefix + " ") if prefix else "", num_spaces_at_right = Memory.PREFIX_LENGTH, fill_char = ".") + " "

    # Returns a console visualization of free bytes
    @staticmethod
    def _visualize_free_bytes(free_bytes, size = VISUALIZATION_SIZE):
        num_chars = int((free_bytes / Memory.STARTING_FREE_BYTES) * size)
        return "".join([("X" if i <= num_chars else ".") for i in range(size)])

    # Returns a console visualization of allocated_bytes bytes
    @staticmethod
    def _visualize_allocated_bytes(allocated_bytes, size = VISUALIZATION_SIZE):
        zero_char = int(size / 2)
        value_char = int((-allocated_bytes * Memory.ALLOCATED_BYTES_ZOOM / Memory.STARTING_FREE_BYTES) * size / 2) + zero_char

        if allocated_bytes >= 0:
            ret = "".join([("<" if i >= value_char and i <= zero_char else ".") for i in range(size)])
        else:
            ret = "".join([(">" if i <= value_char and i >= zero_char else ".") for i in range(size)])

        return "".join([ret[i] if i != zero_char else "|" for i in range(size)])
