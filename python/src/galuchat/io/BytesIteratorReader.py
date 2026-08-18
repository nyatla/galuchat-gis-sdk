from typing import Iterator

from .ABytesReader import ABytesReader


class BytesIteratorReader(ABytesReader):
    def __init__(self, src: Iterator[int]):
        super().__init__()
        self._src = src
        self._pos = 0

    @property
    def pos(self) -> int:
        """Reader起点からの相対位置。"""
        return self._pos

    def _skipByte(self, n: int):
        for _ in range(n):
            self._pos += 1
            next(self._src)

    def _nextByte(self) -> int:
        value = next(self._src)
        self._pos += 1
        assert 0 <= value < 256
        return value

    @classmethod
    def wrapByteReader(cls, src: ABytesReader) -> "BytesIteratorReader":
        class Iter(Iterator):
            def __init__(self, src: ABytesReader):
                self._src = src

            def __next__(self):
                return self._src.readByte()

        return BytesIteratorReader(Iter(src))


# 旧SubByteIteratorReaderの参考実装は、ABytesReaderに統合済み。
# class SubByteIteratorReader(ABytesReader):
#     """バイトストリームから任意ビットのSubbyte値及びbyte値を読み出す。
#
#     SubByteを読みだした場合、初めの1ビット目を読みだした時点でposは
#     カウントアップする。
#     """
#
#     def __init__(self, src: Iterator[int]):
#         self._src = src
#         self._nleft = 0
#         self._cleft = 0
#         self._pos = 0
#
#     @classmethod
#     def wrapByteReader(cls, src: ABytesReader) -> "SubByteIteratorReader":
#         class Iter(Iterator):
#             def __init__(self, src: ABytesReader):
#                 self._src = src
#
#             def __next__(self):
#                 return self._src.readByte()
#
#         return SubByteIteratorReader(Iter(src))
#
#     @property
#     def pos(self) -> int:
#         return self._pos
#
#     def readBitsAsInt32(self, bits: int):
#         assert bits < 8
#         c = self._cleft
#         left = self._nleft
#         mask = (1 << bits) - 1
#         if bits <= left:
#             value = c >> (left - bits)
#             result = value & mask
#             self._nleft -= bits
#             return result
#         tmp = (c << 8) | next(self._src)
#         self._pos += 1
#         result = tmp >> (left + 8 - bits) & mask
#         self._nleft = self._nleft + 8 - bits
#         assert self._nleft <= 8
#         self._cleft = tmp & ((1 << self._nleft) - 1)
#         return result
#
#     def readByte(self):
#         left = self._nleft
#         next_byte = next(self._src)
#         self._pos += 1
#         if left == 0:
#             return next_byte
#         c = self._cleft
#         tmp = (c << 8) | next_byte
#         result = (tmp >> left) & 0xff
#         self._cleft = tmp & ((1 << left) - 1)
#         return result
