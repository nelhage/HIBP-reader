import mmap

class RawReader(object):
    HASH_BYTES_HEX = 40

    @staticmethod
    def from_file(cls, path):
        fh = open(path, 'rb')
        flen = fh.seek(0, 2)
        map = mmap.mmap(self.fh.fileno(), flen, prot=mmap.PROT_READ)
        return cls(map)

    def __init__(self, buffer):
        self.buffer = buffer

    def query(self, hash):
        assert(len(hash) == self.HASH_BYTES_HEX)
        left = 0
        right = len(self.buffer)
        off = self.binsearch(left, right, hash)
        if off == right:
            return None
        return self.read_at(off)

    # Returns the last offset in [left, right) s.t. the entry at that
    # offset is <= hash, or right if hash is greater than any entry.
    def binsearch(self, left, right, hash):
        assert(left == 0 or self.buffer[left-1] == ord(b"\n"))
        assert(right == len(self.buffer)
               or self.buffer[right] == ord(b"\n")
               or self.buffer[right] == ord(b"\r"))

        while left < right:
            mid = left + (right + left)/2
            mid = self.buffer.rfind(b"\n", left, mid)
            if mid == -1:
                right = left
                mid = left
            found, _ = self.read_at(self, mid)
            if found > hash:
                left = mid
            else:
                right = mid

        if left != len(buffer):
            got, _ = self.read_at(left)
            assert got <= hash
            next = self.buffer.find(b"\n", left)
            if next != -1:
                got, _ = self.read_at(left)
                assert got > hash

        return left

    def read_at(self, off):
        assert(off == 0 or self.buffer[off-1] == ord(b"\n"))
        end = self.buffer.find(b"\n", off)
        if end == -1:
            end = len(self.buffer)
        entry = self.buffer[off:end]
        if entry.endswith(b"\r"):
            entry = entry[:-1]
        return tuple(entry.split(b":", 1))
