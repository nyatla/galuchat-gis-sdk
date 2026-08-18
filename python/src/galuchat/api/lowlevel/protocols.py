from __future__ import annotations

from typing import Iterable, Iterator, Protocol

from .types import IRaster, LonLatPoint, LonLatRect, PixelPoint, PixelRect, RectAnchor


class IWgsMapset3Reader(Protocol):
    @property
    def unitInvX(self) -> int:
        ...

    @property
    def unitInvY(self) -> int:
        ...

    @property
    def mapCount(self) -> int:
        ...

    @property
    def pixelBounds(self) -> PixelRect:
        ...

    @property
    def lonLatBounds(self) -> LonLatRect:
        ...

    @property
    def metadata(self) -> str | None:
        ...

    def wgsToPoint(self, lon: float, lat: float) -> PixelPoint:
        ...

    def pointToWgs(self, x: int, y: int) -> LonLatPoint:
        ...

    def containsPoint(self, x: int, y: int) -> bool:
        ...

    def containsWgsPoint(self, lon: float, lat: float) -> bool:
        ...

    def readPoint(self, x: int, y: int) -> int | None:
        ...

    def readWgsPoint(self, lon: float, lat: float) -> int | None:
        ...

    def readRect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        anchor: RectAnchor | None = None,
    ) -> IRaster:
        ...

    def readWgsRect(
        self,
        lon: float,
        lat: float,
        width: int,
        height: int,
        anchor: RectAnchor | None = None,
    ) -> IRaster:
        ...

    def readWgsBounds(
        self,
        west: float,
        south: float,
        east: float,
        north: float,
    ) -> IRaster:
        ...


class IWordBookReader(Protocol):
    @property
    def recordCount(self) -> int:
        ...

    @property
    def depth(self) -> int:
        ...

    def readStringSetByCode(self, code: int) -> tuple[str, ...] | None:
        ...

    def readStringSetByIndex(self, index: int) -> tuple[str, ...]:
        ...

    def iterStringSetsByCodes(
        self,
        codes: Iterable[int],
    ) -> Iterator[tuple[str, ...] | None]:
        ...

    def iterStringSetsByIndices(
        self,
        indices: Iterable[int],
    ) -> Iterator[tuple[str, ...]]:
        ...

