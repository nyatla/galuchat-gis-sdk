"""Render a VGA PNG around Narashino city.

Run from the repository root:

    python3 getstarted/render_narashino_vga.py
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DATA = ROOT / "getstarted" / "data"
OUTPUT = ROOT / "getstarted" / "narashino-vga.png"

sys.path.insert(0, str(SRC))

from galuchat.api.lowlevel import RectAnchor, WgsMapset3ReaderAdapter
from galuchat.api.maprender import (
    Color,
    MapEdgeRenderOptions,
    MapFillRenderOptions,
    MapImageRenderOptions,
    PilMapImageRenderer,
    WgsPointRectSelector,
)


MAPSET_PATH = DATA / "N03-20240101-grid-4096-1000.remap.wgsmapset.glc"

NARASHINO_LON = 140.0267
NARASHINO_LAT = 35.6810


def main() -> None:
    mapset_path = Path(sys.argv[1]) if len(sys.argv) > 1 else MAPSET_PATH
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT
    reader = WgsMapset3ReaderAdapter.fromFile(str(mapset_path))
    selector = WgsPointRectSelector(
        lon=NARASHINO_LON,
        lat=NARASHINO_LAT,
        width=640,
        height=480,
        anchor=RectAnchor.CENTER,
    )
    options = MapImageRenderOptions(
        fillOptions=MapFillRenderOptions(
            defaultColor=Color(60, 160, 60, 255),
            colors={
                0: Color(0, 0, 255, 255),
            },
        ),
        edgeOptions=MapEdgeRenderOptions(
            edgeColor=Color(64, 64, 64, 255),
            edgeWidth=1,
            includeZero=True,
        ),
    )

    image = PilMapImageRenderer().render(reader, selector, options)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    print(f"wrote: {output_path}")


if __name__ == "__main__":
    main()
