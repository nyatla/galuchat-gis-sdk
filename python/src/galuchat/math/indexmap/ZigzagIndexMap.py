from .IndexMap import IndexMap


class ZigzagIndexMap(IndexMap):
    """一次元のsize*size矩形をジグザグスキャンする場合のインデクスを返します。"""

    def __init__(self, size: int):
        super().__init__(size)

    def map(self, index: int):
        size = self._size
        y = index // size
        x = index % size
        if y % 2 == 0:
            return x + y * size
        else:
            return size - 1 + y * size - x

    def unmap(self, index: int):
        size = self._size
        y = index // size
        x = index % size
        if y % 2 == 0:
            return x + y * size
        else:
            return size - 1 + y * size - x

    @staticmethod
    def test(n: int = 16, nextmap=None):
        n = 4
        dz = ZigzagIndexMap(n, nextmap)
        print("src--")
        for i in range(n):
            print([(j + i * n) for j in range(n)])
        print("map--")
        for i in range(n):
            print([dz.map(j + i * n) for j in range(n)])
        print("unmap")
        for i in range(n):
            print([dz.unmap(dz.map(j + i * n)) for j in range(n)])
