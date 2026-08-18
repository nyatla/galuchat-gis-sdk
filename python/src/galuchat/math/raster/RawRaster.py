import builtins
from typing import List,List,TypeVar,Set,Optional,Sequence

from ..rect import Rect
from .Raster import Raster,IReadableRaster

T_READABLERASTER_DEST=TypeVar("T_READABLERASTER_DEST",bound="IReadableRaster")






class RawRaster(Raster[IReadableRaster]):
    @classmethod
    def createRaster(cls,width:int,height:int,value:int=0)->"RawRaster":
        buf=[value]*width*height
        return RawRaster(width,height,buf)

    def __init__(self,width:int,height:int,buf:List[int]):
        super().__init__(width,height)
        self._buf=buf


    def set(self,x:int,y:int,v:int):
        """ 値をセットする
        """
        self._buf[x+y*self._width]=v
    def get(self,x:int,y:int)->int:
        """ 値を取得する
        """
        return self._buf[x+y*self._width]
    def valueSet(self, range: Optional["Rect[int]"] = None) -> Set[int]:
        """Rasterを構成する値セットを返します。"""
        if range is None:
            return set(self._buf)

        x, y, w, h = range.x, range.y, range.width, range.height

        assert x >= 0 and y >= 0
        assert w >= 0 and h >= 0
        assert x + w <= self._width
        assert y + h <= self._height

        s: Set[int] = set()
        row_start = y * self._width

        for i in builtins.range(h):
            start = row_start + i * self._width + x
            s.update(self._buf[start : start + w])

        return s
    def toArray(self)->Sequence[int]:
        """00->01->10->11の順で直列化した配列を返します。
        """
        return self._buf
    def padding(self, left:int, top:int, right:int, bottom:int, pad:int) -> "RawRaster":
        """上下左右にパディングした画像を生成して返します。"""
        new_w = self._width + left + right
        new_h = self._height + top + bottom

        # 全体を pad で初期化
        new_buf: List[int] = [pad] * (new_w * new_h)

        # 元画像をコピー（行単位で貼り付け）
        for y in range(self._height):
            src_off = y * self._width
            dst_off = (y + top) * new_w + left
            new_buf[dst_off : dst_off + self._width] = self._buf[src_off : src_off + self._width]

        return RawRaster(new_w, new_h, new_buf)

    def createSubRaster(self,x:int,y:int,w:int,h:int)->IReadableRaster:
        assert x >= 0 and y >= 0, "negative origin"
        assert w >= 0 and h >= 0, "negative size"
        assert x + w <= self._width, "x out of bounds"
        assert y + h <= self._height, "y out of bounds"
        return _PartialRawRaster(self,x,y,w,h)

    
    
    


class _PartialRawRaster(Raster["_PartialRawRaster"]):
    """RawRasterの一部を参照する読み取り専用ラスタ。"""

    def __init__(self, parent: IReadableRaster, x: int, y: int, width: int, height: int):
        assert x >= 0 and y >= 0, "negative origin"
        assert width >= 0 and height >= 0, "negative size"
        assert x + width <= parent.width, "x out of bounds"
        assert y + height <= parent.height, "y out of bounds"
        super().__init__(width,height)
        self._parent = parent
        self._x = x
        self._y = y

    def get(self, x: int, y: int) -> int:
        assert x >= 0 and y >= 0, "negative coordinate"
        assert x < self._width and y < self._height, "coordinate out of bounds"
        return self._parent.get(self._x + x, self._y + y)

    def set(self, x: int, y: int, v: int):
        raise TypeError("_PartialRawRaster is read-only")

    def createSubRaster(self, x: int, y: int, w: int, h: int) -> "_PartialRawRaster":
        assert x >= 0 and y >= 0, "negative origin"
        assert w >= 0 and h >= 0, "negative size"
        assert x + w <= self._width, "x out of bounds"
        assert y + h <= self._height, "y out of bounds"
        return _PartialRawRaster(self._parent, self._x + x, self._y + y, w, h)

    def padding(self, left: int, top: int, right: int, bottom: int, pad: int) -> RawRaster:
        assert left >= 0 and top >= 0 and right >= 0 and bottom >= 0
        width = self._width + left + right
        height = self._height + top + bottom
        buf = [pad] * (width * height)
        for y in builtins.range(self._height):
            dst = (y + top) * width + left
            for x in builtins.range(self._width):
                buf[dst + x] = self.get(x, y)
        return RawRaster(width, height, buf)

    def toArray(self) -> Sequence[int]:
        return [
            self.get(x, y)
            for y in builtins.range(self._height)
            for x in builtins.range(self._width)
        ]

    def valueSet(self, range: Optional["Rect[int]"] = None) -> Set[int]:
        if range is None:
            x, y, w, h = 0, 0, self._width, self._height
        else:
            x, y, w, h = range.x, range.y, range.width, range.height
            assert x >= 0 and y >= 0
            assert w >= 0 and h >= 0
            assert x + w <= self._width
            assert y + h <= self._height
        return {
            self.get(ix, iy)
            for iy in builtins.range(y, y + h)
            for ix in builtins.range(x, x + w)
        }
