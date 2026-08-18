"""WGSMapSet format helpers."""

from .GaluchatWGSMapSet3Dom import GaluchatWGSMapSet3Dom
from .GaluchatWGSMapSet3Reader import GaluchatWGSMapSet3Reader
from .WGSMapSetHeader3 import WGSMapSetHeader3

__all__ = [
    "GaluchatWGSMapSet2Dom",
    "GaluchatWGSMapSet2Reader",
    "GaluchatWGSMapSet3Dom",
    "GaluchatWGSMapSet3Reader",
    "GaluchatWGSMapSetDom",
    "GaluchatWGSMapSetReader",
    "WGSMapSetHeader2",
    "WGSMapSetHeader3",
]


def __getattr__(name: str):
    """Keep legacy WGSMapSet/2 exports lazy for current-format SDKs."""
    if name in {"GaluchatWGSMapSet2Dom", "GaluchatWGSMapSetDom"}:
        from .GaluchatWGSMapSet2Dom import GaluchatWGSMapSet2Dom
        globals()["GaluchatWGSMapSet2Dom"] = GaluchatWGSMapSet2Dom
        globals()["GaluchatWGSMapSetDom"] = GaluchatWGSMapSet2Dom
        return GaluchatWGSMapSet2Dom
    if name in {"GaluchatWGSMapSet2Reader", "GaluchatWGSMapSetReader"}:
        from .GaluchatWGSMapSet2Reader import GaluchatWGSMapSet2Reader
        globals()["GaluchatWGSMapSet2Reader"] = GaluchatWGSMapSet2Reader
        globals()["GaluchatWGSMapSetReader"] = GaluchatWGSMapSet2Reader
        return GaluchatWGSMapSet2Reader
    if name == "WGSMapSetHeader2":
        from .WGSMapSetHeader2 import WGSMapSetHeader2
        globals()[name] = WGSMapSetHeader2
        return WGSMapSetHeader2
    raise AttributeError(name)
