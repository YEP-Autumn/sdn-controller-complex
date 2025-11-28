import array
from pprint import pprint
from bitmap import BitMap

class OPF:

    BITMASK = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]

    def __init__(self, min_offset, max_offset):
        max_offset = max_offset - min_offset + 1
        nbytes = (max_offset + 7) // 8
        self.bitmap = array.array('B', [0 for _ in range(nbytes)])
        self.offset_start = min_offset

    def size(self):
        return len(self.bitmap) * 8

    def alloc_offset(self):
        for pos in range(self.size()):
            if (self.bitmap[pos // 8] & self.BITMASK[pos % 8]) == 0:
                self.bitmap[pos // 8] |= self.BITMASK[pos % 8]
                return (pos + self.offset_start)
        return -1

    def free_offset(self, offset):
        offset -= self.offset_start
        if(offset < 0 or offset > self.size()):
            return

        self.bitmap[offset // 8] &= ~self.BITMASK[offset % 8]
