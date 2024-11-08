from micropython import const
from gc import collect, mem_free, mem_alloc
from .misc import Tools


# Size for visualizations (num of characters. Best is an odd number)
_VISUALIZATION_SIZE = const(15)

# Memory monitoring tools
class Memory:

    # Padding for the prefix string
    PREFIX_LENGTH = const(60)

    # Free space at first and last call of watch()
    TOTAL_BYTES = -1
    LAST_FREE_BYTES = -1

    # Zoom facor for allocated bytes
    ALLOCATED_BYTES_ZOOM = None

    # Initialize memory watching. Must be called for any measurements to take place.
    @staticmethod
    def start(prefix = None, zoom = 3):
        free_bytes = Memory._get_free_bytes()
        allocated_bytes = mem_alloc()
        TOTAL_BYTES = allocated_bytes + free_bytes
        prefix_out = Memory._convert_prefix(prefix)
    
        # Initialize
        Memory.LAST_FREE_BYTES = free_bytes
        Memory.TOTAL_BYTES = TOTAL_BYTES

        Memory.ALLOCATED_BYTES_ZOOM = zoom

        Tools.print(prefix_out + Tools.fill_up_to("Starting with " + Tools.format_size(free_bytes) + " of " + Tools.format_size(TOTAL_BYTES), 63) + Memory._visualize_free_bytes(free_bytes))

    # Prints the memory allocated since the last call
    @staticmethod
    def watch(prefix = None):
        if Memory.TOTAL_BYTES < 0:
            return

        free_bytes = Memory._get_free_bytes()
        allocated_bytes = Memory.LAST_FREE_BYTES - free_bytes        
        Memory.LAST_FREE_BYTES = free_bytes
        prefix_out = Memory._convert_prefix(prefix)

        alloc_vis = Memory._visualize_allocated_bytes(allocated_bytes)
        alloc_out = "            " if allocated_bytes == 0 else Tools.format_size(allocated_bytes, fill_up_to = 12)
        free_out = Tools.format_size(free_bytes, fill_up_to = 15)
        free_vis = Memory._visualize_free_bytes(free_bytes)
        free_perc_out = Tools.fill_up_to(str(int(free_bytes / Memory.TOTAL_BYTES * 100)) + "%", 4)

        if allocated_bytes > 0:
            descr = "Allocated "
        elif allocated_bytes < 0:
            descr = "Released  "
        else:
            descr = "          "

        Tools.print(prefix_out + descr + alloc_out + " " + alloc_vis + " -> " + free_out + " " + free_perc_out + " " + free_vis)        

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
    def _visualize_free_bytes(free_bytes, size = _VISUALIZATION_SIZE):
        num_chars = int((free_bytes / Memory.TOTAL_BYTES) * size)
        return "".join([("X" if i <= num_chars else ".") for i in range(size)])

    # Returns a console visualization of allocated_bytes bytes
    @staticmethod
    def _visualize_allocated_bytes(allocated_bytes, size = _VISUALIZATION_SIZE):
        zero_char = int(size / 2)
        value_char = int((-allocated_bytes * Memory.ALLOCATED_BYTES_ZOOM / Memory.TOTAL_BYTES) * size / 2) + zero_char

        if allocated_bytes >= 0:
            ret = "".join([("<" if i >= value_char and i <= zero_char else ".") for i in range(size)])
        else:
            ret = "".join([(">" if i <= value_char and i >= zero_char else ".") for i in range(size)])

        return "".join([ret[i] if i != zero_char else "|" for i in range(size)])

