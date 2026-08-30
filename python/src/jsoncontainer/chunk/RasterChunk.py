
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
    lines:Tuple[Tuple[int,...],...]
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
            raise ValueError(f"Invalid raster type: {src['type']!r}")
        width=src["width"]
        height=src["height"]
        if type(width) is not int or type(height) is not int:
            raise ValueError("Raster width and height must be integers")
        if width<0 or height<0:
            raise ValueError("Raster width and height must be non-negative")
        if len(src["lines"])!=height:
            raise ValueError(
                f"Raster row count mismatch: expected={height} actual={len(src['lines'])}"
            )
        lines:List[Tuple[int,...]]=[]
        for r in src["lines"]:
            if len(r)%2!=0:
                raise ValueError("RLE row must contain count/value pairs")
            parsed_row:List[int]=[]
            row_width=0
            for i in range(0,len(r),2):
                count=r[i]
                value=r[i+1]
                if type(count) is not int or type(value) is not int:
                    raise ValueError("RLE count and value must be integers")
                if count<=0:
                    raise ValueError("RLE count must be greater than zero")
                row_width+=count
                parsed_row.extend((count,value))
            if row_width!=width:
                raise ValueError(
                    f"RLE row width mismatch: expected={width} actual={row_width}"
                )
            lines.append(tuple(parsed_row))
        
        return cls(width,height,tuple(lines))
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
