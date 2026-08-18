from __future__ import annotations

from ...io import BytesBufferReader
from .WordBookHeaderChunk import WordBookHeaderChunk
from ..core.constants import WORDBOOK_VERSION


class WordBookHeaderChunkReader:
    def __init__(self, src: bytes, offset: int, size: int):
        reader = BytesBufferReader(src, offset=offset)
        version = reader.readBytesAsBStr(16)
        if version != WORDBOOK_VERSION:
            raise ValueError(f"invalid WordBook version: {version!r}")
        metadata_size = reader.readMbUInt()
        self.metadata = None if metadata_size == 0 else reader.readAsBytes(metadata_size).decode("utf-8")
        if reader.pos != size:
            raise ValueError("NM00 has trailing bytes")

    def toChunk(self) -> WordBookHeaderChunk:
        return WordBookHeaderChunk(metadata=self.metadata)


def parse_mapped_nm00_data(src: bytes, offset: int, size: int) -> WordBookHeaderChunk:
    return WordBookHeaderChunkReader(src, offset, size).toChunk()
