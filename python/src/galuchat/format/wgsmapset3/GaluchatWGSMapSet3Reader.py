"""WGSMapSet/3 sequential reader implementation."""

from os import PathLike

from ...chunk.gi01 import GaluchatImageDataChunk01Reader
from ...io import BytesReaderFactory, FileReaderFactory, ReaderFactory
from ...math.raster import IReadableRaster, RawRaster
from ...math.rect import GisRect
from .WGSMapSetHeader3 import WGSMapSetHeader3


class GaluchatWGSMapSet3Reader:
    """WGSMapSet/3をチャンク索引なしで先頭から逐次走査するReader。"""

    def __init__(
        self,
        header: WGSMapSetHeader3,
        reader_factory: ReaderFactory,
        chunk_offset: int,
    ):
        self.header = header
        self._reader_factory = reader_factory
        self._chunk_offset = chunk_offset

        west_min: int | None = None
        south_min: int | None = None
        east_max: int | None = None
        north_max: int | None = None
        with reader_factory.create(chunk_offset) as reader:
            for west, south in header.iterMapset():
                chunk = GaluchatImageDataChunk01Reader(reader)
                west_min = west if west_min is None else min(west_min, west)
                south_min = south if south_min is None else min(south_min, south)
                east = west + chunk.width
                north = south + chunk.height
                east_max = east if east_max is None else max(east_max, east)
                north_max = north if north_max is None else max(north_max, north)
                chunk.skipToEnd()

        if (
            west_min is None
            or south_min is None
            or east_max is None
            or north_max is None
        ):
            raise ValueError("WGSMapSet/3 must contain at least one map")
        self._area = GisRect[int](
            west_min,
            south_min,
            east_max - west_min,
            north_max - south_min,
        )

    @classmethod
    def fromBytes(cls, src: bytes) -> "GaluchatWGSMapSet3Reader":
        reader_factory = BytesReaderFactory(src)
        with reader_factory.create() as reader:
            header = WGSMapSetHeader3.unpack(reader)
            chunk_offset = reader.pos
            chunk_name = reader.readAsBytes(4)
            if chunk_name == b"LAYO":
                reader.skipInByte(reader.readMbUInt())
                chunk_offset = reader.pos
                chunk_name = reader.readAsBytes(4)
            if chunk_name != b"GI01":
                raise ValueError("WGSMapSet/3 does not contain a GI01 chunk")
        return cls(header, reader_factory, chunk_offset)

    @classmethod
    def fromFile(
        cls,
        path: str | PathLike[str],
        buffer_size: int = 8192,
    ) -> "GaluchatWGSMapSet3Reader":
        reader_factory = FileReaderFactory(path, buffer_size=buffer_size)
        with reader_factory.create() as reader:
            header = WGSMapSetHeader3.unpack(reader)
            chunk_offset = reader.pos
            chunk_name = reader.readAsBytes(4)
            if chunk_name == b"LAYO":
                reader.skipInByte(reader.readMbUInt())
                chunk_offset = reader.pos
                chunk_name = reader.readAsBytes(4)
            if chunk_name != b"GI01":
                raise ValueError("WGSMapSet/3 does not contain a GI01 chunk")
        return cls(header, reader_factory, chunk_offset)

    @property
    def unitInvX(self) -> int:
        return self.header.unit_inv_x

    @property
    def unitInvY(self) -> int:
        return self.header.unit_inv_y

    @property
    def numOfMaps(self) -> int:
        return self.header.numofmap

    @property
    def area(self) -> GisRect[int]:
        return self._area

    @property
    def areaOfWgs(self) -> GisRect[float]:
        area = self.area
        return GisRect[float](
            area.x / self.header.unit_inv_x,
            area.y / self.header.unit_inv_y,
            area.width / self.header.unit_inv_x,
            area.height / self.header.unit_inv_y,
        )

    def readWgsPoint(self, ilon: int, ilat: int) -> int | None:
        result = None
        with self._reader_factory.create(self._chunk_offset) as reader:
            for west, south in self.header.iterMapset():
                chunk = GaluchatImageDataChunk01Reader(reader)
                if not (
                    west <= ilon < west + chunk.width
                    and south <= ilat < south + chunk.height
                ):
                    chunk.skipToEnd()
                    continue
                value = chunk.readPoint(ilon - west, ilat - south)
                if value != 0:
                    return value
                result = 0
                chunk.skipToEnd()
        return result

    def readWgsPointf(self, lon: float, lat: float) -> int | None:
        return self.readWgsPoint(
            round(lon * self.header.unit_inv_x),
            round(lat * self.header.unit_inv_y),
        )

    def readRect(self, lx: int, ly: int, width: int, height: int) -> IReadableRaster:
        area = self.area
        return self.readWgsRect(
            GisRect[int](area.x + lx, area.y + ly, width, height)
        )

    def readWgsRect(self, target: GisRect[int]) -> IReadableRaster:
        class ZeroFilter:
            def __init__(self, parent):
                self._parent = parent

            @property
            def width(self):
                return self._parent.width

            @property
            def height(self):
                return self._parent.height

            def get(self, x: int, y: int) -> int:
                return self._parent.get(x, y)

            def set(self, x: int, y: int, v: int):
                if v != 0:
                    self._parent.set(x, y, v)

        dest = RawRaster.createRaster(target.width, target.height)
        filtered = ZeroFilter(dest)
        with self._reader_factory.create(self._chunk_offset) as reader:
            for west, south in self.header.iterMapset():
                chunk = GaluchatImageDataChunk01Reader(reader)
                area = GisRect[int].createWithNSEW(
                    south + chunk.height,
                    south,
                    west + chunk.width,
                    west,
                )
                crossed = area.cross(target)
                if crossed is None:
                    chunk.skipToEnd()
                    continue
                temp = RawRaster.createRaster(crossed.width, crossed.height)
                chunk.readRect(crossed.x - west, crossed.y - south, temp)
                for y in range(crossed.height):
                    for x in range(crossed.width):
                        filtered.set(
                            crossed.x - target.x + x,
                            crossed.y - target.y + y,
                            temp.get(x, y),
                        )
                chunk.skipToEnd()
        return dest

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
        return self.readWgsRect(self.area)
