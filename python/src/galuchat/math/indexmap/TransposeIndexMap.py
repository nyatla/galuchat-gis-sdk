from .IndexMap import IndexMap


class TransposeIndexMap(IndexMap):
    """一次元のsize*size矩形を転置スキャンするインデクスを返します。"""

    def __init__(self, size: int):
        super().__init__(size)

    def map(self, index: int):
        size = self._size
        x = index // size
        y = index % size
        return x + y * size

    def unmap(self, index: int):
        size = self._size
        y = index // size
        x = index % size
        return x * size + y

    @staticmethod
    def test():
        z = TransposeIndexMap(2)
        print([z.map(i) for i in range(4)])
        print([z.unmap(z.map(i)) for i in range(4)])
        z = TransposeIndexMap(3)
        print([z.map(i) for i in range(9)])
        print([z.unmap(z.map(i)) for i in range(9)])
        z = TransposeIndexMap(4)
        print([z.map(i) for i in range(16)])
        print([z.unmap(z.map(i)) for i in range(16)])
