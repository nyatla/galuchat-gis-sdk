from .IndexMap import IndexMap


class SpiralIndexMap(IndexMap):
    """size*sizeの矩形をスパイラル順にスキャンするインデックスを返します。"""

    def __init__(self, size: int):
        super().__init__(size)
        assert size % 2 == 0

    def map(self, index: int) -> int:
        size = self._size
        size_m1 = size - 1
        c = index % size
        r = index // size
        sidx_of_round = min(c, r, size - 1 - c, size - 1 - r)
        bottom = size_m1 - sidx_of_round
        r_width = size - sidx_of_round * 2
        if r == sidx_of_round:
            b = size**2 - (size - sidx_of_round * 2) ** 2
            return b + c - sidx_of_round
        elif c == bottom:
            b = size**2 - (size - sidx_of_round * 2) ** 2 + r_width
            return b + r - (sidx_of_round + 1)
        elif r == bottom:
            b = size**2 - (size - sidx_of_round * 2) ** 2 + r_width * 2 - 1
            return b + (size - 1 - c) - (sidx_of_round + 1)
        else:
            b = size**2 - (size - sidx_of_round * 2) ** 2 + r_width * 3 - 2
            return b + (size - 1 - r) - (sidx_of_round + 1)

    def unmap(self, index: int) -> int:
        size = self._size
        rn = 0
        sum_round = 0
        for i in range(1, size):
            t = size**2 - (size - i * 2) ** 2
            if index < t:
                break
            sum_round = t
            rn = i
        num_round = (size - rn * 2) * 4 - 4
        sidel = num_round // 4
        sideg = (index - sum_round) // sidel
        offset_side = (index - sum_round) % sidel
        if sideg == 0:
            c = offset_side + rn
            r = rn
            return c + r * size
        elif sideg == 1:
            c = size - 1 - rn
            r = rn + offset_side
            return c + r * size
        elif sideg == 2:
            c = (sidel - offset_side) + rn
            r = size - 1 - rn
            return c + r * size
        elif sideg == 3:
            c = rn
            r = (sidel - offset_side) + rn
            return c + r * size
        else:
            raise RuntimeError()

    @staticmethod
    def test():
        n = 8
        sz = SpiralIndexMap(n)
        for i in range(n):
            print([(j + i * n) for j in range(n)])
        print("-----")
        for i in range(n):
            print([sz.map(j + i * n) for j in range(n)])
        print("-----")
        for i in range(n):
            print([sz.unmap(sz.map(j + i * n)) for j in range(n)])
