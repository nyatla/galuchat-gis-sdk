"""Reverse geocode a few points around the Imperial Palace.

Run from the repository root:

    python3 getstarted/reverse_geocode_imperial_palace.py
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DATA = ROOT / "getstarted" / "data"

sys.path.insert(0, str(SRC))

from galuchat.api.lowlevel import GisWordBookReaderAdapter, WgsMapset3ReaderAdapter


MAPSET_PATH = DATA / "N03-20240101-grid-4096-1000.remap.wgsmapset.glc"
WORDBOOK_PATH = DATA / "N03-20240101.giswordbook"

POINTS = (
    ("Imperial Palace", 139.7528, 35.6852),
    ("Tokyo Station", 139.7671, 35.6812),
    ("Shinjuku Station", 139.7006, 35.6896),
)


def format_path(path: tuple[str, ...] | None) -> str:
    if path is None:
        return "(not found)"
    return " / ".join(component for component in path if component)


def main() -> None:
    mapset_path = Path(sys.argv[1]) if len(sys.argv) > 1 else MAPSET_PATH
    wordbook_path = Path(sys.argv[2]) if len(sys.argv) > 2 else WORDBOOK_PATH
    mapset = WgsMapset3ReaderAdapter.fromFile(str(mapset_path))
    wordbook = GisWordBookReaderAdapter.fromFile(str(wordbook_path))

    print(f"mapset: unitInv=({mapset.unitInvX}, {mapset.unitInvY}), maps={mapset.mapCount}")
    print(
        "bounds: "
        f"lon {mapset.lonLatBounds.west:.3f}..{mapset.lonLatBounds.east:.3f}, "
        f"lat {mapset.lonLatBounds.south:.3f}..{mapset.lonLatBounds.north:.3f}"
    )
    print(f"wordbook: records={wordbook.recordCount}, depth={wordbook.depth}")
    print()

    for label, lon, lat in POINTS:
        code = mapset.readWgsPoint(lon, lat)
        path = wordbook.readStringSetByCode(code) if code is not None else None
        print(f"{label}: lon={lon:.4f}, lat={lat:.4f}")
        print(f"  code: {code}")
        print(f"  path: {format_path(path)}")


if __name__ == "__main__":
    main()
