from os import PathLike
from typing import Optional

from galuchat.chunk.gi01 import GaluchatImageDataChunk01Reader
from galuchat.io import BytesReaderFactory, FileReaderFactory, ReaderFactory
from galuchat.math.raster import IReadableRaster, RawRaster
from galuchat.math.rect import GisRect

from .WGSMapHeader import WGSMapHeader


class GaluchatWGSMap3Reader:
    """ReaderFactoryから独立したGI01復号セッションを作って読む。"""

    def __init__(
        self,
        header: WGSMapHeader,
        reader_factory: ReaderFactory,
        chunk_offset: int,
    ):
        self.header = header
        self._reader_factory = reader_factory
        self._chunk_offset = chunk_offset
        with reader_factory.create(chunk_offset) as reader:
            chunk = GaluchatImageDataChunk01Reader(reader)
            self._width = chunk.width
            self._height = chunk.height

    @classmethod
    def fromBytes(cls, src: bytes) -> "GaluchatWGSMap3Reader":
        reader_factory = BytesReaderFactory(src)
        with reader_factory.create() as reader:
            header = WGSMapHeader.unpack(reader)
            chunk_offset = reader.pos
        return cls(header, reader_factory, chunk_offset)

    @classmethod
    def fromFile(
        cls,
        path: str | PathLike[str],
        buffer_size: int = 8192,
    ) -> "GaluchatWGSMap3Reader":
        reader_factory = FileReaderFactory(path, buffer_size=buffer_size)
        with reader_factory.create() as reader:
            header = WGSMapHeader.unpack(reader)
            chunk_offset = reader.pos
        return cls(header, reader_factory, chunk_offset)

    @property
    def unitInvX(self) -> int:
        return self.header.unit_inv_x

    @property
    def unitInvY(self) -> int:
        return self.header.unit_inv_y

    @property
    def area(self) -> GisRect[int]:
        h = self.header
        return GisRect[int].createWithNSEW(
            h.south + self._height,
            h.south,
            h.west + self._width,
            h.west,
        )

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
        if not (0 <= lx < self._width and 0 <= ly < self._height):
            return None
        with self._reader_factory.create(self._chunk_offset) as reader:
            chunk = GaluchatImageDataChunk01Reader(reader)
            return chunk.readPoint(lx, ly)

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
        with self._reader_factory.create(self._chunk_offset) as reader:
            GaluchatImageDataChunk01Reader(reader).readRect(lx, ly, raster)
        return raster

    def readWgsRect(self, target: GisRect[int]) -> IReadableRaster:
        return self.readRect(
            target.x - self.header.west,
            target.y - self.header.south,
            target.width,
            target.height,
        )

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
        return self.readRect(0, 0, self._width, self._height)
