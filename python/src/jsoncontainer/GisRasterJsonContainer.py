from abc import ABC,abstractmethod
from itertools import chain
from typing import Iterable,List,Optional,Sequence,Tuple,Any,ClassVar,Self
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

from collections.abc import Sequence
from typing import Any

from .writer import CustomPrettyJsonType
from .JsonContainer import JsonContainer
from .chunk import LatLonBaseChunk,RasterChunk

from galuchat.math.raster.Raster import IReadableRaster
from galuchat.math.rle import Rle



@dataclass
class GisRasterJsonContainer(JsonContainer):
    """ Json形式のデータコンテナ。
        ファイルIOとして使用し、データの処理媒体としては使用すべきでない。
    """
    CHUNK_TYPE:ClassVar[str]="GisRaster:3"
    created_date:datetime
    uuid:UUID
    source:str
    comment:str|None
    location:LatLonBaseChunk
    raster:RasterChunk    
    def toPrettyJson(self)->CustomPrettyJsonType:
        return {
            "type":self.CHUNK_TYPE,
            "metadata":{
                "created-date":self.created_date.strftime("%Y%m%dT%H%M%SZ"),
                "uuid":str(self.uuid),
                "source":self.source,
                "comment":self.comment,
            },
            "location":self.location.toPrettyJson(),
            "raster":self.raster.toPrettyJson()
        }
    @classmethod
    def createFromRasterChunk(
        cls,
        created_date: datetime,
        uuid: UUID,
        source: str,
        raster: RasterChunk,
        location: LatLonBaseChunk,
        comment: str | None = None,
    ) -> Self:
        """Create a container from an already RLE-compressed raster chunk."""
        return cls(created_date, uuid, source, comment, location, raster)

    @classmethod
    def create(cls,created_date:datetime,uuid:UUID,source:str,raster:IReadableRaster,location:LatLonBaseChunk,comment:str|None=None):
        lines:List[Tuple[int,...]]=[]
        for y in range(raster.height):
            #列にして圧縮
            lines.append(
                tuple(chain.from_iterable((Rle.encode([raster.get(x,y) for x in range(raster.width)]))))
            )
        raster_chunk = RasterChunk.fromRleRows(
            raster.width,
            raster.height,
            lines,
        )
        return cls.createFromRasterChunk(
            created_date,
            uuid,
            source,
            raster_chunk,
            location,
            comment,
        )
    @classmethod
    def parse(cls,src:Any)->Self:
        if src["type"]!=cls.CHUNK_TYPE:
            raise RuntimeError()
        meta=src["metadata"]
        return cls(
             datetime.strptime(meta["created-date"], "%Y%m%dT%H%M%SZ"),
             UUID(meta["uuid"]),
             meta["source"],
             meta["comment"],
             LatLonBaseChunk.parse(src["location"]),
             RasterChunk.parse(src["raster"]),
             )
