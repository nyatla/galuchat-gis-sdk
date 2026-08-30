from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ...chunk import Chunk
from ...io import ABytesReader, ABytesWriter, BytesBufferReader, BytesWriter


@dataclass(frozen=True)
class WGSMapHeader:
    """Current WGSMap/3 GLCH header."""

    VERSION: ClassVar[bytes] = b"WGSMap/3"
    CHUNK_NAME: ClassVar[bytes] = b"GLCH"

    unit_inv_x: int
    unit_inv_y: int
    west: int
    south: int
    metadata: str | None = None

    @classmethod
    def unpack(cls, src: ABytesReader) -> "WGSMapHeader":
        chunk = Chunk.unpack(src)
        if chunk.name != cls.CHUNK_NAME:
            raise ValueError("WGSMap/3 must start with GLCH")
        reader = BytesBufferReader(chunk.data)
        version = reader.readBytesAsBStr(16)
        if version != cls.VERSION:
            raise ValueError("WGSMap/3 parser requires WGSMap/3 header")
        unit_inv_x = reader.readMbUInt()
        unit_inv_y = reader.readMbUInt()
        west = reader.readMbInt()
        south = reader.readMbInt()
        metadata_size = reader.readMbUInt()
        metadata = (
            None
            if metadata_size == 0
            else reader.readAsBytes(metadata_size).decode("utf-8")
        )
        if reader.pos != len(chunk.data):
            raise ValueError("WGSMap/3 header has trailing bytes")
        return cls(unit_inv_x, unit_inv_y, west, south, metadata)

    @classmethod
    def pack(cls, src: "WGSMapHeader", dest: ABytesWriter) -> None:
        payload = BytesWriter()
        payload.writeBytesAsBStr(cls.VERSION, 16)
        payload.writeMbUInt(src.unit_inv_x)
        payload.writeMbUInt(src.unit_inv_y)
        payload.writeMbInt(src.west)
        payload.writeMbInt(src.south)
        if src.metadata is None:
            payload.writeMbUInt(0)
        else:
            metadata = src.metadata.encode("utf-8")
            payload.writeMbUInt(len(metadata))
            payload.writeBytes(metadata)
        Chunk.pack(cls.CHUNK_NAME, payload.buffer, dest)

    @classmethod
    def createNew(
        cls,
        unit_inv_x: int,
        unit_inv_y: int,
        west: int,
        south: int,
        metadata: str | None,
    ) -> "WGSMapHeader":
        return cls(unit_inv_x, unit_inv_y, west, south, metadata)
