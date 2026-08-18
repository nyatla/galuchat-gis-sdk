from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...math.raster import IReadableRaster as IRaster


class RectAnchor(Enum):
    CENTER = "center"
    NORTHWEST = "northwest"
    SOUTHWEST = "southwest"
    NORTHEAST = "northeast"
    SOUTHEAST = "southeast"


@dataclass(frozen=True)
class PixelPoint:
    x: int
    y: int


@dataclass(frozen=True)
class LonLatPoint:
    lon: float
    lat: float


@dataclass(frozen=True)
class PixelRect:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class LonLatRect:
    west: float
    south: float
    east: float
    north: float

