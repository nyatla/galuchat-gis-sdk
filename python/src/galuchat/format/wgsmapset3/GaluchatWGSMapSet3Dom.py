"""WGSMapSet/3 DOM implementation."""

from typing import List

from ...chunk import Chunk
from ...chunk.gi01 import GaluchatImageDataChunk01
from ...io import BytesBufferReader, BytesWriter
from ...math.raster import IReadableRaster, RawRaster
from ...math.rect import GisRect
from ..wgsmap3 import GaluchatWGSMap3Dom
from .WGSMapSetHeader3 import WGSMapSetHeader3


class GaluchatWGSMapSet3Dom:
    def __init__(self, header: WGSMapSetHeader3, chunks: List[GaluchatImageDataChunk01]):
        self.header = header
        self.chunks = chunks

    @property
    def area(self) -> GisRect[int]:
        areas = [
            GisRect[int].createWithNSEW(
                origin[1] + chunk.height,
                origin[1],
                origin[0] + chunk.width,
                origin[0],
            )
            for origin, chunk in zip(self.header.mapset, self.chunks)
        ]
        return GisRect[int].marge(areas)

    def toRaster(self) -> IReadableRaster:
        area = self.area
        dest = RawRaster.createRaster(area.width, area.height)
        for origin, chunk in zip(self.header.mapset, self.chunks):
            source = chunk.toRaster()
            dest_x = origin[0] - area.x
            dest_y = origin[1] - area.y
            for y in range(source.height):
                for x in range(source.width):
                    value = source.get(x, y)
                    if value != 0:
                        dest.set(dest_x + x, dest_y + y, value)
        return dest

    @classmethod
    def createFromWgsDoms(
        cls,
        data: List[GaluchatWGSMap3Dom],
        metadata: str | None,
    ) -> "GaluchatWGSMapSet3Dom":
        if len(data) < 1:
            raise ValueError("The data list must contain at least one instance.")
        unit_inv_x = {item.header.unit_inv_x for item in data}
        unit_inv_y = {item.header.unit_inv_y for item in data}
        if len(unit_inv_x) != 1 or len(unit_inv_y) != 1:
            raise ValueError("All headers must have same unit_inv_x/unit_inv_y.")
        header = WGSMapSetHeader3.createNew(
            list(unit_inv_x)[0],
            list(unit_inv_y)[0],
            [(item.header.west, item.header.south) for item in data],
            metadata,
        )
        return cls(header, [item.chunk for item in data])

    def toBytes(self) -> bytes:
        writer = BytesWriter()
        WGSMapSetHeader3.pack(self.header, writer)
        for chunk in self.chunks:
            GaluchatImageDataChunk01.pack(chunk, writer)
        return bytes(writer.buffer)

    @classmethod
    def fromBytes(cls, src: bytes) -> "GaluchatWGSMapSet3Dom":
        reader = BytesBufferReader(src)
        header = WGSMapSetHeader3.unpack(reader)
        if src[reader.pos:reader.pos + 4] == b"LAYO":
            Chunk.unpack(reader)
        chunks = [GaluchatImageDataChunk01.unpack(reader) for _ in range(header.numofmap)]
        return cls(header, chunks)
