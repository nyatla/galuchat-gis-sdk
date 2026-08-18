from __future__ import annotations

from typing import Iterable, Iterator

from ...format.wgsmapset import GaluchatWGSMapSet3Reader
from ...math.rect import GisRect
from ...wordbook import GaluchatGisWordBookReader
from .types import IRaster, LonLatPoint, LonLatRect, PixelPoint, PixelRect, RectAnchor


class WgsMapset3ReaderAdapter:
    def __init__(self, reader: GaluchatWGSMapSet3Reader):
        self._reader = reader

    @classmethod
    def fromBytes(cls, src: bytes) -> "WgsMapset3ReaderAdapter":
        return cls(GaluchatWGSMapSet3Reader.unpack(src))

    @classmethod
    def fromFile(cls, path: str) -> "WgsMapset3ReaderAdapter":
        with open(path, "rb") as fp:
            return cls.fromBytes(fp.read())

    @property
    def unitInvX(self) -> int:
        return self._reader.unitInvX

    @property
    def unitInvY(self) -> int:
        return self._reader.unitInvY

    @property
    def mapCount(self) -> int:
        return self._reader.numOfMaps

    @property
    def pixelBounds(self) -> PixelRect:
        area = self._reader.area
        return PixelRect(area.x, area.y, area.width, area.height)

    @property
    def lonLatBounds(self) -> LonLatRect:
        area = self._reader.areaOfWgs
        return LonLatRect(area.west, area.south, area.east, area.north)

    @property
    def metadata(self) -> str | None:
        return self._reader.header.metadata

    def wgsToPoint(self, lon: float, lat: float) -> PixelPoint:
        return PixelPoint(
            round(lon * self.unitInvX),
            round(lat * self.unitInvY),
        )

    def pointToWgs(self, x: int, y: int) -> LonLatPoint:
        return LonLatPoint(
            x / self.unitInvX,
            y / self.unitInvY,
        )

    def containsPoint(self, x: int, y: int) -> bool:
        bounds = self.pixelBounds
        return (
            bounds.x <= x < bounds.x + bounds.width
            and bounds.y <= y < bounds.y + bounds.height
        )

    def containsWgsPoint(self, lon: float, lat: float) -> bool:
        point = self.wgsToPoint(lon, lat)
        return self.containsPoint(point.x, point.y)

    def readPoint(self, x: int, y: int) -> int | None:
        return self._reader.readWgsPoint(x, y)

    def readWgsPoint(self, lon: float, lat: float) -> int | None:
        return self._reader.readWgsPointf(lon, lat)

    def readRect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        anchor: RectAnchor | None = None,
    ) -> IRaster:
        left, bottom = _resolve_anchor(x, y, width, height, anchor)
        return self._reader.readWgsRect(GisRect[int](left, bottom, width, height))

    def readWgsRect(
        self,
        lon: float,
        lat: float,
        width: int,
        height: int,
        anchor: RectAnchor | None = None,
    ) -> IRaster:
        point = self.wgsToPoint(lon, lat)
        return self.readRect(point.x, point.y, width, height, anchor)

    def readWgsBounds(
        self,
        west: float,
        south: float,
        east: float,
        north: float,
    ) -> IRaster:
        southwest = self.wgsToPoint(west, south)
        northeast = self.wgsToPoint(east, north)
        return self.readRect(
            southwest.x,
            southwest.y,
            northeast.x - southwest.x,
            northeast.y - southwest.y,
        )


class GisWordBookReaderAdapter:
    def __init__(self, reader: GaluchatGisWordBookReader):
        self._reader = reader

    @classmethod
    def fromBytes(cls, src: bytes) -> "GisWordBookReaderAdapter":
        return cls(GaluchatGisWordBookReader.unpack(src))

    @classmethod
    def fromFile(cls, path: str) -> "GisWordBookReaderAdapter":
        with open(path, "rb") as fp:
            return cls.fromBytes(fp.read())

    @property
    def recordCount(self) -> int:
        return self._reader.record_count

    @property
    def depth(self) -> int:
        return self._reader.depth

    def readStringSetByCode(self, code: int) -> tuple[str, ...] | None:
        if code <= 0:
            return None
        return self.readStringSetByIndex(code - 1)

    def readStringSetByIndex(self, index: int) -> tuple[str, ...]:
        return tuple(self._reader.readStringSet(index))

    def iterStringSetsByCodes(
        self,
        codes: Iterable[int],
    ) -> Iterator[tuple[str, ...] | None]:
        run: list[int] = []
        for code in codes:
            if code <= 0:
                if run:
                    yield from self.iterStringSetsByIndices(run)
                    run.clear()
                yield None
            else:
                run.append(code - 1)
        if run:
            yield from self.iterStringSetsByIndices(run)

    def iterStringSetsByIndices(
        self,
        indices: Iterable[int],
    ) -> Iterator[tuple[str, ...]]:
        for string_set in self._reader.iterStringSetsFor(indices):
            yield tuple(string_set)


def _resolve_anchor(
    x: int,
    y: int,
    width: int,
    height: int,
    anchor: RectAnchor | None,
) -> tuple[int, int]:
    if width < 0 or height < 0:
        raise ValueError("width and height must be non-negative")
    if anchor is None or anchor is RectAnchor.SOUTHWEST:
        return x, y
    if anchor is RectAnchor.CENTER:
        return x - width // 2, y - height // 2
    if anchor is RectAnchor.NORTHWEST:
        return x, y - height
    if anchor is RectAnchor.NORTHEAST:
        return x - width, y - height
    if anchor is RectAnchor.SOUTHEAST:
        return x - width, y
    raise ValueError(f"unsupported RectAnchor: {anchor!r}")
