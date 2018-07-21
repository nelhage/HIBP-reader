import mmap

class RawReader(object):
    HASH_BYTES_HEX = 40

    INDEX_CHARS = 2
    INDEX_BITS  = 4 * INDEX_CHARS

    @classmethod
    def from_file(cls, path):
        with open(path, 'rb') as fh:
            flen = fh.seek(0, 2)
            map = mmap.mmap(fh.fileno(), flen, prot=mmap.PROT_READ)
            return cls(map)

    def __init__(self, buffer):
        self.buffer = buffer
        self.maxpos = len(self.buffer)
        self.index = None
        self.queries = 0

    def build_index(self):
        self.index = [0] * (2**self.INDEX_BITS+1)
        def recurse(l, r, loff, roff):
            mid = (l + r) // 2
            q = (bytes("{{:0{}x}}".format(self.INDEX_CHARS).format(mid), 'ascii') + b'0'*(40-self.INDEX_CHARS)).upper()
            moff = self.binsearch(q, loff, roff)
            self.index[mid] = moff
            if mid != l:
                recurse(l, mid - 1, loff, moff)
            if mid != r:
                recurse(mid + 1, r, moff, roff)

        recurse(0, 2**self.INDEX_BITS-1, 0, self.maxpos)
        self.index[-1] = self.maxpos

    def query(self, hash):
        assert(len(hash) == self.HASH_BYTES_HEX)
        if self.index:
            byte = int(hash[:self.INDEX_CHARS], 16)
            off = self.binsearch(hash, self.index[byte], self.index[byte+1])
        else:
            off = self.binsearch(hash)
        if off == self.maxpos:
            return None
        k, v = self.read_at(off)
        if k == hash:
            return v
        return None

    def nextrecord(self, off, max=None):
        next = self.buffer.find(b"\n", off, max)
        if next == -1:
            return max
        return next + 1

    def prevrecord(self, off, start=None):
        prev = self.buffer.rfind(b"\n", start, off)
        if prev == -1:
            return start
        return prev + 1

    # Returns the first offset in [left, right) s.t. the entry at that
    # offset is >= hash, or `right' if no such entry exists
    def binsearch(self, hash, left=None, right=None):
        if left == None:
            left = 0
        if right == None:
            right = self.maxpos

        assert(left == 0 or self.buffer[left-1] == ord(b"\n"))
        assert(right == len(self.buffer)
               or self.buffer[right-1] == ord(b"\n"))

        while left < right:
            mid = left + (right - left)//2
            mid = self.prevrecord(mid, left)

            found, _ = self.read_at(mid)

            if found == hash:
                return mid
            elif found > hash:
                right = mid
            else:
                left = self.nextrecord(mid, right)

        if left < self.maxpos:
            got, _ = self.read_at(left)
            assert got >= hash
        if left != 0:
            prev = self.prevrecord(left-1, 0)
            got, _ = self.read_at(prev)
            assert got < hash

        return left

    def read_at(self, off):
        self.queries += 1
        assert(off == 0 or self.buffer[off-1] == ord(b"\n"))
        assert(off < len(self.buffer))
        end = self.buffer.find(b"\n", off)
        if end == -1:
            end = len(self.buffer)
        entry = self.buffer[off:end]
        if entry.endswith(b"\r"):
            entry = entry[:-1]
        return tuple(entry.split(b":", 1))
