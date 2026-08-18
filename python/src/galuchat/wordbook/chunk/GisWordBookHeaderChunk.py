from __future__ import annotations

from dataclasses import dataclass

from ...io import BytesBufferReader, BytesWriter
from ..core.constants import GISWORDBOOK_VERSION


@dataclass(frozen=True)
class GisWordBookHeaderChunk:
    metadata: str | None = None


def write_gw00_data(header: GisWordBookHeaderChunk) -> bytes:
    writer = BytesWriter()
    writer.writeBytesAsBStr(GISWORDBOOK_VERSION, 16)
    if header.metadata is None:
        writer.writeMbUInt(0)
    else:
        metadata = header.metadata.encode("utf-8")
        writer.writeMbUInt(len(metadata))
        writer.writeBytes(metadata)
    return bytes(writer.buffer)


def parse_gw00_data(data: bytes) -> GisWordBookHeaderChunk:
    reader = BytesBufferReader(data)
    version = reader.readBytesAsBStr(16)
    if version != GISWORDBOOK_VERSION:
        raise ValueError(f"invalid GisWordBook version: {version!r}")
    metadata_size = reader.readMbUInt()
    metadata = None if metadata_size == 0 else reader.readAsBytes(metadata_size).decode("utf-8")
    if reader.pos != len(data):
        raise ValueError("GW00 has trailing bytes")
    return GisWordBookHeaderChunk(metadata=metadata)

