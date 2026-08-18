from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
    a: int = 255


@dataclass(frozen=True)
class MapFillRenderOptions:
    defaultColor: Color = Color(0, 0, 0, 0)
    colors: Mapping[int, Color] = field(default_factory=dict)
    colorResolver: Callable[[int, int, int], Color | None] | None = None


@dataclass(frozen=True)
class MapEdgeRenderOptions:
    edgeColor: Color = Color(0, 0, 0, 255)
    backgroundColor: Color = Color(0, 0, 0, 0)
    edgeWidth: int = 1
    includeZero: bool = False


@dataclass(frozen=True)
class MapImageRenderOptions:
    fillOptions: MapFillRenderOptions = field(default_factory=MapFillRenderOptions)
    edgeOptions: MapEdgeRenderOptions | None = field(
        default_factory=MapEdgeRenderOptions
    )
