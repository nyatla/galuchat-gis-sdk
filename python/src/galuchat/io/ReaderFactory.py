from abc import ABC, abstractmethod
from os import PathLike

from .ABytesReader import ABytesReader
from .BytesBufferReader import BytesBufferReader
from .FileBytesBufferedReader import FileBytesBufferedReader


class ReaderFactory(ABC):
    """Reader起点を指定して、新しい逐次Readerを生成する。"""

    @abstractmethod
    def create(self, offset: int = 0) -> ABytesReader:
        ...


class BytesReaderFactory(ReaderFactory):
    def __init__(self, src: bytes):
        self._src = src

    def create(self, offset: int = 0) -> ABytesReader:
        if offset < 0:
            raise ValueError("offset must not be negative")
        return BytesBufferReader(self._src, offset=offset)


class FileReaderFactory(ReaderFactory):
    def __init__(self, path: str | PathLike[str], buffer_size: int = 8192):
        if buffer_size < 1:
            raise ValueError("buffer_size must be greater than zero")
        self._path = path
        self._buffer_size = buffer_size

    def create(self, offset: int = 0) -> ABytesReader:
        if offset < 0:
            raise ValueError("offset must not be negative")
        return FileBytesBufferedReader(
            self._path,
            buffer_size=self._buffer_size,
            offset=offset,
        )
