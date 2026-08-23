from typing import Iterator

from .ABytesReader import ABytesReader


class BytesIteratorReader(ABytesReader):
    def __init__(self, src: Iterator[int], offset: int = 0):
        super().__init__()
        if offset < 0:
            raise ValueError("offset must not be negative")
        self._src = src
        self._pos = 0
        self._skipByte(offset)
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
