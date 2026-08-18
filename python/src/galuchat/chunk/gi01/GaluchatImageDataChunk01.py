from typing import List
import math
from enum import Enum

from ...io import ABytesReader, ABytesWriter, BytesBufferReader, BytesWriter, Lzss
from ...io.MBIntDef import MBIntDef
from ...math.raster import RawRaster, Raster
from ..Chunk import Chunk
from .GI01Format import (
    BlockHeader as GI01BlockHeader,
    CC_LZSS,
    CC_RAW,
    CC_RAWS,
    CHUNK_NAME as GI01_CHUNK_NAME,
)
from .nodes.NodeDeserializer import DeltaNodeDeserializer, NodeDeserializer
from .nodes.NodeSerializer import DeltaNodeSerializer, NodeSerializer
from .nodes.node import BaseNode


class GaluchatImageDataChunk01(Chunk):
    """GI01形式の画像チャンク。"""

    CHUNK_NAME = GI01_CHUNK_NAME

    class PaletteValueMode(Enum):
        """カスケードパレット更新値列の記録方式。"""

        ABSOLUTE = "off"
        DELTA = "on"
        AUTO = "auto"

        @classmethod
        def normalize(cls, value: "GaluchatImageDataChunk01.PaletteValueMode | str") -> "GaluchatImageDataChunk01.PaletteValueMode":
            if isinstance(value, cls):
                return value
            return cls(value)

    class Block:
        """square_unit四方のノードと任意の追加圧縮を保持する。"""

        CC_RAW = CC_RAW
        CC_RAWS = CC_RAWS
        CC_LZSS = CC_LZSS
        BlockHeader = GI01BlockHeader

        def __init__(self, data: BaseNode):
            self.data = data

        @classmethod
        def deserialize(cls, square_unit: int, src: ABytesReader) -> "GaluchatImageDataChunk01.Block":
            block_header = cls.BlockHeader(src.readByte())
            compression_type = block_header.compressionType
            deserializer = (
                DeltaNodeDeserializer()
                if block_header.paletteDelta
                else NodeDeserializer())
            if compression_type == cls.CC_RAW:
                node = deserializer.deserialize(square_unit, src)
                src.skipToByte()
                return cls(node)
            if compression_type == cls.CC_RAWS:
                size = src.readMbUInt()
                payload = src.readAsBytes(size)
                reader = BytesBufferReader(payload)
                node = deserializer.deserialize(square_unit, reader)
                reader.skipToByte()
                assert reader.pos == len(payload)
                return cls(node)
            if compression_type == cls.CC_LZSS:
                size = src.readMbUInt()
                compressed = src.readAsBytes(size)
                data = Lzss(256).decompressFromBytes(compressed)
                reader = BytesBufferReader(data)
                node = deserializer.deserialize(square_unit, reader)
                reader.skipToByte()
                assert reader.pos == len(data)
                return cls(node)
            raise ValueError(f"unsupported GI01 block compression type: {compression_type}")

        @classmethod
        def desirialize(cls, square_unit: int, src: ABytesReader) -> "GaluchatImageDataChunk01.Block":
            return cls.deserialize(square_unit, src)

        def serialize(
            self,
            dest: ABytesWriter,
            compress: bool,
            palette_value_mode: "GaluchatImageDataChunk01.PaletteValueMode | str" = "off",
        ) -> None:
            palette_value_mode = GaluchatImageDataChunk01.PaletteValueMode.normalize(palette_value_mode)
            payloads = []
            if palette_value_mode in (
                GaluchatImageDataChunk01.PaletteValueMode.ABSOLUTE,
                GaluchatImageDataChunk01.PaletteValueMode.AUTO,
            ):
                node_dest = BytesWriter()
                NodeSerializer().serialize(node_dest, self.data)
                payloads.append((bytes(node_dest.buffer), False))
            if palette_value_mode in (
                GaluchatImageDataChunk01.PaletteValueMode.DELTA,
                GaluchatImageDataChunk01.PaletteValueMode.AUTO,
            ):
                node_dest = BytesWriter()
                DeltaNodeSerializer().serialize(node_dest, self.data)
                payloads.append((bytes(node_dest.buffer), True))

            candidate = []
            for payload, is_palette_delta in payloads:
                if len(payload) < 16:
                    candidate.append((self.CC_RAW, 1 + len(payload), payload, is_palette_delta))
                    continue
                candidate.append((
                    self.CC_RAWS,
                    len(payload) + 1 + MBIntDef.sizeOfMbUint(len(payload)),
                    payload,
                    is_palette_delta,
                ))
                if compress:
                    compressed = bytes(Lzss(256).compressToBytes(payload))
                    candidate.append((
                        self.CC_LZSS,
                        len(compressed) + 1 + MBIntDef.sizeOfMbUint(len(compressed)),
                        compressed,
                        is_palette_delta,
                    ))
            compression_type,_,payload,palette_delta=min(
                candidate,
                key=lambda i:(i[1],1 if i[3] else 0,i[0]))
            

            dest.writeByte(self.BlockHeader.create(compression_type, palette_delta).byte1)
            if compression_type != self.CC_RAW:
                dest.writeMbUInt(len(payload))
            dest.writeBytes(payload)

        def extractToRaster(self, x: int, y: int, dest: Raster) -> None:
            self.data.toRaster(dest, x, y)

    def __init__(self, src: ABytesReader):
        super().__init__(src)
        assert self.name == self.CHUNK_NAME
        reader = BytesBufferReader(self.data)
        self.width = reader.readMbUInt()
        self.height = reader.readMbUInt()
        self.square_unit = 2 ** reader.readByte()
        self._imgdata_offset = reader.pos

    def _toUnit(self, value: int) -> int:
        return (value + self.square_unit - 1) // self.square_unit

    @classmethod
    def _makeChunkDataField(
        cls,
        width: int,
        height: int,
        square_unit: int,
        blocks: List["GaluchatImageDataChunk01.Block"],
        dbg_no_compress: bool,
        palette_value_mode: "PaletteValueMode | str" = PaletteValueMode.ABSOLUTE,
    ) -> bytes:
        writer = BytesWriter()
        writer.writeMbUInts([width, height])
        writer.writeByte(round(math.log2(square_unit)))
        for block in blocks:
            block.serialize(writer, not dbg_no_compress, palette_value_mode)
        return bytes(writer.buffer)

    @classmethod
    def createFromBlocks(
        cls,
        width: int,
        height: int,
        square_unit: int,
        blocks: List["GaluchatImageDataChunk01.Block"],
        no_compress: bool = False,
        palette_value_mode: "PaletteValueMode | str" = PaletteValueMode.ABSOLUTE,
    ) -> "GaluchatImageDataChunk01":
        """Create a GI01 DOM from an already selected block/node structure.

        This method serializes the supplied representation as-is.
        """
        data = cls._makeChunkDataField(
            width,
            height,
            square_unit,
            blocks,
            no_compress,
            palette_value_mode,
        )
        writer = BytesWriter()
        Chunk.pack(cls.CHUNK_NAME, data, writer)
        return cls(BytesBufferReader(writer.buffer))

    @classmethod
    def unpack(cls, src: ABytesReader) -> "GaluchatImageDataChunk01":
        return cls(src)

    @classmethod
    def pack(cls, src: "GaluchatImageDataChunk01", dest: ABytesWriter):
        return Chunk.pack(cls.CHUNK_NAME, src.data, dest)

    @property
    def numOfHUnits(self) -> int:
        return self._toUnit(self.width)

    @property
    def numOfVUnits(self) -> int:
        return self._toUnit(self.height)

    def toNodes(self) -> List[BaseNode]:
        reader = BytesBufferReader(self.data)
        reader.skipInByte(self._imgdata_offset)
        return [
            self.Block.deserialize(self.square_unit, reader).data
            for _ in range(self.numOfHUnits * self.numOfVUnits)
        ]

    def toRaster(self) -> Raster:
        horizontal_units = self.numOfHUnits
        vertical_units = self.numOfVUnits
        raster = RawRaster.createRaster(
            horizontal_units * self.square_unit,
            vertical_units * self.square_unit,
        )
        for index, node in enumerate(self.toNodes()):
            node.toRaster(
                raster,
                index % horizontal_units * self.square_unit,
                index // horizontal_units * self.square_unit,
            )
        return raster.createSubRaster(0, 0, self.width, self.height)
