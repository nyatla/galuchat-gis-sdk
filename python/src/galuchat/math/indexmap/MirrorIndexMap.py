from .IndexMap import IndexMap


class MirrorIndexMap(IndexMap):
    def __init__(self, size: int, x_mirror=True, y_mirror=False):
        super().__init__(size)
        self._x_mirror = x_mirror
        self._y_mirror = y_mirror

    def map(self, index: int):
        size = self._size
        x = (size - 1 - index % size) if self._x_mirror else index % size
        y = (size - 1 - index // size) if self._y_mirror else index // size
        return x + y * size

    def unmap(self, index: int):
        size = self._size
        x = (size - 1 - index % size) if self._x_mirror else index % size
        y = (size - 1 - index // size) if self._y_mirror else index // size
        return x + y * size

    @staticmethod
    def test():
        n = 4
        dz = MirrorIndexMap(n, False, False)
        for i in range(n):
            print([dz.map(j + i * n) for j in range(n)])
        print("----")
        for i in range(n):
            print([dz.unmap(dz.map(j + i * n)) for j in range(n)])
