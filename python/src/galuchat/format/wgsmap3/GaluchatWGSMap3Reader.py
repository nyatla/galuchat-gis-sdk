from typing import Optional

from galuchat.chunk.gi01 import GaluchatImageDataChunk01Reader
from galuchat.io import BytesBufferReader
from galuchat.math.raster import IReadableRaster, RawRaster
from galuchat.math.rect import GisRect

from ..wgsmap2 import WGSMapHeader


class GaluchatWGSMap3Reader:
    """WGSMap/3 + GI01をDOM化せずに読むReader。"""

    def __init__(self, header: WGSMapHeader, reader: GaluchatImageDataChunk01Reader):
        if header.data[:8] != WGSMapHeader.VERSION_3:
            raise ValueError("GaluchatWGSMap3Reader requires WGSMap/3 header")
        self.header = header
        self.reader = reader

    @classmethod
    def unpack(cls, src: bytes) -> "GaluchatWGSMap3Reader":
        reader = BytesBufferReader(src)
        header = WGSMapHeader.unpack(reader)
        chunk_reader = GaluchatImageDataChunk01Reader(src, offset=reader.pos)
        return cls(header, chunk_reader)

    @property
    def unitInvX(self) -> int:
        return self.header.unit_inv_x

    @property
    def unitInvY(self) -> int:
        return self.header.unit_inv_y

    @property
    def area(self) -> GisRect[int]:
        h = self.header
        r = self.reader
        return GisRect[int].createWithNSEW(h.south + r.height, h.south, h.west + r.width, h.west)

    @property
    def areaOfWgs(self) -> GisRect[float]:
        area = self.area
        return GisRect[float](
            area.x / self.header.unit_inv_x,
            area.y / self.header.unit_inv_y,
            area.width / self.header.unit_inv_x,
            area.height / self.header.unit_inv_y,
        )

    def readPoint(self, lx: int, ly: int) -> Optional[int]:
        if not self.reader.isInside(lx, ly):
            return None
        return self.reader.readPoint(lx, ly)

    def readWgsPoint(self, ilon: int, ilat: int) -> Optional[int]:
        h = self.header
        return self.readPoint(ilon - h.west, ilat - h.south)

    def readWgsPointf(self, lon: float, lat: float) -> Optional[int]:
        h = self.header
        return self.readPoint(
            round(lon * h.unit_inv_x) - h.west,
            round(lat * h.unit_inv_y) - h.south,
        )

    def readRect(self, lx: int, ly: int, width: int, height: int) -> IReadableRaster:
        raster = RawRaster.createRaster(width, height)
        self.reader.readRect(lx, ly, raster)
        return raster

    def readWgsRect(self, target: GisRect[int]) -> IReadableRaster:
        raster = RawRaster.createRaster(target.width, target.height)
        self.reader.readRect(target.x - self.header.west, target.y - self.header.south, raster)
        return raster

    def readWgsRectf(self, target: GisRect[float]) -> IReadableRaster:
        return self.readWgsRect(
            GisRect[int](
                round(target.x * self.header.unit_inv_x),
                round(target.y * self.header.unit_inv_y),
                round(target.width * self.header.unit_inv_x),
                round(target.height * self.header.unit_inv_y),
            )
        )

    def toRaster(self) -> IReadableRaster:
        raster = RawRaster.createRaster(self.reader.width, self.reader.height)
        return self.reader.readRect(0, 0, raster)
