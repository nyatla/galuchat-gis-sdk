from .IndexMap import IndexMap


class DiagonalIndexMap(IndexMap):
    """size*sizeの矩形を斜めにスキャンするインデックスを返します。"""

    def __init__(self, size: int):
        super().__init__(size)
        self.threshold = size * (size + 1) // 2

    def map(self, index: int) -> int:
        size = self._size
        c = index % size
        r = index // size
        if c + r < size:
            return (c + r) * (c + r + 1) // 2 + r
        else:
            rev_r = size - 1 - r
            rev_c = size - 1 - c
            return size * size - 1 - (rev_c + rev_r) * (rev_c + rev_r + 1) // 2 - rev_r

    def unmap(self, index: int) -> int:
        size = self._size
        if index < self.threshold:
            n = self.find_n(index)
            y0 = n * (n + 1) // 2
            r = index - y0
            c = n - r
            return r * size + c
        else:
            rev_index = size * size - 1 - index
            n = self.find_n(rev_index)
            y0 = n * (n + 1) // 2
            rev_r = rev_index - y0
            rev_c = n - rev_r
            r = size - 1 - rev_r
            c = size - 1 - rev_c
            return r * size + c

    def find_n(self, index: int) -> int:
        """index 以下の最大の n を見つける。n は n * (n + 1) / 2 <= index を満たす。"""
        low, high = 0, self._size
        while low < high:
            mid = (low + high + 1) // 2
            if mid * (mid + 1) // 2 <= index:
                low = mid
            else:
                high = mid - 1
        return low

    @staticmethod
    def test():
        n = 4
        dz = DiagonalIndexMap(n)
        for i in range(n):
            print([dz.map(j + i * n) for j in range(n)])
        for i in range(n):
            print([dz.unmap(dz.map(j + i * n)) for j in range(n)])
