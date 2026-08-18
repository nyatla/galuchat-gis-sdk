from abc import ABC, abstractmethod
from typing import Sequence

from ..math import toBitWidth
from .MBIntDef import MBIntDef


class ABytesWriter(ABC):
    """バイトストリームの出力インタフェイス。"""

    def __init__(self):
        self._nleft = 0
        self._cleft = 0  # キャッシュ

    @abstractmethod
    def __len__(self) -> int:
        ...

    @property
    @abstractmethod
    def buffer(self) -> bytearray:
        """継承先で出力した値にフラグメントを追加した値を生成します。"""
        ...

    @abstractmethod
    def _putByte(self, v: int) -> int:
        """継承先で値をストリームへ出力する関数を書きます。"""
        ...

    @property
    def bitOffset(self) -> int:
        """現在のbyte内に保持している未出力bit数を返す。0ならbyte境界。"""
        return self._nleft

    @property
    def isByteAligned(self) -> bool:
        """現在の書き込み位置がbyte境界ならTrueを返す。"""
        return self._nleft == 0

    def writeMbUInt(self, v: int) -> int:
        """最大5バイトのマルチバイトUIntを格納する。"""
        if v < MBIntDef.MUINT2_BASE:
            self.writeByte(v)
            return 1
        elif v < MBIntDef.MUINT3_BASE:
            w = v - MBIntDef.MUINT2_BASE
            self.writeBytes([255, w & 0xff])
            return 2
        elif v < MBIntDef.MUINT4_BASE:
            w = v - MBIntDef.MUINT3_BASE
            self.writeBytes([254, (w >> 8) & 0xff, w & 0xff])
            return 3
        elif v < MBIntDef.MUINT5_BASE:
            w = v - MBIntDef.MUINT4_BASE
            self.writeBytes([253, (w >> 16) & 0xff, (w >> 8) & 0xff, w & 0xff])
            return 4
        elif v < MBIntDef.MUINT5_BASE + 0xffffffff:
            w = v - MBIntDef.MUINT5_BASE
            self.writeBytes([252, (w >> 24) & 0xff, (w >> 16) & 0xff, (w >> 8) & 0xff, w & 0xff])
            return 5
        raise RuntimeError()

    def writeMbInt(self, v: int) -> int:
        sign = (1 if v < 0 else 0) << 7
        v = abs(v)
        if v < MBIntDef.MINT2_BASE:
            self.writeByte(sign | v)
            return 1
        elif v < MBIntDef.MINT3_BASE:
            w = v - MBIntDef.MINT2_BASE
            self.writeBytes([sign | 127, w & 0xff])
            return 2
        elif v < MBIntDef.MINT4_BASE:
            w = v - MBIntDef.MINT3_BASE
            self.writeBytes([sign | 126, (w >> 8) & 0xff, w & 0xff])
            return 3
        elif v < MBIntDef.MINT5_BASE:
            w = v - MBIntDef.MINT4_BASE
            self.writeBytes([sign | 125, (w >> 16) & 0xff, (w >> 8) & 0xff, w & 0xff])
            return 4
        elif v < MBIntDef.MINT5_BASE + 0xffffffff:
            w = v - MBIntDef.MINT5_BASE
            self.writeBytes([sign | 124, (w >> 24) & 0xff, (w >> 16) & 0xff, (w >> 8) & 0xff, w & 0xff])
            return 5
        raise RuntimeError()

    def writeMbUInts(self, values: Sequence[int]) -> int:
        result = 0
        for value in values:
            result += self.writeMbUInt(value)
        return result

    def writeBytes(self, values: Sequence[int]):
        for value in values:
            self.writeByte(value)
        return len(values)

    def writeBitBytes(self, values: bytes | bytearray | Sequence[int], bit_count: int) -> int:
        """valuesの先頭からbit_count bitだけ書き出す。

        byte境界へのpaddingは行わない。戻り値は書き出したbit数である。
        bit_countが8の倍数でない場合、最後のbyteは上位bitから必要分だけ使う。
        """
        assert bit_count >= 0
        assert len(values) * 8 >= bit_count
        byte_count = bit_count // 8
        rest_bits = bit_count % 8
        if byte_count > 0:
            self.writeBytes(values[:byte_count])
        if rest_bits > 0:
            self.writeBitsFromInt32(values[byte_count] >> (8 - rest_bits), rest_bits)
        return bit_count

    def writeSubByteWithMap(self, src: Sequence[int], vset: Sequence[int]):
        """ビット深度をlen(vset)としてサブバイト配列に変換して書き込みます。"""
        bit_width = toBitWidth(len(vset))
        dest = []
        value = 0
        count = 0
        for item in src:
            value = (value << bit_width) | vset.index(item)
            count += 1
            if count % (8 // bit_width) == 0:
                dest.append(value)
                value = 0
        rest = count % (8 // bit_width)
        if rest != 0:
            for _ in range(8 // bit_width - rest):
                value = value << bit_width
            dest.append(value)
        return self.writeBytes(dest)

    def writeBytesAsBStr(self, text: bytes, field_size: int = 0) -> int:
        """フィールドサイズを指定してテキストをバイト値として書き込みます。"""
        if field_size == 0:
            field_size = len(text)
        assert len(text) <= field_size
        self.writeBytes(text)
        rest = field_size - len(text)
        if rest > 0:
            self.writeBytes(b"\0" * rest)
        return field_size

    def writeBitsFromInt32(self, value: int, bits: int) -> int:
        """右詰めintの下位bitsをMSB-firstで最大31bitまで書き出す。"""
        assert 0 <= bits <= 31
        assert value >= 0
        if bits == 0:
            assert value == 0
            return 0
        assert value < (1 << bits)

        remaining = bits
        left = self._nleft
        cache = self._cleft

        if left > 0:
            free_bits = 8 - left
            write_bits = free_bits if free_bits < remaining else remaining
            shift = remaining - write_bits
            cache = (cache << write_bits) | ((value >> shift) & ((1 << write_bits) - 1))
            left += write_bits
            remaining -= write_bits
            if left == 8:
                self._putByte(cache)
                left = 0
                cache = 0

        while remaining >= 8:
            shift = remaining - 8
            self._putByte((value >> shift) & 0xff)
            remaining -= 8

        if remaining > 0:
            cache = (value & ((1 << remaining) - 1))
            left = remaining

        self._nleft = left
        self._cleft = cache
        return bits

    def writeByte(self, v: int):
        assert v <= 255
        if self._nleft == 0:
            self._putByte(v)
        else:
            self._cleft = (self._cleft << (8 - self._nleft)) | (v >> self._nleft)
            self._putByte(self._cleft)
            self._cleft = v & ((1 << self._nleft) - 1)

    def alignToByte(self, fill: int = 0) -> int:
        """現在のsub-bit書き込み位置をbyte境界へ揃える。

        端数bitがある場合、残りを`fill` bitで埋めて1byte出力する。
        戻り値は追加で出力したbyte数である。
        """
        assert fill in (0, 1)
        if self._nleft == 0:
            return 0
        value = self._cleft << (8 - self._nleft)
        if fill == 1:
            value |= (1 << (8 - self._nleft)) - 1
        self._putByte(value)
        self._nleft = 0
        self._cleft = 0
        return 1
