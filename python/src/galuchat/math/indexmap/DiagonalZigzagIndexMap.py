from .IndexMap import IndexMap


class DiagonalZigzagIndexMap(IndexMap):
    """size*sizeの矩形を斜めにジグザグスキャンするインデックスを返します。"""

    def __init__(self, size: int):
        super().__init__(size)

    def map(self, index: int) -> int:
        size = self._size
        c = index % size
        r = index // size
        cr = c + r
        if c + r < size:
            ct = c + r
            y0 = ct * (ct + 1) // 2
            if cr % 2 == 0:
                return y0 + r
            else:
                return y0 + ct - r
        else:
            rr = size - 1 - r
            ct = (size - 1 - c) + rr
            ym = (size**2 - 1) - ct * (ct + 1) // 2
            if cr % 2 == 0:
                return ym - rr
            else:
                return ym - ct + rr

    def unmap(self, index: int) -> int:
        size = self._size
        zli = None
        if index < size * (size + 1) // 2:
            for i in range(size):
                n = size - 1 - i
                if index >= (n**2 + n) // 2:
                    zli = i
                    break
            dlidx = size - 1 - zli
            slidx = (dlidx**2 + dlidx) // 2
            s = index - slidx
            c = dlidx - s
            r = s
            if (c + r) % 2 == 0:
                return c + r * size
            else:
                return r + c * size
        else:
            f = size**2 - 1
            for i in range(size):
                k = size - 1 - i - 1
                t = f - k * (k + 1) // 2
                if t >= index:
                    zli = i
                    break
            dlidx = zli + size
            dlidx = dlidx - size + 1
            ct = size - 1 - dlidx
            sindex = (size**2 - 1) - ct * (ct + 1) // 2
            ys = sindex - index
            xs = dlidx + ys
            c = xs
            r = size - 1 - ys
            if (c + r) % 2 == 0:
                return c + r * size
            else:
                return r + c * size

    @staticmethod
    def test():
        n = 4
        dz = DiagonalZigzagIndexMap(n)
        for i in range(n):
            print([dz.map(j + i * n) for j in range(n)])
        print("-----")
        for i in range(n):
            print([dz.unmap(dz.map(j + i * n)) for j in range(n)])
