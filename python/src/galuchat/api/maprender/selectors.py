from __future__ import annotations

from dataclasses import dataclass

from ..lowlevel import IRaster, IWgsMapset3Reader, RectAnchor


@dataclass(frozen=True)
class PointRectSelector:
    x: int
    y: int
    width: int
    height: int
    anchor: RectAnchor | None = None

    def readRaster(self, reader: IWgsMapset3Reader) -> IRaster:
        return reader.readRect(
            self.x,
            self.y,
            self.width,
            self.height,
            self.anchor,
        )


@dataclass(frozen=True)
class WgsPointRectSelector:
    lon: float
    lat: float
    width: int
    height: int
    anchor: RectAnchor | None = None

    def readRaster(self, reader: IWgsMapset3Reader) -> IRaster:
        return reader.readWgsRect(
            self.lon,
            self.lat,
            self.width,
            self.height,
            self.anchor,
        )


@dataclass(frozen=True)
class WgsBoundsSelector:
    west: float
    south: float
    east: float
    north: float

    def readRaster(self, reader: IWgsMapset3Reader) -> IRaster:
        return reader.readWgsBounds(
            self.west,
            self.south,
            self.east,
            self.north,
        )


@dataclass(frozen=True)
class FullMapsetSelector:
    def readRaster(self, reader: IWgsMapset3Reader) -> IRaster:
        bounds = reader.pixelBounds
        return reader.readRect(
            bounds.x,
            bounds.y,
            bounds.width,
            bounds.height,
        )
