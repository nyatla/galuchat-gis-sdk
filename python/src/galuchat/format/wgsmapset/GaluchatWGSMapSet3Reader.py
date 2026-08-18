from ...chunk import Chunk
from ...chunk.gi01 import GaluchatImageDataChunk01Reader
from ...io import BytesBufferReader
from ...math.raster import IReadableRaster, RawRaster
from ...math.rect import GisRect
from .WGSMapSetHeader3 import WGSMapSetHeader3


class GaluchatWGSMapSet3Reader:
    def __init__(self, header: WGSMapSetHeader3, src: bytes, chunk_offset: int):
        self.header = header
        self._src = src
        self._chunk_offset = chunk_offset

    @classmethod
    def unpack(cls, src: bytes) -> "GaluchatWGSMapSet3Reader":
        reader = BytesBufferReader(src)
        header = WGSMapSetHeader3.unpack(reader)
        if src[reader.pos:reader.pos + 4] == b"LAYO":
            Chunk.unpack(reader)
        return cls(header, src, reader.pos)

    @property
    def unitInvX(self) -> int:
        return self.header.unit_inv_x

    @property
    def unitInvY(self) -> int:
        return self.header.unit_inv_y

    @property
    def numOfMaps(self) -> int:
        return self.header.numofmap

    def _chunkReaderAt(self, idx: int) -> GaluchatImageDataChunk01Reader:
        if idx < 0 or idx >= self.header.numofmap:
            raise IndexError(idx)
        offset = self._chunk_offset
        reader = None
        for _ in range(idx + 1):
            reader = GaluchatImageDataChunk01Reader(self._src, offset)
            offset += reader.chunk_size
        return reader

    @property
    def area(self) -> GisRect[int]:
        areas = []
        offset = self._chunk_offset
        for west, south in self.header.mapset:
            chunk = GaluchatImageDataChunk01Reader(self._src, offset)
            offset += chunk.chunk_size
            areas.append(GisRect[int].createWithNSEW(
                south + chunk.height,
                south,
                west + chunk.width,
                west,
            ))
        return GisRect[int].marge(areas)

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
        offset = self._chunk_offset
        result = None
        for west, south in self.header.mapset:
            chunk = GaluchatImageDataChunk01Reader(self._src, offset)
            offset += chunk.chunk_size
            if not (west <= ilon < west + chunk.width and south <= ilat < south + chunk.height):
                continue
            value = chunk.readPoint(ilon - west, ilat - south)
            if value != 0:
                return value
            result = 0
        return result

    def readWgsPointf(self, lon: float, lat: float) -> int | None:
        return self.readWgsPoint(
            round(lon * self.header.unit_inv_x),
            round(lat * self.header.unit_inv_y),
        )

    def readRect(self, lx: int, ly: int, width: int, height: int) -> IReadableRaster:
        return self.readWgsRect(GisRect[int](self.area.x + lx, self.area.y + ly, width, height))

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
        offset = self._chunk_offset
        for west, south in self.header.mapset:
            chunk = GaluchatImageDataChunk01Reader(self._src, offset)
            offset += chunk.chunk_size
            area = GisRect[int].createWithNSEW(south + chunk.height, south, west + chunk.width, west)
            crossed = area.cross(target)
            if crossed is None:
                continue
            temp = RawRaster.createRaster(crossed.width, crossed.height)
            chunk.readRect(crossed.x - west, crossed.y - south, temp)
            for y in range(crossed.height):
                for x in range(crossed.width):
                    filtered.set(crossed.x - target.x + x, crossed.y - target.y + y, temp.get(x, y))
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

    def getChunkReader(self, idx: int) -> GaluchatImageDataChunk01Reader:
        return self._chunkReaderAt(idx)
