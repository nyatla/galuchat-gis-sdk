from __future__ import annotations

from typing import Protocol, TypeVar

from ..lowlevel import IRaster, IWgsMapset3Reader
from .types import MapEdgeRenderOptions, MapFillRenderOptions, MapImageRenderOptions

OptionsT = TypeVar("OptionsT")
ImageT = TypeVar("ImageT")


class IWgsMapset3Selector(Protocol):
    def readRaster(self, reader: IWgsMapset3Reader) -> IRaster:
        ...


class IMapRender(Protocol[OptionsT, ImageT]):
    @property
    def defaultOptions(self) -> OptionsT:
        ...

    def render(
        self,
        reader: IWgsMapset3Reader,
        selector: IWgsMapset3Selector,
        options: OptionsT | None = None,
    ) -> ImageT:
        ...


class IMapFillRenderer(
    IMapRender[MapFillRenderOptions, ImageT],
    Protocol[ImageT],
):
    ...


class IMapEdgeRenderer(
    IMapRender[MapEdgeRenderOptions, ImageT],
    Protocol[ImageT],
):
    ...


class IMapImageRenderer(
    IMapRender[MapImageRenderOptions, ImageT],
    Protocol[ImageT],
):
    ...
