from typing import Sequence

from .ABytesWriter import ABytesWriter


class BytesWriter(ABytesWriter):
    def __init__(self):
        super().__init__()
        self._buffer = bytearray()

    def __len__(self) -> int:
        return len(self._buffer) + (0 if self._nleft == 0 else 1)

    def _putByte(self, v: int) -> int:
        assert v <= 255
        self._buffer.append(v)
        return 1

    def writeBytes(self, values: Sequence[int]):
        if self._nleft == 0:
            self._buffer.extend(values)
        else:
            super().writeBytes(values)
        return len(values)

    @property
    def buffer(self) -> bytearray:
        """端数ビットをパディングしてバッファを返します。"""
        if self._nleft > 0:
            result = self._buffer.copy()
            result.append(self._cleft << (8 - self._nleft))
            return result
        return self._buffer


# 旧SubByteWriterの参考実装は、ABytesWriter/BytesWriterに統合済み。
# class SubByteWriter(ABytesWriter):
#     """任意ビットのSubbyte値及びbyte値をバイトストリームに書き出す。"""
#
#     def __init__(self):
#         self._buffer = bytearray()
#         self._nleft = 0
#         self._cleft = 0
#
#     def __len__(self):
#         return len(self._buffer) + (1 if self._nleft > 0 else 0)
#
#     def writeBitsFromInt32(self, v: int, bits: int):
#         assert 0 <= bits and bits <= 8
#         assert v <= (1 << bits)
#
#         v &= (1 << bits) - 1
#         if self._nleft + bits <= 8:
#             self._cleft = (self._cleft << bits) | v
#             self._nleft += bits
#             if self._nleft == 8:
#                 self._buffer.append(self._cleft)
#                 self._nleft = 0
#                 self._cleft = 0
#         else:
#             remaining_bits = 8 - self._nleft
#             self._cleft = (self._cleft << remaining_bits) | (v >> (bits - remaining_bits))
#             self._buffer.append(self._cleft)
#             self._cleft = v & ((1 << (bits - remaining_bits)) - 1)
#             self._nleft = bits - remaining_bits
#
#     def writeByte(self, v: int):
#         assert v <= 255
#         if self._nleft == 0:
#             self._buffer.append(v)
#         else:
#             self._cleft = (self._cleft << (8 - self._nleft)) | (v >> self._nleft)
#             self._buffer.append(self._cleft)
#             self._cleft = v & ((1 << self._nleft) - 1)
#
#     @property
#     def buffer(self) -> bytearray:
#         if self._nleft > 0:
#             r = self._buffer.copy()
#             r.append(self._cleft << (8 - self._nleft))
#             return r
#         return self._buffer
