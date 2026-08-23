from __future__ import annotations

from ...io import ABytesReader
from .GisWordBookHeaderChunk import GisWordBookHeaderChunk
from ..core.constants import GISWORDBOOK_VERSION


class GisWordBookHeaderChunkReader:
    def __init__(self, reader: ABytesReader, size: int):
        start = reader.pos
        version = reader.readBytesAsBStr(16)
        if version != GISWORDBOOK_VERSION:
            raise ValueError(f"invalid GisWordBook version: {version!r}")
        metadata_size = reader.readMbUInt()
        self.metadata = None if metadata_size == 0 else reader.readAsBytes(metadata_size).decode("utf-8")
        if reader.pos - start != size:
            raise ValueError("GW00 has trailing bytes")

    def toChunk(self) -> GisWordBookHeaderChunk:
        return GisWordBookHeaderChunk(metadata=self.metadata)


def read_gw00_data(reader: ABytesReader, size: int) -> GisWordBookHeaderChunk:
    return GisWordBookHeaderChunkReader(reader, size).toChunk()
