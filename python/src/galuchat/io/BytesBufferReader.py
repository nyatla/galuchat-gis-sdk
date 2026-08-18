from .ABytesReader import ABytesReader


class BytesBufferReader(ABytesReader):
    """BufferをラップするReaderです。"""

    def __init__(self, src: bytes, offset: int = 0):
        """src[offset]を起点とします。"""
        super().__init__()
        self._src = src
        self._offset = offset
        self._pos = 0

    @property
    def pos(self) -> int:
        """Reader起点からの相対位置。"""
        return self._pos

    def _skipByte(self, n: int):
        if self._pos + n <= len(self._src):
            self._pos += n
        else:
            self._pos = len(self._src)
            raise StopIteration()

    def _nextByte(self) -> int:
        value = self._src[self._pos + self._offset]
        self._pos += 1
        assert 0 <= value < 256
        return value

    def readBytes(self, n: int) -> list[int]:
        """int配列としてnバイト読み出す。byte境界ではsliceでまとめて読む。"""
        if self._nleft != 0:
            return super().readBytes(n)
        start = self._offset + self._pos
        end = start + n
        data = self._src[start:end]
        if len(data) != n:
            raise IndexError()
        self._pos += n
        return list(data)

    def readAsBytes(self, n: int) -> bytes:
        """bytesとしてnバイト読み出す。byte境界ではsliceでまとめて読む。"""
        if self._nleft != 0:
            return super().readAsBytes(n)
        start = self._offset + self._pos
        end = start + n
        data = self._src[start:end]
        if len(data) != n:
            raise IndexError()
        self._pos += n
        return bytes(data)
