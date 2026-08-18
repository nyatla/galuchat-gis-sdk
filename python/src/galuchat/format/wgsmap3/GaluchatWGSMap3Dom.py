from galuchat.chunk.gi01 import GaluchatImageDataChunk01
from galuchat.io import BytesBufferReader, BytesWriter
from galuchat.math.rect import GisRect

from ..wgsmap2 import WGSMapHeader


class GaluchatWGSMap3Dom:
    def __init__(self, header: WGSMapHeader, chunk: GaluchatImageDataChunk01):
        self.header = header
        self.chunk = chunk

    @property
    def area(self) -> GisRect[int]:
        h = self.header
        c = self.chunk
        return GisRect[int].createWithNSEW(h.south + c.height, h.south, h.west + c.width, h.west)

    def toRaster(self):
        return self.chunk.toRaster()

    @classmethod
    def pack(cls, src: "GaluchatWGSMap3Dom") -> bytes:
        writer = BytesWriter()
        WGSMapHeader.pack(src.header, writer)
        GaluchatImageDataChunk01.pack(src.chunk, writer)
        return bytes(writer.buffer)

    @classmethod
    def unpack(cls, src: bytes) -> "GaluchatWGSMap3Dom":
        reader = BytesBufferReader(src)
        header = WGSMapHeader.unpack(reader)
        chunk = GaluchatImageDataChunk01.unpack(reader)
        return cls(header, chunk)
