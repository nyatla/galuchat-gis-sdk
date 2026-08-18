from typing import Dict, List, NamedTuple, Sequence, Tuple

from ....io import ABytesReader, ABytesWriter, BytesBufferReader, BytesWriter
from ....io.MBIntDef import MBIntDef


class SingleEdgeRowDValueFormat(NamedTuple):
    """SingleEdgeRow tokenのd値記録パラメータ。"""

    bits: int
    minimum: int
    maximum: int


class SingleEdgeRowLenToken(NamedTuple):
    """DPで選択されたSingleEdgeRow codecの1 token。"""

    token_type: str
    mbuint_value: int
    values: Tuple[int, ...]
    next_index: int


class SingleEdgeRowLenEncodePlan(NamedTuple):
    """SingleEdgeRow codecが選択したラン長列の符号化計画。"""

    bit_count: int
    mbuint_reduce_bits: int | None
    tokens: Tuple[SingleEdgeRowLenToken, ...]


SINGLE_EDGE_ROW_LEN_PARAMETERS: Dict[int, bool] = {
    8: True,
    16: True,
    32: True,
    64: True,
    128: True,
    256: True,
}


class SingleEdgeRowLenCodec:
    """MBUIntと単一境界行tokenだけを使うRLEラン長codec。"""

    DEFAULT_PARAMETERS = SINGLE_EDGE_ROW_LEN_PARAMETERS
    RUN_COUNT_BITS = 5
    MIN_RUN_COUNT = 2
    DEFAULT_MBUINT_REDUCE_VALUE_BITS = 4
    D_VALUE_FORMATS = (
        SingleEdgeRowDValueFormat(2, -1, 2),
        SingleEdgeRowDValueFormat(3, -3, 4),
        SingleEdgeRowDValueFormat(4, -7, 8),
    )

    def __init__(self, resolution: int, d_value_format: int = 2, mbuint_reduce_bits: int | None = None):
        if not 0 <= d_value_format < len(self.D_VALUE_FORMATS):
            raise ValueError("d_value_format must be in 0..2")
        if mbuint_reduce_bits is not None and not 1 <= mbuint_reduce_bits <= 8:
            raise ValueError("mbuint_reduce_bits must be in 1..8")
        self.resolution = resolution
        self.d_value_format = d_value_format
        self.mbuint_reduce_bits = mbuint_reduce_bits
        self._parameter = self.DEFAULT_PARAMETERS.get(resolution)
        self._d_format = self.D_VALUE_FORMATS[d_value_format]
        self._run_max = self.MIN_RUN_COUNT + (1 << self.RUN_COUNT_BITS) - 1

    def encodeState(self, values: Sequence[int]) -> Tuple[int, int]:
        before = sum(MBIntDef.sizeOfMbUint(value) for value in values)
        after = len(self.encodeToBytes(values))
        return before, after

    def encodeToBytes(self, values: Sequence[int]) -> bytes:
        writer = BytesWriter()
        self.encodeToWriter(writer, values, align=True)
        return bytes(writer.buffer)

    def selectEncoding(
        self,
        values: Sequence[int],
        mbuint_reduce_bit_candidates: Sequence[int] = (),
    ) -> Tuple[int, int | None]:
        plan = self._selectEncodePlan(values, mbuint_reduce_bit_candidates)
        return plan.bit_count, plan.mbuint_reduce_bits

    def encodeToWriter(self, writer: ABytesWriter, values: Sequence[int], align: bool = True) -> int:
        bit_count = 0
        if self.mbuint_reduce_bits is not None:
            bit_count = self._writeReduced(writer, values)
            if align:
                writer.alignToByte()
            return bit_count

        if len(values) < 2:
            raise ValueError("SingleEdgeRow requires at least two values")
        writer.writeMbUInt(len(values))
        bit_count += MBIntDef.sizeOfMbUint(len(values)) * 8
        tokens = self.selectPlan(values).tokens
        for token in tokens:
            bit_count += self.writeToken(writer, token)
        if align:
            writer.alignToByte()
        return bit_count

    def estimateBits(self, values: Sequence[int]) -> int:
        if self.mbuint_reduce_bits is not None:
            return self._reducedBits(values)
        if len(values) < 2:
            raise ValueError("SingleEdgeRow requires at least two values")
        tokens = self._selectTokens(values[:-1])
        return MBIntDef.sizeOfMbUint(len(values)) * 8 + sum(
            self._tokenBits(token) for token in tokens)

    def selectPlan(self, values: Sequence[int]) -> SingleEdgeRowLenEncodePlan:
        if self.mbuint_reduce_bits is not None:
            return self._selectReducedPlan(values)
        if len(values) < 2:
            raise ValueError("SingleEdgeRow requires at least two values")
        tokens = tuple(self._selectTokens(values[:-1]))
        bit_count = (
            MBIntDef.sizeOfMbUint(len(values)) * 8 +
            sum(self._tokenBits(token) for token in tokens))
        return SingleEdgeRowLenEncodePlan(bit_count, None, tokens)

    def writeRunCount(self, writer: ABytesWriter, values: Sequence[int]) -> int:
        if len(values) < 2:
            raise ValueError("SingleEdgeRow requires at least two values")
        writer.writeMbUInt(len(values))
        return MBIntDef.sizeOfMbUint(len(values)) * 8

    def writeReduceFirstValue(self, writer: ABytesWriter, values: Sequence[int]) -> int:
        if self.mbuint_reduce_bits is None:
            raise ValueError("RLE SingleEdgeRow MBUIntReduce is disabled")
        if len(values) < 2:
            raise ValueError("MBUIntReduce requires at least two values")
        writer.writeMbUInt(values[0])
        return MBIntDef.sizeOfMbUint(values[0]) * 8

    def writeToken(self, writer: ABytesWriter, token: SingleEdgeRowLenToken) -> int:
        if token.token_type == "mbuint":
            writer.writeBitsFromInt32(0, 1)
            writer.writeMbUInt(token.mbuint_value)
        elif token.token_type == "short_mbuint":
            self._writeShortMbUIntToken(writer, token.mbuint_value)
        elif token.token_type == "single_edge":
            self._writeSingleEdgeToken(writer, token.values)
        else:
            raise RuntimeError("invalid RLE single edge token")
        return self._tokenBits(token)

    def readToken(self, reader: ABytesReader, values: List[int], count: int) -> int:
        before = len(values)
        self._readToken(reader, values, count)
        return len(values) - before

    def readReducedMiddleToken(self, reader: ABytesReader, values: List[int], count: int) -> int:
        before = len(values)
        self._readReducedMiddleToken(reader, values, count)
        return len(values) - before

    def decodeFromBytes(self, src: bytes, count: int) -> List[int]:
        return self.decode(BytesBufferReader(src), count)

    def decode(self, reader: ABytesReader, count: int) -> List[int]:
        if self.mbuint_reduce_bits is not None:
            return self._decodeReduced(reader, count)
        run_count = reader.readMbUInt()
        if run_count != count:
            raise ValueError("RLE run count does not match requested count")
        if run_count < 2:
            raise ValueError("SingleEdgeRow requires at least two values")
        values: List[int] = []
        while len(values) < run_count - 1:
            self._readToken(reader, values, run_count - 1)
        last = self.resolution * self.resolution - sum(values)
        if last <= 0:
            raise ValueError("RLE count total exceeds pixel count")
        values.append(last)
        return values

    def decodeUntilPixelCount(self, reader: ABytesReader, pixel_count: int, align: bool = True) -> List[int]:
        if self.mbuint_reduce_bits is not None:
            return self._decodeReducedUntilPixelCount(reader, pixel_count, align)
        run_count = reader.readMbUInt()
        if run_count < 2:
            raise ValueError("SingleEdgeRow requires at least two values")
        values: List[int] = []
        total = 0
        while len(values) < run_count - 1:
            previous_count = len(values)
            self._readToken(reader, values, run_count - 1)
            for value in values[previous_count:]:
                if value <= 0:
                    raise ValueError("RLE count must be positive")
                total += value
                if total >= pixel_count:
                    raise ValueError("RLE count total exceeds pixel count")
        last = pixel_count - total
        if last <= 0:
            raise ValueError("RLE count total does not leave final run")
        values.append(last)
        if align:
            reader.skipToByte()
        return values

    def _tokenBits(self, token: SingleEdgeRowLenToken) -> int:
        if token.token_type == "mbuint":
            return 1 + MBIntDef.sizeOfMbUint(token.mbuint_value) * 8
        if token.token_type == "short_mbuint":
            if self.mbuint_reduce_bits is None:
                raise RuntimeError("short MBUInt token requires mbuint_reduce_bits")
            return 1 + self.mbuint_reduce_bits
        if token.token_type == "single_edge":
            return (
                1 + self.RUN_COUNT_BITS + MBIntDef.sizeOfMbUint(token.values[0]) * 8 +
                (len(token.values) - 1) * self._d_format.bits)
        raise RuntimeError("invalid RLE single edge token")

    def _selectTokens(self, values: Sequence[int]) -> List[SingleEdgeRowLenToken]:
        count = len(values)
        costs = [0] * (count + 1)
        choices: List[SingleEdgeRowLenToken | None] = [None] * count

        for index in range(count - 1, -1, -1):
            value = values[index]
            mbuint_bits = 1 + MBIntDef.sizeOfMbUint(value) * 8
            best_cost = mbuint_bits + costs[index + 1]
            best_choice = SingleEdgeRowLenToken("mbuint", value, (), index + 1)

            for bit_count, token in self._iterSingleEdgeCandidates(values, index):
                cost = bit_count + costs[token.next_index]
                if cost < best_cost:
                    best_cost = cost
                    best_choice = token

            costs[index] = best_cost
            choices[index] = best_choice

        tokens: List[SingleEdgeRowLenToken] = []
        index = 0
        while index < count:
            choice = choices[index]
            if choice is None:
                raise RuntimeError("missing RLE single edge token choice")
            tokens.append(choice)
            index = choice.next_index
        return tokens

    def _selectEncodePlan(
        self,
        values: Sequence[int],
        mbuint_reduce_bit_candidates: Sequence[int],
    ) -> SingleEdgeRowLenEncodePlan:
        if len(values) < 2:
            raise ValueError("SingleEdgeRow requires at least two values")
        tokens = tuple(self._selectTokens(values[:-1]))
        normal_bit_count = (
            MBIntDef.sizeOfMbUint(len(values)) * 8 +
            sum(self._tokenBits(token) for token in tokens)
        )
        normal_plan = SingleEdgeRowLenEncodePlan(normal_bit_count, None, tokens)

        best_plan = normal_plan
        for mbuint_reduce_bits in mbuint_reduce_bit_candidates:
            reduced_plan = self._selectReducedPlanOrNone(values, mbuint_reduce_bits)
            if reduced_plan is not None and reduced_plan.bit_count < best_plan.bit_count:
                best_plan = reduced_plan
        return best_plan

    def _convertMiddleTokensForReduce(
        self,
        tokens: Sequence[SingleEdgeRowLenToken],
        mbuint_reduce_bits: int,
    ) -> Tuple[SingleEdgeRowLenToken, ...] | None:
        reduced_tokens: List[SingleEdgeRowLenToken] = []
        for token in tokens:
            if token.token_type == "mbuint":
                value = token.mbuint_value
                if not 1 <= value <= (1 << mbuint_reduce_bits):
                    return None
                reduced_tokens.append(SingleEdgeRowLenToken(
                    "short_mbuint", value, (), token.next_index))
            elif token.token_type == "single_edge":
                reduced_tokens.append(token)
            else:
                raise RuntimeError("invalid RLE single edge token")
        return tuple(reduced_tokens)

    def _selectReducedPlanOrNone(
        self,
        values: Sequence[int],
        mbuint_reduce_bits: int,
    ) -> SingleEdgeRowLenEncodePlan | None:
        if len(values) < 2:
            return None
        if values[0] <= 0 or values[-1] <= 0:
            raise ValueError("RLE count must be positive")
        run_count = len(values)
        middle_tokens = tuple(self._selectTokens(values[1:-1]))
        reduced_middle_tokens = self._convertMiddleTokensForReduce(middle_tokens, mbuint_reduce_bits)
        if reduced_middle_tokens is None:
            return None
        bit_count = (
            MBIntDef.sizeOfMbUint(run_count) * 8 +
            MBIntDef.sizeOfMbUint(values[0]) * 8 +
            sum(self._tokenBitsWithReduceBits(token, mbuint_reduce_bits) for token in reduced_middle_tokens)
        )
        return SingleEdgeRowLenEncodePlan(bit_count, mbuint_reduce_bits, reduced_middle_tokens)

    def _tokenBitsWithReduceBits(self, token: SingleEdgeRowLenToken, mbuint_reduce_bits: int) -> int:
        if token.token_type == "short_mbuint":
            return 1 + mbuint_reduce_bits
        return self._tokenBits(token)

    def _selectReducedPlan(self, values: Sequence[int]) -> SingleEdgeRowLenEncodePlan:
        if self.mbuint_reduce_bits is None:
            raise ValueError("RLE SingleEdgeRow MBUIntReduce is disabled")
        plan = self._selectReducedPlanOrNone(
            values, self.mbuint_reduce_bits)
        if plan is None:
            raise ValueError("RLE SingleEdgeRow MBUIntReduce cannot encode counts")
        return plan

    def _reducedBits(self, values: Sequence[int]) -> int:
        return self._selectReducedPlan(values).bit_count

    def _iterSingleEdgeCandidates(self, values: Sequence[int], index: int):
        if self._parameter is None:
            return
        if index + self.MIN_RUN_COUNT > len(values):
            return
        first = values[index]
        if not self._isValueInRange(first):
            return

        token_values = [first]
        max_end = min(len(values), index + self._run_max)
        for cursor in range(index + 1, max_end):
            value = values[cursor]
            if not self._isValueInRange(value):
                break
            d_value = value - (2 * self.resolution - token_values[-1])
            if not self._d_format.minimum <= d_value <= self._d_format.maximum:
                break
            token_values.append(value)
            run_count = len(token_values)
            if run_count >= self.MIN_RUN_COUNT:
                bit_count = (
                    1 + self.RUN_COUNT_BITS + MBIntDef.sizeOfMbUint(token_values[0]) * 8 +
                    (run_count - 1) * self._d_format.bits)
                yield bit_count, SingleEdgeRowLenToken(
                    "single_edge", 0, tuple(token_values), index + run_count)

    def _isValueInRange(self, value: int) -> bool:
        return value > 0

    def _writeSingleEdgeToken(self, writer: ABytesWriter, values: Sequence[int]) -> None:
        if self._parameter is None:
            raise ValueError(f"single edge token is not supported at resolution: {self.resolution}")
        if not self.MIN_RUN_COUNT <= len(values) <= self._run_max:
            raise ValueError("invalid single edge token count")
        writer.writeBitsFromInt32(1, 1)
        writer.writeBitsFromInt32(len(values) - self.MIN_RUN_COUNT, self.RUN_COUNT_BITS)
        if not self._isValueInRange(values[0]):
            raise ValueError(f"invalid single edge value: {values[0]}")
        writer.writeMbUInt(values[0])
        previous = values[0]
        for value in values[1:]:
            d_value = value - (2 * self.resolution - previous)
            if not self._d_format.minimum <= d_value <= self._d_format.maximum:
                raise ValueError(f"single edge d does not fit d value format: {d_value}")
            writer.writeBitsFromInt32(d_value - self._d_format.minimum, self._d_format.bits)
            previous = value

    def _writeReduced(self, writer: ABytesWriter, values: Sequence[int]) -> int:
        plan = self._selectReducedPlan(values)
        writer.writeMbUInt(len(values))
        writer.writeMbUInt(values[0])
        for token in plan.tokens:
            if token.token_type == "short_mbuint":
                self._writeShortMbUIntToken(writer, token.mbuint_value)
            elif token.token_type == "single_edge":
                self._writeSingleEdgeToken(writer, token.values)
            else:
                raise RuntimeError("invalid RLE single edge reduce token")
        return plan.bit_count

    def _writeShortMbUIntToken(self, writer: ABytesWriter, value: int) -> None:
        if self.mbuint_reduce_bits is None:
            raise ValueError("RLE SingleEdgeRow MBUIntReduce is disabled")
        if not 1 <= value <= (1 << self.mbuint_reduce_bits):
            raise ValueError("short MBUInt value is out of range")
        writer.writeBitsFromInt32(0, 1)
        writer.writeBitsFromInt32(value - 1, self.mbuint_reduce_bits)

    def _decodeReduced(self, reader: ABytesReader, count: int) -> List[int]:
        run_count = reader.readMbUInt()
        if run_count != count:
            raise ValueError("RLE run count does not match requested count")
        if run_count < 2:
            raise ValueError("MBUIntReduce requires at least two values")
        first = reader.readMbUInt()
        if first <= 0:
            raise ValueError("RLE count must be positive")
        values: List[int] = [first]
        while len(values) < run_count - 1:
            self._readReducedMiddleToken(reader, values, run_count - 1)
        last = self.resolution * self.resolution - sum(values)
        if last <= 0:
            raise ValueError("RLE count total exceeds pixel count")
        values.append(last)
        return values

    def _decodeReducedUntilPixelCount(
        self,
        reader: ABytesReader,
        pixel_count: int,
        align: bool = True,
    ) -> List[int]:
        run_count = reader.readMbUInt()
        if run_count < 2:
            raise ValueError("MBUIntReduce requires at least two values")
        first = reader.readMbUInt()
        if first <= 0:
            raise ValueError("RLE count must be positive")
        values: List[int] = [first]
        total = first
        if total >= pixel_count:
            raise ValueError("RLE count total exceeds pixel count")

        # MBUIntReduceではrun_countとfirstを先に読む。middle tokenを
        # run_count-2個だけ読み、lastは既知の画素数から復元する。
        while len(values) < run_count - 1:
            previous_count = len(values)
            self._readReducedMiddleToken(reader, values, run_count - 1)
            for value in values[previous_count:]:
                if value <= 0:
                    raise ValueError("RLE count must be positive")
                total += value
                if total >= pixel_count:
                    raise ValueError("RLE count total exceeds pixel count")
        last = pixel_count - total
        if last <= 0:
            raise ValueError("RLE count total does not leave final run")
        values.append(last)
        if align:
            reader.skipToByte()
        return values

    def _readReducedMiddleToken(
        self,
        reader: ABytesReader,
        values: List[int],
        count: int,
    ) -> None:
        prefix = reader.readBitsAsInt32(1)
        if prefix == 0:
            if self.mbuint_reduce_bits is None:
                raise ValueError("RLE SingleEdgeRow MBUIntReduce is disabled")
            if len(values) >= count:
                raise ValueError("short MBUInt token exceeds requested count")
            values.append(reader.readBitsAsInt32(self.mbuint_reduce_bits) + 1)
            return
        self._readSingleEdgeToken(reader, values, count)

    def _readToken(self, reader: ABytesReader, values: List[int], count: int) -> None:
        prefix = reader.readBitsAsInt32(1)
        if prefix == 0:
            if len(values) >= count:
                raise ValueError("MBUInt token exceeds requested count")
            values.append(reader.readMbUInt())
            return
        self._readSingleEdgeToken(reader, values, count)

    def _readSingleEdgeToken(self, reader: ABytesReader, values: List[int], count: int) -> None:
        if self._parameter is None:
            raise ValueError(f"single edge token is not supported at resolution: {self.resolution}")

        run_count = reader.readBitsAsInt32(self.RUN_COUNT_BITS) + self.MIN_RUN_COUNT
        if len(values) + run_count > count:
            raise ValueError("single edge token exceeds requested count")

        previous = reader.readMbUInt()
        if not self._isValueInRange(previous):
            raise ValueError(f"invalid single edge value: {previous}")
        values.append(previous)
        for _ in range(run_count - 1):
            d_value = reader.readBitsAsInt32(self._d_format.bits) + self._d_format.minimum
            value = 2 * self.resolution - previous + d_value
            if not self._isValueInRange(value):
                raise ValueError(f"invalid single edge value: {value}")
            values.append(value)
            previous = value
