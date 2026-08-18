
from typing import Iterable, List, Self,Sequence,Tuple,Any,ClassVar
from dataclasses import dataclass
from typing import Any

from galuchat.math.rect import Rect
from galuchat.math.raster import RawRaster
from galuchat.math.raster.Raster import IReadableRaster
from ..JsonContainer import JsonContainer
from ..writer import CustomPrettyJsonType, Inline, RowArray, RowObject

@dataclass
class RasterChunk(JsonContainer):
    CHUNK_TYPE:ClassVar[str]="Raster:1::LV-RLE-ROWS"
    width:int
    height:int
    lines:Tuple[Tuple[int],...]
    def toPrettyJson(self)->CustomPrettyJsonType:
        lines=RowArray([Inline(i) for i in self.lines], group=1)
        return RowObject(
            (
                (("type",self.CHUNK_TYPE,),),
                (("width",self.width,),("height",self.height,)),
                (("lines",lines,),),
            )
        )
    @classmethod
    def parse(cls,src:Any)->Self:
        if src["type"]!=cls.CHUNK_TYPE:
            raise RuntimeError()
        width=int(src["width"])
        height=int(src["height"])        
        lines:List[Tuple[int,...]]=[]
        for r in src["lines"]:
            if len(r)%2!=0:
                raise RuntimeError()
            if sum([int(r[i*2+0]) for i in range(len(r)//2)])!=width:
                raise RuntimeError()
            lines.append(tuple([int(r[j]) for j in range(0, len(r))]))
        
        return cls(width,height,lines)
    def toRaster(self, rect: Rect[int] | None = None)->IReadableRaster[RawRaster]:
        if rect is not None:
            if rect.x < 0 or rect.y < 0:
                raise ValueError("rect origin must be non-negative")
            if rect.width < 0 or rect.height < 0:
                raise ValueError("rect size must be non-negative")
            if rect.x + rect.width > self.width or rect.y + rect.height > self.height:
                raise ValueError("rect exceeds raster bounds")

            pixels:List[int]=[]
            x0=rect.x
            x1=rect.x+rect.width
            for line in self.lines[rect.y:rect.y+rect.height]:
                px=0
                for i in range(0,len(line),2):
                    count=line[i]
                    value=line[i+1]
                    run_start=px
                    run_end=px+count
                    left=max(run_start,x0)
                    right=min(run_end,x1)
                    if left<right:
                        pixels.extend([value]*(right-left))
                    px=run_end
                    if px>=x1:
                        break
            return RawRaster(rect.width,rect.height,pixels)

        pixels:List[int]=[]
        for line in self.lines:
            for i in range(0,len(line),2):
                pixels.extend([line[i+1]]*line[i])
        return RawRaster(self.width,self.height,pixels)

    def valueSet(self)->set[int]:
        """LV-RLE行をラスタ展開せず、含まれる値の集合を返す。"""
        values:set[int]=set()
        for line in self.lines:
            for i in range(1,len(line),2):
                values.add(line[i])
        return values
