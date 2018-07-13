import mmap

class RawReader(object):
    HASH_BYTES_HEX = 40

    @classmethod
    def from_file(cls, path):
        with open(path, 'rb') as fh:
            flen = fh.seek(0, 2)
            map = mmap.mmap(fh.fileno(), flen, prot=mmap.PROT_READ)
            return cls(map)

    def __init__(self, buffer):
        self.buffer = buffer
        self.maxpos = len(self.buffer)
        while (self.buffer[self.maxpos-1] == ord(b"\r") or
               self.buffer[self.maxpos-1] == ord(b"\n")):
            self.maxpos -= 1

    def query(self, hash):
        assert(len(hash) == self.HASH_BYTES_HEX)
        off = self.binsearch(hash)
        k, v = self.read_at(off)
        if k == hash:
            return v
        return None

    # Returns the last offset in [left, right) s.t. the entry at that
    # offset is <= hash
    def binsearch(self, hash, left=None, right=None):
        if left == None:
            left = 0
        if right == None:
            right = self.maxpos

        assert(left == 0 or self.buffer[left-1] == ord(b"\n"))
        assert(right == len(self.buffer)
               or self.buffer[right] == ord(b"\n")
               or self.buffer[right] == ord(b"\r"))

        while left < right:
            mid = left + (right - left)//2
            mid = self.buffer.rfind(b"\n", left, mid)
            if mid == -1:
                right = left
                mid = left
            else:
                mid += 1

            found, _ = self.read_at(mid)

            if found > hash:
                right = mid
            else:
                left = mid

        if left != len(self.buffer):
            got, _ = self.read_at(left)
            assert got <= hash
            next = self.buffer.find(b"\n", left)
            if next != -1:
                got, _ = self.read_at(next+1)
                assert got > hash

        return left

    def read_at(self, off):
        assert(off == 0 or self.buffer[off-1] == ord(b"\n"))
        assert(off < len(self.buffer))
        end = self.buffer.find(b"\n", off)
        if end == -1:
            end = len(self.buffer)
        entry = self.buffer[off:end]
        if entry.endswith(b"\r"):
            entry = entry[:-1]
        return tuple(entry.split(b":", 1))
