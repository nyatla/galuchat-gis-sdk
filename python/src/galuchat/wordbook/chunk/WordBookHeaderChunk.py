from __future__ import annotations

from dataclasses import dataclass

from ...io import BytesBufferReader, BytesWriter
from ..core.constants import WORDBOOK_VERSION


@dataclass(frozen=True)
class WordBookHeaderChunk:
    metadata: str | None = None


def write_nm00_data(header: WordBookHeaderChunk) -> bytes:
    writer = BytesWriter()
    writer.writeBytesAsBStr(WORDBOOK_VERSION, 16)
    if header.metadata is None:
        writer.writeMbUInt(0)
    else:
        metadata = header.metadata.encode("utf-8")
        writer.writeMbUInt(len(metadata))
        writer.writeBytes(metadata)
    return bytes(writer.buffer)


def parse_nm00_data(data: bytes) -> WordBookHeaderChunk:
    reader = BytesBufferReader(data)
    version = reader.readBytesAsBStr(16)
    if version != WORDBOOK_VERSION:
        raise ValueError(f"invalid WordBook version: {version!r}")
    metadata_size = reader.readMbUInt()
    metadata = None if metadata_size == 0 else reader.readAsBytes(metadata_size).decode("utf-8")
    if reader.pos != len(data):
        raise ValueError("NM00 has trailing bytes")
    return WordBookHeaderChunk(metadata=metadata)


WordBookHeader = WordBookHeaderChunk
