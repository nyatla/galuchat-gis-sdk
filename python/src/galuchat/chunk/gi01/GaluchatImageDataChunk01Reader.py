from abc import ABC, abstractmethod
from typing import Sequence

from galuchat.io import ABytesReader, BytesBufferReader, BytesIteratorReader, Lzss
from galuchat.math.raster import IWritableRaster, RawRaster, Raster
from galuchat.math.rect import Rect

from .CellHeader import CellHeader
from .GI01Format import BlockHeader, CC_LZSS, CC_RAW, CC_RAWS, CHUNK_NAME
from .PalletHeader import PalletHeader
from .PalletMgr import PalletMgr
from .ContainerPallet import ContainerPallet
from .RlePacketReader import RlePacketReader
from .nodes.node.IndexMapset import IndexMapset


class _PalletValueReader:
    """ブロックのpaletteDelta指定に応じてパレット更新値を読む。"""

    def __init__(self, delta: bool):
        self._delta = delta

    @staticmethod
    def tableSlots(update_table: int, width: int) -> list[int]:
        return [
            slot
            for slot in range(width)
            if update_table & (1 << (width - 1 - slot))
        ]

    def readValuesBySlots(self, src: ABytesReader, pmgr: PalletMgr, slots: Sequence[int]) -> list[int]:
        if self._delta:
            return [
                pmgr.table[slot] + src.readMbInt()
                for slot in slots
            ]
        return src.readMbUInts(len(slots))

    def applyTable(self, src: ABytesReader, pmgr: PalletMgr, update_table: int, width: int) -> None:
        if update_table == 0:
            return
        slots = self.tableSlots(update_table, width)
        pmgr.putByTable(update_table, self.readValuesBySlots(src, pmgr, slots), width)


class NodeReader(ABC):
    """GI01ノードをDOM化せず、関連付けたReaderから1回だけ逐次読出しする。"""

    @abstractmethod
    def readPixel(self, pmgr: PalletMgr, lx: int, ly: int) -> int:
        ...

    @abstractmethod
    def readRect(self, pmgr: PalletMgr, target: Rect[int], dest: IWritableRaster, dest_x: int, dest_y: int):
        ...

    @abstractmethod
    def skipToEnd(self, pmgr: PalletMgr):
        ...


class RawDataNodeReader(NodeReader):
    def __init__(self, header: CellHeader, reader: ABytesReader, resolution: int, pallet_reader: _PalletValueReader):
        assert header.isRaw
        self._header = header
        self._reader = reader
        self._resolution = resolution
        self._pallet_reader = pallet_reader

    def _readPallet(self, pmgr: PalletMgr) -> Sequence[int]:
        header = self._header
        reader = self._reader
        update_low4 = header.rawUpdatePalletTableLow4
        if header.palletResolution == CellHeader.PALLET_4BIT:
            update_table = (reader.readBitsAsInt32(12) << 4) | update_low4
            self._pallet_reader.applyTable(reader, pmgr, update_table, 16)
            return pmgr.get(header.numOfPallet)

        update_width = [2, 4][header.palletResolution]
        if update_low4 >= (1 << update_width):
            raise ValueError("RAW/P pallet update table has reserved bits")
        self._pallet_reader.applyTable(reader, pmgr, update_low4, update_width)
        return pmgr.get(header.numOfPallet)

    def _readValueAt(self, pixel_index: int, pallet: Sequence[int] | None) -> int:
        reader = self._reader
        if pallet is None:
            for _ in range(pixel_index):
                reader.readMbUInt()
            return reader.readMbUInt()
        nbits = ABytesReader.toBitWidth(len(pallet))
        if pixel_index > 0:
            reader.skipBits(pixel_index * nbits)
        return pallet[reader.readBitsAsInt32(nbits)]

    def readPixel(self, pmgr: PalletMgr, lx: int, ly: int) -> int:
        header = self._header
        if not header.hasValidRawReservedBits:
            raise ValueError("RAW CellHeader reserved bits are not zero")
        pixel_index = lx + ly * self._resolution
        if header.palletResolution == CellHeader.PALLET_NBIT:
            return self._readValueAt(pixel_index, None)
        return self._readValueAt(pixel_index, self._readPallet(pmgr))

    def readRect(self, pmgr: PalletMgr, target: Rect[int], dest: IWritableRaster, dest_x: int, dest_y: int):
        header = self._header
        if not header.hasValidRawReservedBits:
            raise ValueError("RAW CellHeader reserved bits are not zero")
        pallet = None if header.palletResolution == CellHeader.PALLET_NBIT else self._readPallet(pmgr)
        resolution = self._resolution
        nbits = None if pallet is None else ABytesReader.toBitWidth(len(pallet))
        for index in range(resolution * resolution):
            if pallet is None:
                value = self._reader.readMbUInt()
            else:
                value = pallet[self._reader.readBitsAsInt32(nbits)]
            lx = index % resolution
            ly = index // resolution
            if target.isInside(lx, ly):
                dest.set((lx - target.x) + dest_x, (ly - target.y) + dest_y, value)

    def skipToEnd(self, pmgr: PalletMgr):
        header = self._header
        if not header.hasValidRawReservedBits:
            raise ValueError("RAW CellHeader reserved bits are not zero")
        pixels = self._resolution ** 2
        if header.palletResolution == CellHeader.PALLET_NBIT:
            self._reader.skipMbUInt(pixels)
            return
        pallet = self._readPallet(pmgr)
        self._reader.skipBits(pixels * ABytesReader.toBitWidth(len(pallet)))


class RleDataNodeReader(NodeReader):
    def __init__(self, header: CellHeader, reader: ABytesReader, resolution: int, pallet_reader: _PalletValueReader):
        assert header.isRle
        self._header = header
        self._reader = reader
        self._resolution = resolution
        self._pallet_reader = pallet_reader

    def _readPacketHeader(self, pmgr: PalletMgr):
        header = self._header
        if not header.hasValidRleReservedBits:
            raise ValueError("RLE CellHeader data encoding is reserved")
        pallet_header = PalletHeader.readFrom(self._reader, header.palletResolution)
        value_bits_add = (
            pallet_header.valueBitsAdd
            if header.rleDataEncoding in (
                CellHeader.RLE_DATA_ENCODING_SHORT_VALUE,
                CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW,
            )
            else 0
        )
        if (
            header.rleDataEncoding == CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW
            and pallet_header.valueBitsAdd > 14
        ):
            raise ValueError("RLE SingleEdgeRow EncodingParams is reserved")
        if (
            header.rleDataEncoding == CellHeader.RLE_DATA_ENCODING_SHORT_VALUE
            and pallet_header.valueBitsAdd > 0x07
        ):
            raise ValueError("RLE ShortValue EncodingParams is reserved")
        if (
            header.rleDataEncoding not in (
                CellHeader.RLE_DATA_ENCODING_SHORT_VALUE,
                CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW,
            )
            and pallet_header.valueBitsAdd != 0
        ):
            raise ValueError("RLE PalletHeader encoding params must be zero")

        update_table = pallet_header.updatePalletTable
        if update_table is not None:
            self._pallet_reader.applyTable(
                self._reader, pmgr, update_table, pallet_header.capacity)
        elif pallet_header.updateCount > 0:
            slots = list(range(pallet_header.updateCount))
            pmgr.put(self._pallet_reader.readValuesBySlots(self._reader, pmgr, slots))

        return pallet_header.initialIndex,value_bits_add

    def _iterRuns(self, pmgr: PalletMgr):
        initial_index,value_bits_add=self._readPacketHeader(pmgr)
        return RlePacketReader.iterRunsFromReader(
            self._reader,
            self._resolution,
            self._header.palletResolution,
            initial_index,
            self._header.rleDataEncoding,
            value_bits_add,
        )

    def _validatePalletIndexRange(self, maximum_index: int) -> None:
        pallet_count=maximum_index+1
        expected_ranges = ((1, 2), (3, 3), (4, 5), (6, 16))
        minimum,maximum=expected_ranges[self._header.palletResolution]
        if not minimum <= pallet_count <= maximum:
            raise ValueError("RLE pallet index range does not match encoding mode")

    def readPixel(self, pmgr: PalletMgr, lx: int, ly: int) -> int:
        target = IndexMapset.getIndexMap(self._resolution, self._header.rleMode).unmap(
            lx + ly * self._resolution)
        position = 0
        for count,pallet_index in self._iterRuns(pmgr):
            if position + count > target:
                return pmgr.table[pallet_index]
            position += count
        raise ValueError("RLE pixel position is out of range")

    def readRect(self, pmgr: PalletMgr, target: Rect[int], dest: IWritableRaster, dest_x: int, dest_y: int):
        index_map = IndexMapset.getIndexMap(self._resolution, self._header.rleMode)
        position = 0
        maximum_index=-1
        for count,pallet_index in self._iterRuns(pmgr):
            if pallet_index>maximum_index:
                maximum_index=pallet_index
            value=pmgr.table[pallet_index]
            for _ in range(count):
                mapped = index_map.map(position)
                lx = mapped % self._resolution
                ly = mapped // self._resolution
                if target.isInside(lx, ly):
                    dest.set((lx - target.x) + dest_x, (ly - target.y) + dest_y, value)
                position += 1
        self._validatePalletIndexRange(maximum_index)

    def skipToEnd(self, pmgr: PalletMgr):
        maximum_index=-1
        for _,pallet_index in self._iterRuns(pmgr):
            if pallet_index>maximum_index:
                maximum_index=pallet_index
        self._validatePalletIndexRange(maximum_index)


class ContainerNodeReader(NodeReader):
    def __init__(self, header: CellHeader, reader: ABytesReader, resolution: int, pallet_reader: _PalletValueReader):
        assert header.isNode
        self._header = header
        self._reader = reader
        self._resolution = resolution
        self._pallet_reader = pallet_reader

    def _createChildReader(self, header: CellHeader, resolution: int) -> NodeReader:
        if header.isNode:
            return ContainerNodeReader(header, self._reader, resolution, self._pallet_reader)
        if header.isRaw:
            return RawDataNodeReader(header, self._reader, resolution, self._pallet_reader)
        if header.isRle:
            return RleDataNodeReader(header, self._reader, resolution, self._pallet_reader)
        raise ValueError("invalid GI01 CellHeader type")

    def _readContainerPallet(self, pmgr: PalletMgr) -> None:
        update_table = self._header.updatePalletTable4
        self._pallet_reader.applyTable(self._reader, pmgr, update_table, 4)

    def readPixel(self, pmgr: PalletMgr, lx: int, ly: int) -> int:
        header = self._header
        if not header.hasValidContainerHeader:
            raise ValueError("invalid ContainerNode CellHeader")
        half = self._resolution // 2
        child_index = lx // half + 2 * (ly // half)
        if header.containerType == CellHeader.CONTAINER_TYPE_MONO:
            self._readContainerPallet(pmgr)
            return pmgr.get(1)[0]

        mask = self._reader.readByte()
        self._readContainerPallet(pmgr)
        node_pallet = ContainerPallet.restore(mask, header.containerType, pmgr.get(4))
        for index in range(4):
            value = node_pallet.palletValue(index)
            if value is not None:
                if index == child_index:
                    return value
                continue
            child_header = CellHeader(self._reader.readByte())
            child_reader = self._createChildReader(child_header, half)
            if index == child_index:
                return child_reader.readPixel(
                    pmgr,
                    lx - (index % 2) * half,
                    ly - (index // 2) * half,
                )
            child_reader.skipToEnd(pmgr)
        raise ValueError("Container child index is out of range")

    def readRect(self, pmgr: PalletMgr, target: Rect[int], dest: IWritableRaster, dest_x: int, dest_y: int):
        header = self._header
        if not header.hasValidContainerHeader:
            raise ValueError("invalid ContainerNode CellHeader")
        half = self._resolution // 2
        hs = half - target.x if target.x < half else 0
        vs = half - target.y if target.y < half else 0

        if header.containerType == CellHeader.CONTAINER_TYPE_MONO:
            self._readContainerPallet(pmgr)
            self._fillRect(dest, dest_x, dest_y, target.width, target.height, pmgr.get(1)[0])
            return

        mask = self._reader.readByte()
        self._readContainerPallet(pmgr)
        node_pallet = ContainerPallet.restore(mask, header.containerType, pmgr.get(4))
        for index in range(4):
            hx = index % 2 * half
            hy = index // 2 * half
            half_area = Rect[int](hx, hy, half, half)
            crossed = half_area.cross(target)
            lx = dest_x + (index % 2) * hs
            ly = dest_y + (index // 2) * vs
            value = node_pallet.palletValue(index)
            if value is not None:
                if crossed is not None:
                    self._fillRect(dest, lx, ly, crossed.width, crossed.height, value)
                continue

            child_header = CellHeader(self._reader.readByte())
            child_reader = self._createChildReader(child_header, half)
            if crossed is None:
                child_reader.skipToEnd(pmgr)
            else:
                child_reader.readRect(
                    pmgr,
                    Rect[int](crossed.x - hx, crossed.y - hy, crossed.width, crossed.height),
                    dest,
                    lx,
                    ly,
                )

    def skipToEnd(self, pmgr: PalletMgr):
        header = self._header
        if not header.hasValidContainerHeader:
            raise ValueError("invalid ContainerNode CellHeader")
        if header.containerType == CellHeader.CONTAINER_TYPE_MONO:
            self._readContainerPallet(pmgr)
            return
        mask = self._reader.readByte()
        self._readContainerPallet(pmgr)
        node_pallet = ContainerPallet.restore(mask, header.containerType, pmgr.get(4))
        for index in range(4):
            if node_pallet.palletValue(index) is not None:
                continue
            child_header = CellHeader(self._reader.readByte())
            self._createChildReader(child_header, self._resolution // 2).skipToEnd(pmgr)

    @staticmethod
    def _fillRect(dest: IWritableRaster, x: int, y: int, width: int, height: int, value: int) -> None:
        for iy in range(height):
            for ix in range(width):
                dest.set(x + ix, y + iy, value)


class BlockReader:
    """GI01ブロック列を先頭から逐次走査するReader。"""

    def __init__(self, data: bytes, root_resolution: int, offset: int = 0):
        reader = BytesBufferReader(data)
        reader.skipInByte(offset)
        self._reader = reader
        self._resolution = root_resolution
        self._current: BlockNodeReader | None = None

    def skipBlock(self, count: int = 1):
        for _ in range(count):
            if self._current is not None:
                self.skipToEnd()
                continue
            reader = self._reader
            block_header = BlockHeader(reader.readByte())
            compression_type = block_header.compressionType
            if compression_type != CC_RAW:
                size = reader.readMbUInt()
                reader.skipInByte(size)
                continue
            pallet_reader = _PalletValueReader(block_header.paletteDelta)
            header = CellHeader(reader.readByte())
            self._createNodeReader(header, reader, pallet_reader).skipToEnd(PalletMgr(16))
            reader.skipToByte()

    def readBlock(self) -> "BlockNodeReader":
        if self._current is not None:
            return self._current
        reader = self._reader
        block_header = BlockHeader(reader.readByte())
        compression_type = block_header.compressionType
        pallet_reader = _PalletValueReader(block_header.paletteDelta)
        payload_reader: BytesBufferReader | None = None
        payload_end: int | None = None
        if compression_type == CC_RAW:
            node_reader = reader
        elif compression_type == CC_RAWS:
            payload_size = reader.readMbUInt()
            payload = reader.readAsBytes(payload_size)
            payload_reader = BytesBufferReader(payload)
            node_reader = payload_reader
            payload_end = payload_size
        elif compression_type == CC_LZSS:
            payload_size = reader.readMbUInt()
            payload_end = reader.pos + payload_size
            node_reader = BytesIteratorReader(Lzss(256).decompressIteratorFromBytes(reader))
        else:
            raise ValueError("unsupported GI01 block compression type")
        header = CellHeader(node_reader.readByte())
        node_reader = self._createNodeReader(header, node_reader, pallet_reader)
        self._current = BlockNodeReader(
            node_reader,
            PalletMgr(16),
            payload_reader if payload_reader is not None else reader,
            payload_end,
        )
        return self._current

    def skipToEnd(self):
        if self._current is None:
            return
        self._current.skipToEnd()
        self._current = None

    def getNodeReader(self, index: int) -> NodeReader:
        if index > 0:
            self.skipBlock(index)
        return self.readBlock().nodeReader

    def _createNodeReader(self, header: CellHeader, reader: ABytesReader, pallet_reader: _PalletValueReader) -> NodeReader:
        if header.isNode:
            return ContainerNodeReader(header, reader, self._resolution, pallet_reader)
        if header.isRaw:
            return RawDataNodeReader(header, reader, self._resolution, pallet_reader)
        if header.isRle:
            return RleDataNodeReader(header, reader, self._resolution, pallet_reader)
        raise ValueError("invalid GI01 root CellHeader")


class BlockNodeReader:
    """1ブロック分のNodeReaderとブロック終端処理を束ねる。"""

    def __init__(
        self,
        node_reader: NodeReader,
        pmgr: PalletMgr,
        block_reader: ABytesReader,
        payload_end: int | None,
    ):
        self.nodeReader = node_reader
        self._pmgr = pmgr
        self._block_reader = block_reader
        self._payload_end = payload_end
        self._node_finished = False
        self._finished = False

    def readRect(self, target: Rect[int], dest: IWritableRaster, dest_x: int, dest_y: int):
        self.nodeReader.readRect(self._pmgr, target, dest, dest_x, dest_y)
        self._node_finished = True

    def skipToEnd(self):
        if self._finished:
            return
        if not self._node_finished:
            self.nodeReader.skipToEnd(self._pmgr)
            self._node_finished = True
        self._block_reader.skipToByte()
        if self._payload_end is not None:
            remain = self._payload_end - self._block_reader.pos
            if remain < 0:
                raise ValueError("GI01 block payload reader exceeded payload size")
            self._block_reader.skipInByte(remain)
        self._finished = True


class GaluchatImageDataChunk01Reader:
    """GI01チャンクをDOM化せず、WGSMap/3のbytes上で逐次読み出すReader。"""

    def __init__(self, src: bytes, offset: int = 0):
        reader = BytesBufferReader(src, offset=offset)
        if reader.readAsBytes(4) != CHUNK_NAME:
            raise RuntimeError("invalid GI01 chunk")
        size = reader.readMbUInt()
        data_offset = reader.pos
        width, height = reader.readMbUInts(2)
        square_unit = 2 ** reader.readByte()
        self.width = width
        self.height = height
        self.square_unit = square_unit
        self.hus = (width + square_unit - 1) // square_unit
        self.vus = (height + square_unit - 1) // square_unit
        self._src = src
        self._gblock_offset = offset + reader.pos
        self._chunk_size = size + data_offset

    @property
    def chunk_size(self) -> int:
        return self._chunk_size

    def isInside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def readPoint(self, x: int, y: int) -> int:
        if not self.isInside(x, y):
            raise RuntimeError()
        unit = self.square_unit
        ux = x // unit
        uy = y // unit
        block_index = ux + uy * self.hus
        reader = BlockReader(self._src, self.square_unit, self._gblock_offset)
        node_reader = reader.getNodeReader(block_index)
        return node_reader.readPixel(PalletMgr(16), x - ux * unit, y - uy * unit)

    def getAreaByBlockIndex(self, index: int) -> Rect[int]:
        unit = self.square_unit
        return Rect[int](index % self.hus * unit, index // self.hus * unit, unit, unit)

    def readRect(self, x: int, y: int, dest: IWritableRaster):
        target_box = Rect[int](x, y, dest.width, dest.height)
        block_reader = BlockReader(self._src, self.square_unit, self._gblock_offset)
        for index in range(self.hus * self.vus):
            source_box = self.getAreaByBlockIndex(index)
            crossed = source_box.cross(target_box)
            if crossed is None:
                block_reader.skipBlock()
                continue
            block = block_reader.readBlock()
            try:
                block.readRect(
                    Rect[int](
                        crossed.x - source_box.x,
                        crossed.y - source_box.y,
                        crossed.width,
                        crossed.height,
                    ),
                    dest,
                    crossed.x - target_box.x,
                    crossed.y - target_box.y,
                )
            finally:
                block_reader.skipToEnd()
        return dest

    def toRaster(self) -> Raster:
        dest = RawRaster.createRaster(self.width, self.height)
        self.readRect(0, 0, dest)
        return dest
