from os import PathLike, SEEK_CUR, path as os_path

from .ABytesReader import ABytesReader


class FileBytesBufferedReader(ABytesReader):
    """ローカルファイルを前進読出しするバッファ付きReader。

    ``offset`` をReaderの起点とし、前方skipにはファイルseekを使用する。
    Readerをcloseすると内部で開いたファイルもcloseする。
    """

    def __init__(
        self,
        path: str | PathLike[str],
        buffer_size: int = 8192,
        *,
        offset: int = 0,
    ):
        super().__init__()
        if buffer_size < 1:
            raise ValueError("buffer_size must be greater than zero")
        if offset < 0:
            raise ValueError("offset must not be negative")
        source_size = os_path.getsize(path)
        if offset > source_size:
            raise ValueError("offset exceeds file size")
        self._src = open(path, "rb", buffering=0)
        self._src.seek(offset)
        self._buffer_size = buffer_size
        self._buffer = b""
        self._buffer_pos = 0
        self._pos = 0
        self._length = source_size - offset
        self._closed = False

    @property
    def pos(self) -> int:
        """Reader起点から論理的に消費したbyte数。"""
        return self._pos

    def _fillBuffer(self) -> bool:
        if self._closed:
            raise ValueError("I/O operation on closed reader")
        self._buffer = self._src.read(self._buffer_size)
        self._buffer_pos = 0
        return len(self._buffer) > 0

    def _available(self) -> int:
        return len(self._buffer) - self._buffer_pos

    def _nextByte(self) -> int:
        if self._available() == 0 and not self._fillBuffer():
            raise StopIteration()
        value = self._buffer[self._buffer_pos]
        self._buffer_pos += 1
        self._pos += 1
        return value

    def _skipByte(self, n: int):
        assert n >= 0
        if self._pos + n > self._length:
            self._skipByteUnchecked(self._length - self._pos)
            raise StopIteration()
        self._skipByteUnchecked(n)

    def _skipByteUnchecked(self, n: int) -> None:
        available = self._available()
        if n <= available:
            self._buffer_pos += n
            self._pos += n
            return
        if available > 0:
            self._buffer_pos += available
            self._pos += available
            n -= available
        if n > 0:
            self._src.seek(n, SEEK_CUR)
            self._buffer = b""
            self._buffer_pos = 0
            self._pos += n

    def readBytes(self, n: int) -> list[int]:
        """int配列としてnバイト読み出す。"""
        if self._nleft != 0:
            return super().readBytes(n)
        return list(self.readAsBytes(n))

    def readAsBytes(self, n: int) -> bytes:
        """bytesとしてnバイト読み出す。byte境界ではまとめて読む。"""
        assert n >= 0
        if self._nleft != 0:
            return bytes(super().readBytes(n))

        result = bytearray()
        while n > 0:
            if self._available() == 0 and not self._fillBuffer():
                raise IndexError()
            count = min(n, self._available())
            start = self._buffer_pos
            self._buffer_pos += count
            self._pos += count
            result.extend(self._buffer[start : start + count])
            n -= count
        return bytes(result)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._buffer = b""
        self._buffer_pos = 0
        self._src.close()
