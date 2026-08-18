from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from ....io import ABytesReader, ABytesWriter, BytesBufferReader, BytesWriter
from ....io.MBIntDef import MBIntDef


class ShortValueRleLenParameter(NamedTuple):
    """ShortValue tokenの解像度別パラメータ。"""

    run_bits: int
    run_min: int
    run_max: int
    base_value_bits: int


class ShortValueRleLenToken(NamedTuple):
    """DPで選択されたShortValue codecの1 token。"""

    token_type: str
    mbuint_value: int
    values: Tuple[int, ...]
    next_index: int


SHORT_VALUE_RLE_LEN_PARAMETERS: Dict[int, ShortValueRleLenParameter] = {
    8: ShortValueRleLenParameter(run_bits=3, run_min=2, run_max=9, base_value_bits=2),
    16: ShortValueRleLenParameter(run_bits=3, run_min=2, run_max=9, base_value_bits=2),
    32: ShortValueRleLenParameter(run_bits=4, run_min=4, run_max=19, base_value_bits=3),
    64: ShortValueRleLenParameter(run_bits=4, run_min=4, run_max=19, base_value_bits=4),
    128: ShortValueRleLenParameter(run_bits=4, run_min=4, run_max=19, base_value_bits=4),
    256: ShortValueRleLenParameter(run_bits=5, run_min=4, run_max=35, base_value_bits=4),
}


class ShortValueRleLenCodec:
    """MBUIntと短連続V値tokenだけを使うRLEラン長codec。"""

    DEFAULT_PARAMETERS = SHORT_VALUE_RLE_LEN_PARAMETERS

    def __init__(
        self,
        resolution: int,
        value_bits_add: int = 0,
        run_bits_add: int = 0,
        parameters: Optional[Mapping[int, ShortValueRleLenParameter]] = None,
    ):
        if not 0 <= value_bits_add <= 3:
            raise ValueError("value_bits_add must be in 0..3")
        if not 0 <= run_bits_add <= 1:
            raise ValueError("run_bits_add must be in 0..1")
        self.resolution = resolution
        self.value_bits_add = value_bits_add
        self.run_bits_add = run_bits_add
        self._parameters = parameters if parameters is not None else self.DEFAULT_PARAMETERS
        self._parameter = self._parameters.get(resolution)
        if self._parameter is not None:
            self._validateParameter(self._parameter)
            self._run_bits = self._parameter.run_bits + run_bits_add
            self._run_max = self._parameter.run_min + (1 << self._run_bits) - 1
            self._value_bits = self._parameter.base_value_bits + value_bits_add
        else:
            self._run_bits = None
            self._run_max = None
            self._value_bits = None

    def encodeState(self, values: Sequence[int]) -> Tuple[int, int]:
        before = sum(MBIntDef.sizeOfMbUint(value) for value in values)
        after = len(self.encodeToBytes(values))
        return before, after

    def encodeToBytes(self, values: Sequence[int]) -> bytes:
        writer = BytesWriter()
        self.encodeToWriter(writer, values, align=True)
        return bytes(writer.buffer)

    def encodeToWriter(self, writer: ABytesWriter, values: Sequence[int], align: bool = True) -> int:
        if len(values) == 0:
            raise ValueError("ShortValue requires at least one value")
        writer.writeMbUInt(len(values))
        bit_count = MBIntDef.sizeOfMbUint(len(values)) * 8
        tokens = self.selectTokens(values)
        for token in tokens:
            bit_count += self.writeToken(writer, token)
        if align:
            writer.alignToByte()
        return bit_count

    def estimateBits(self, values: Sequence[int]) -> int:
        if len(values) == 0:
            raise ValueError("ShortValue requires at least one value")
        return (
            MBIntDef.sizeOfMbUint(len(values)) * 8 +
            sum(self._tokenBits(token) for token in self.selectTokens(values))
        )

    def selectTokens(self, values: Sequence[int]) -> Tuple[ShortValueRleLenToken, ...]:
        if len(values) == 0:
            raise ValueError("ShortValue requires at least one value")
        return tuple(self._selectTokens(values[:-1]))

    def writeRunCount(self, writer: ABytesWriter, values: Sequence[int]) -> int:
        if len(values) == 0:
            raise ValueError("ShortValue requires at least one value")
        writer.writeMbUInt(len(values))
        return MBIntDef.sizeOfMbUint(len(values)) * 8

    def writeToken(self, writer: ABytesWriter, token: ShortValueRleLenToken) -> int:
        if token.token_type == "mbuint":
            writer.writeBitsFromInt32(0, 1)
            writer.writeMbUInt(token.mbuint_value)
        elif token.token_type == "short_value":
            self._writeShortValueToken(writer, token.values)
        else:
            raise RuntimeError("invalid RLE short value token")
        return self._tokenBits(token)

    def readToken(self, reader: ABytesReader, values: List[int], count: int) -> int:
        before = len(values)
        self._readToken(reader, values, count)
        return len(values) - before

    def decodeFromBytes(self, src: bytes, count: int) -> List[int]:
        return self.decode(BytesBufferReader(src), count)

    def decode(self, reader: ABytesReader, count: int) -> List[int]:
        run_count = reader.readMbUInt()
        if run_count != count:
            raise ValueError("RLE run count does not match requested count")
        if run_count <= 0:
            raise ValueError("ShortValue requires at least one value")
        values: List[int] = []
        while len(values) < run_count - 1:
            self._readToken(reader, values, run_count - 1)
        last = self.resolution * self.resolution - sum(values)
        if last <= 0:
            raise ValueError("RLE count total exceeds pixel count")
        values.append(last)
        return values

    def decodeUntilPixelCount(self, reader: ABytesReader, pixel_count: int, align: bool = True) -> List[int]:
        run_count = reader.readMbUInt()
        if run_count <= 0:
            raise ValueError("ShortValue requires at least one value")
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

    def _tokenBits(self, token: ShortValueRleLenToken) -> int:
        if token.token_type == "mbuint":
            return 1 + MBIntDef.sizeOfMbUint(token.mbuint_value) * 8
        if token.token_type == "short_value":
            return 1 + self._run_bits + self._value_bits * len(token.values)
        raise RuntimeError("invalid RLE short value token")

    def _selectTokens(self, values: Sequence[int]) -> List[ShortValueRleLenToken]:
        count = len(values)
        costs = [0] * (count + 1)
        choices: List[ShortValueRleLenToken | None] = [None] * count

        for index in range(count - 1, -1, -1):
            value = values[index]
            mbuint_bits = 1 + MBIntDef.sizeOfMbUint(value) * 8
            best_cost = mbuint_bits + costs[index + 1]
            best_choice = ShortValueRleLenToken("mbuint", value, (), index + 1)

            for bit_count, token in self._iterShortValueCandidates(values, index):
                cost = bit_count + costs[token.next_index]
                if cost < best_cost:
                    best_cost = cost
                    best_choice = token

            costs[index] = best_cost
            choices[index] = best_choice

        tokens: List[ShortValueRleLenToken] = []
        index = 0
        while index < count:
            choice = choices[index]
            if choice is None:
                raise RuntimeError("missing RLE short value token choice")
            tokens.append(choice)
            index = choice.next_index
        return tokens

    def _iterShortValueCandidates(self, values: Sequence[int], index: int):
        parameter = self._parameter
        if parameter is None:
            return

        value_bits = self._value_bits
        run_max = self._run_max
        run_bits = self._run_bits
        if value_bits is None or run_max is None or run_bits is None:
            return
        max_value = 1 << value_bits
        token_values: List[int] = []
        for run in range(1, run_max + 1):
            end = index + run
            if end > len(values):
                break
            value = values[end - 1]
            if not 1 <= value <= max_value:
                break
            token_values.append(value)
            if run >= parameter.run_min:
                bit_count = 1 + run_bits + value_bits * run
                yield bit_count, ShortValueRleLenToken(
                    "short_value", 0, tuple(token_values), end)

    def _writeShortValueToken(self, writer: ABytesWriter, values: Sequence[int]) -> None:
        parameter = self._parameter
        if parameter is None:
            raise ValueError(f"short value token is not supported at resolution: {self.resolution}")

        value_bits = self._value_bits
        run_bits = self._run_bits
        run_max = self._run_max
        if value_bits is None or run_bits is None or run_max is None:
            raise ValueError(f"short value token is not supported at resolution: {self.resolution}")

        run = len(values)
        if not parameter.run_min <= run <= run_max:
            raise ValueError(f"invalid short value token run length: {run}")

        max_value = 1 << value_bits
        writer.writeBitsFromInt32(1, 1)
        writer.writeBitsFromInt32(run - parameter.run_min, run_bits)
        for value in values:
            if not 1 <= value <= max_value:
                raise ValueError(f"short value token value out of range: {value}")
            writer.writeBitsFromInt32(value - 1, value_bits)

    def _readToken(self, reader: ABytesReader, values: List[int], count: int) -> None:
        prefix = reader.readBitsAsInt32(1)
        if prefix == 0:
            if len(values) >= count:
                raise ValueError("MBUInt token exceeds requested count")
            values.append(reader.readMbUInt())
            return
        self._readShortValueToken(reader, values, count)

    def _readShortValueToken(self, reader: ABytesReader, values: List[int], count: int) -> None:
        parameter = self._parameter
        if parameter is None:
            raise ValueError(f"short value token is not supported at resolution: {self.resolution}")
        value_bits = self._value_bits
        run_bits = self._run_bits
        run_max = self._run_max
        if value_bits is None or run_bits is None or run_max is None:
            raise ValueError(f"short value token is not supported at resolution: {self.resolution}")

        run = reader.readBitsAsInt32(run_bits) + parameter.run_min
        if run > run_max:
            raise ValueError(f"invalid short value token run length: {run}")
        if len(values) + run > count:
            raise ValueError("short value token exceeds requested count")
        for _ in range(run):
            values.append(reader.readBitsAsInt32(value_bits) + 1)

    @staticmethod
    def _validateParameter(parameter: ShortValueRleLenParameter) -> None:
        """run_codeが指定bit幅に収まることを起動時に確認する。"""
        if parameter.run_bits <= 0:
            raise ValueError("run_bits must be positive")
        if parameter.base_value_bits <= 0:
            raise ValueError("base_value_bits must be positive")
        if parameter.run_min <= 0:
            raise ValueError("run_min must be positive")
        if parameter.run_max < parameter.run_min:
            raise ValueError("run_max must be greater than or equal to run_min")
        if parameter.run_max - parameter.run_min >= (1 << parameter.run_bits):
            raise ValueError("run range does not fit in run_bits")
