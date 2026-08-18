from typing import List, Tuple

from ...chunk import Chunk
from ...io import ABytesReader, ABytesWriter, BytesBufferReader, BytesWriter


class WGSMapSetHeader3(Chunk):
    VERSION = b"WGSMapSet/3"
    CHUNK_NAME = b"GLCH"

    def __init__(self, src: ABytesReader):
        super().__init__(src)
        self._parse()

    def _parse(self):
        assert self.name == self.CHUNK_NAME
        reader = BytesBufferReader(self.data)
        version = reader.readBytesAsBStr(16)
        if version != self.VERSION:
            raise ValueError(f"Invalid version:'{version.decode()}'")
        self.unit_inv_x = reader.readMbUInt()
        self.unit_inv_y = reader.readMbUInt()
        metadata_size = reader.readMbUInt()
        self.metadata = None if metadata_size == 0 else reader.readAsBytes(metadata_size).decode()
        self.numofmap = reader.readMbUInt()
        self.tbl_offset = reader.pos

    @property
    def mapset(self) -> List[Tuple[int, int]]:
        reader = BytesBufferReader(self.data)
        reader.skipInByte(self.tbl_offset)
        return [(reader.readMbInt(), reader.readMbInt()) for _ in range(self.numofmap)]

    @classmethod
    def unpack(cls, src: ABytesReader) -> "WGSMapSetHeader3":
        return cls(src)

    @classmethod
    def fromChunk(cls, chunk: Chunk) -> "WGSMapSetHeader3":
        self = cls.__new__(cls)
        object.__setattr__(self, "_name", chunk.name)
        object.__setattr__(self, "_data", chunk.data)
        self._parse()
        return self

    @classmethod
    def pack(cls, src: "WGSMapSetHeader3", dest: ABytesWriter):
        return Chunk.pack(cls.CHUNK_NAME, src.data, dest)

    @classmethod
    def createNew(
        cls,
        unit_inv_x: int,
        unit_inv_y: int,
        latlons: List[Tuple[int, int]],
        metadata: str | None,
    ) -> "WGSMapSetHeader3":
        writer = BytesWriter()
        writer.writeBytesAsBStr(cls.VERSION, 16)
        writer.writeMbUInt(unit_inv_x)
        writer.writeMbUInt(unit_inv_y)
        if metadata is None:
            writer.writeMbUInt(0)
        else:
            payload = metadata.encode()
            writer.writeMbUInt(len(payload))
            writer.writeBytes(payload)
        writer.writeMbUInt(len(latlons))
        for west, south in latlons:
            writer.writeMbInt(west)
            writer.writeMbInt(south)
        chunk_writer = BytesWriter()
        Chunk.pack(cls.CHUNK_NAME, writer.buffer, chunk_writer)
        return cls(BytesBufferReader(chunk_writer.buffer))
