from __future__ import annotations

from dataclasses import dataclass

from ...io import BytesBufferReader


@dataclass(frozen=True)
class MappedChunk:
    name: bytes
    data_start: int
    size: int


def read_mapped_chunk(reader: BytesBufferReader, source_size: int) -> MappedChunk:
    name = reader.readAsBytes(4)
    size = reader.readMbUInt()
    data_start = reader.pos
    if data_start + size > source_size:
        raise ValueError("chunk data exceeds source size")
    reader.skipInByte(size)
    return MappedChunk(name=name, data_start=data_start, size=size)
