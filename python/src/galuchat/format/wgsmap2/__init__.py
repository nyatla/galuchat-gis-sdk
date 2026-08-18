"""WGSMap/2 + GI00 format helpers."""

from .WGSMapHeader import WGSMapHeader

__all__ = ["WGSMapHeader", "GaluchatWGSMapDom", "GaluchatWGSMapReader"]


def __getattr__(name: str):
    """Keep legacy WGSMap/2 exports lazy for Reader-only distributions."""
    if name == "GaluchatWGSMapDom":
        from .GaluchatWGSMapDom import GaluchatWGSMapDom
        globals()[name] = GaluchatWGSMapDom
        return GaluchatWGSMapDom
    if name == "GaluchatWGSMapReader":
        from .GaluchatWGSMapReader import GaluchatWGSMapReader
        globals()[name] = GaluchatWGSMapReader
        return GaluchatWGSMapReader
    raise AttributeError(name)
