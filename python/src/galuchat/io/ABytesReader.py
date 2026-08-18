from abc import ABC, abstractmethod
from typing import List, Sequence

from .MBIntDef import MBIntDef


class ABytesReader(ABC):
    """データソースからの読出しクラス。

    byte単位の読出しメソッド_nextByteを継承クラスで実装する。
    """

    def __init__(self):
        self._nleft = 0
        self._cleft = 0  # キャッシュ

    @classmethod
    def toBitWidth(cls, n: int) -> int:
        """n種類を表現できるビット幅を返します。"""
        if n <= 2:
            return 1
        elif n <= 4:
            return 2
        elif n <= 16:
            return 4
        elif n <= 256:
            return 8
        else:
            raise RuntimeError()

    @abstractmethod
    def _nextByte(self) -> int:
        """データソースから1バイトを読み出す。"""
        ...

    @abstractmethod
    def _skipByte(self, n: int):
        """データソースをnバイト読み飛ばす。"""
        ...

    @property
    def bitOffset(self) -> int:
        """現在のbyte内に残っている未消費bit数を返す。0ならbyte境界。"""
        return self._nleft

    @property
    def isByteAligned(self) -> bool:
        """現在の読み出し位置がbyte境界ならTrueを返す。"""
        return self._nleft == 0

    def readBitsAsInt32(self, bits: int) -> int:
        """最大31bitをMSB-firstで読み、右詰めintとして返す。"""
        assert 0 <= bits <= 31
        if bits == 0:
            return 0

        result = 0
        left = self._nleft
        cache = self._cleft
        remaining = bits

        if left > 0:
            read_bits = left if left < remaining else remaining
            result = (cache >> (left - read_bits)) & ((1 << read_bits) - 1)
            left -= read_bits
            remaining -= read_bits
            cache &= (1 << left) - 1 if left > 0 else 0

        while remaining >= 8:
            result = (result << 8) | self._nextByte()
            remaining -= 8

        if remaining > 0:
            next_byte = self._nextByte()
            result = (result << remaining) | (next_byte >> (8 - remaining))
            left = 8 - remaining
            cache = next_byte & ((1 << left) - 1)

        self._nleft = left
        self._cleft = cache
        return result

    def readByte(self) -> int:
        left = self._nleft
        next_byte = self._nextByte()
        if left == 0:
            return next_byte
        c = self._cleft
        tmp = (c << 8) | next_byte
        result = (tmp >> left) & 0xff
        self._cleft = tmp & ((1 << left) - 1)
        return result

    def skipToByte(self) -> int:
        """現在のsub-bit読み出し位置を次のbyte境界へ進める。

        未消費の端数bitはパディングとして破棄する。
        実データbyteは追加で読み出さない。
        """
        skipped = self._nleft
        self._nleft = 0
        self._cleft = 0
        return skipped

    def skipBits(self, bit_count: int) -> None:
        """現在位置からbit_count bitを読み飛ばす。"""
        assert bit_count >= 0
        if bit_count == 0:
            return

        if self._nleft > 0:
            consume = min(self._nleft, bit_count)
            self._nleft -= consume
            bit_count -= consume
            self._cleft &= (1 << self._nleft) - 1 if self._nleft > 0 else 0
            if bit_count == 0:
                return

        byte_count = bit_count // 8
        if byte_count > 0:
            self._skipByte(byte_count)
            bit_count -= byte_count * 8

        if bit_count > 0:
            next_byte = self._nextByte()
            self._nleft = 8 - bit_count
            self._cleft = next_byte & ((1 << self._nleft) - 1)

    def readSubBytesWithMap(self, n: int, vset: Sequence[int]) -> List[int]:
        """subByteをN個読みだして、vsetのテーブルで変換して返す。"""
        nbit = self.toBitWidth(len(vset))
        assert (nbit * n) % 8 == 0
        data = []
        mask = 2**nbit - 1
        for _ in range(n // (8 // nbit)):
            value = self.readByte()
            for i in range(8 // nbit):
                data.append(vset[(value >> (8 - nbit * (i + 1))) & mask])
        return data

    def readSubBytes(self, n: int, nbits: int) -> List[int]:
        """subByteをbits単位でN個を読みだす。"""
        assert (nbits * n) % 8 == 0
        data = []
        mask = 2**nbits - 1
        for _ in range(n // (8 // nbits)):
            value = self.readByte()
            for i in range(8 // nbits):
                data.append((value >> (8 - nbits * (i + 1))) & mask)
        return data

    def skipInByte(self, n: int):
        assert n >= 0
        if n < 1:
            return
        if self._nleft == 0:
            self._skipByte(n)
        else:
            if n > 1:
                self._skipByte(n - 1)
            self.readByte()

    def skipMbUInt(self, n: int = 1):
        """現在位置からn個のMbUintをスキップします。"""
        for _ in range(n):
            count = self.readByte()
            if count < MBIntDef.MUINT2_BASE:
                continue
            elif count == 255:
                self.skipInByte(1)
                continue
            elif count == 254:
                self.skipInByte(2)
                continue
            elif count == 253:
                self.skipInByte(3)
                continue
            elif count == 252:
                self.skipInByte(4)
                continue
            else:
                raise RuntimeError()

    def readBytes(self, n: int) -> List[int]:
        """int配列として返す。"""
        return [self.readByte() for _ in range(n)]

    def readAsBytes(self, n: int) -> bytes:
        """bytesとしてnバイト読み出す。"""
        return bytes(self.readBytes(n))

    def readAsBitBytes(self, bit_count: int) -> bytes:
        """bit_count bitだけ読み出し、bytesとして返す。

        読み出し位置はbit_count分だけ進める。byte境界への読み飛ばしはしない。
        戻り値の末尾byteに未使用bitがある場合は0でpaddingする。
        """
        assert bit_count >= 0
        byte_count = bit_count // 8
        rest_bits = bit_count % 8
        result = bytearray(self.readAsBytes(byte_count))
        if rest_bits > 0:
            result.append(self.readBitsAsInt32(rest_bits) << (8 - rest_bits))
        return bytes(result)

    def readMbUInt(self) -> int:
        count = self.readByte()
        if count < MBIntDef.MUINT2_BASE:
            return count
        elif count == 255:
            return self.readBytes(1)[0] + MBIntDef.MUINT2_BASE
        elif count == 254:
            t = self.readBytes(2)
            return ((t[0] << 8) | t[1]) + MBIntDef.MUINT3_BASE
        elif count == 253:
            t = self.readBytes(3)
            return ((t[0] << 16) | (t[1] << 8) | t[2]) + MBIntDef.MUINT4_BASE
        elif count == 252:
            t = self.readBytes(4)
            return ((t[0] << 24) | (t[1] << 16) | (t[2] << 8) | t[3]) + MBIntDef.MUINT5_BASE
        raise RuntimeError()

    def readMbInt(self) -> int:
        count = self.readByte()
        sign = -1 if count & 0x80 != 0 else 1
        count = count & 0x7f
        if count < MBIntDef.MINT2_BASE:
            return count * sign
        elif count == 127:
            return (self.readBytes(1)[0] + MBIntDef.MINT2_BASE) * sign
        elif count == 126:
            t = self.readBytes(2)
            return (((t[0] << 8) | t[1]) + MBIntDef.MINT3_BASE) * sign
        elif count == 125:
            t = self.readBytes(3)
            return (((t[0] << 16) | (t[1] << 8) | t[2]) + MBIntDef.MINT4_BASE) * sign
        elif count == 124:
            t = self.readBytes(4)
            return (((t[0] << 24) | (t[1] << 16) | (t[2] << 8) | t[3]) + MBIntDef.MINT5_BASE) * sign
        raise RuntimeError()

    def readMbUInts(self, n: int) -> List[int]:
        return [self.readMbUInt() for _ in range(n)]

    def readBytesAsBStr(self, size: int) -> bytes:
        """sizeバイトを文字列として読み取ります。後端の0は省略します。"""
        return self.readAsBytes(size).split(b"\0", 1)[0]
