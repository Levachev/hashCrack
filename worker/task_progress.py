import struct

class TaskProgress:
    def __init__(self, array):
        # The DataView equivalent in Python using memoryview.
        # Note: The passed 'array' must be a mutable bytes-like object (e.g., bytearray) to allow in-place modifications.
        self.dataview = memoryview(array)

    @property
    def current(self):
        # Using struct.unpack_from with big-endian format (" >i ") to mimic JavaScript DataView.getInt32 default behavior.
        return struct.unpack_from(">i", self.dataview, 0)[0]

    @current.setter
    def current(self, value):
        # Using struct.pack_into with big-endian format (">i") to mimic JavaScript DataView.setInt32.
        struct.pack_into(">i", self.dataview, 0, value)

TaskProgressSize = 4
