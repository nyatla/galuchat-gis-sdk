from typing import Iterator

from galuchat.io import ABytesReader

from .CellHeader import CellHeader
from .rlelencodec import ShortValueRleLenCodec, SingleEdgeRowLenCodec


class RlePacketReader:
    """GI01 RLE packetをDOM化せずラン列として逐次復号する。"""

    @staticmethod
    def _shortValueBitsAdd(value_bits_add: int) -> int:
        return value_bits_add & 0x03

    @staticmethod
    def _shortValueRunBitsAdd(value_bits_add: int) -> int:
        return (value_bits_add >> 2) & 0x01

    @staticmethod
    def _singleEdgeDValueFormat(value_bits_add: int) -> int:
        return value_bits_add // 5

    @staticmethod
    def _singleEdgeMbUIntReduceBits(value_bits_add: int) -> int | None:
        code = value_bits_add % 5
        return None if code == 0 else code + 1

    @staticmethod
    def readNextIndex(
        src: ABytesReader,
        pallet_mode: int,
        initial_index: int | None,
        run_index: int,
        previous_index: int | None,
    ) -> int:
        if pallet_mode == 0:
            if initial_index is None:
                raise ValueError("initial index is required")
            return (initial_index + run_index) % 2
        if pallet_mode in (1, 2):
            if initial_index is None:
                raise ValueError("initial index is required")
            if run_index == 0:
                return initial_index
            if previous_index is None:
                raise ValueError("previous index is required")
            bits = 1 if pallet_mode == 1 else 2
            modulus = 3 if pallet_mode == 1 else 5
            return (previous_index + src.readBitsAsInt32(bits) + 1) % modulus
        if pallet_mode == 3:
            return src.readBitsAsInt32(4)
        raise ValueError("invalid RLE pallet mode")

    @classmethod
    def iterRunsFromReader(
        cls,
        reader: ABytesReader,
        resolution: int,
        pallet_mode: int,
        initial_index: int | None,
        data_encoding: int = CellHeader.RLE_DATA_ENCODING_MBUINT,
        value_bits_add: int = 0,
    ) -> Iterator[tuple[int, int]]:
        pixels = resolution**2
        run_index = 0
        previous_index: int | None = None
        total = 0

        def read_index() -> int:
            nonlocal previous_index
            index = cls.readNextIndex(
                reader,
                pallet_mode,
                initial_index,
                run_index,
                previous_index,
            )
            previous_index = index
            return index

        if data_encoding == CellHeader.RLE_DATA_ENCODING_MBUINT:
            while total < pixels:
                count = reader.readMbUInt()
                if count <= 0:
                    raise ValueError("RLE count must be positive")
                total += count
                if total > pixels:
                    raise ValueError("RLE count total exceeds resolution")
                pallet_index = read_index()
                run_index += 1
                yield count, pallet_index
            return

        if data_encoding == CellHeader.RLE_DATA_ENCODING_SHORT_VALUE:
            codec = ShortValueRleLenCodec(
                resolution,
                cls._shortValueBitsAdd(value_bits_add),
                cls._shortValueRunBitsAdd(value_bits_add),
            )
            run_count = reader.readMbUInt()
            if run_count <= 0:
                raise ValueError("ShortValue requires at least one value")
            explicit_count = run_count - 1
            while run_index < explicit_count:
                token_counts: list[int] = []
                codec.readToken(reader, token_counts, explicit_count - run_index)
                for count in token_counts:
                    if count <= 0:
                        raise ValueError("RLE count must be positive")
                    total += count
                    if total >= pixels:
                        raise ValueError("RLE count total exceeds pixel count")
                    pallet_index = read_index()
                    run_index += 1
                    yield count, pallet_index
            last = pixels - total
            if last <= 0:
                raise ValueError("RLE count total does not leave final run")
            yield last, read_index()
            return

        if data_encoding == CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW:
            codec = SingleEdgeRowLenCodec(
                resolution,
                cls._singleEdgeDValueFormat(value_bits_add),
                cls._singleEdgeMbUIntReduceBits(value_bits_add),
            )
            run_count = reader.readMbUInt()
            if run_count < 2:
                raise ValueError("SingleEdgeRow requires at least two values")
            explicit_count = run_count - 1
            if codec.mbuint_reduce_bits is not None:
                first = reader.readMbUInt()
                if first <= 0:
                    raise ValueError("RLE count must be positive")
                total += first
                if total >= pixels:
                    raise ValueError("RLE count total exceeds pixel count")
                pallet_index = read_index()
                run_index += 1
                yield first, pallet_index
                while run_index < explicit_count:
                    token_counts = []
                    codec.readReducedMiddleToken(
                        reader, token_counts, explicit_count - run_index)
                    for count in token_counts:
                        if count <= 0:
                            raise ValueError("RLE count must be positive")
                        total += count
                        if total >= pixels:
                            raise ValueError("RLE count total exceeds pixel count")
                        pallet_index = read_index()
                        run_index += 1
                        yield count, pallet_index
            else:
                while run_index < explicit_count:
                    token_counts = []
                    codec.readToken(reader, token_counts, explicit_count - run_index)
                    for count in token_counts:
                        if count <= 0:
                            raise ValueError("RLE count must be positive")
                        total += count
                        if total >= pixels:
                            raise ValueError("RLE count total exceeds pixel count")
                        pallet_index = read_index()
                        run_index += 1
                        yield count, pallet_index
            last = pixels - total
            if last <= 0:
                raise ValueError("RLE count total does not leave final run")
            yield last, read_index()
            return

        raise ValueError("invalid RLE data encoding")
