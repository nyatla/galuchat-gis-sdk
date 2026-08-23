from __future__ import annotations

from os import PathLike, path as os_path

from ...io import BytesReaderFactory, FileReaderFactory, ReaderFactory
from ..chunk.WordBookHeaderChunkReader import read_nm00_data
from ._ReaderSupport import WordBookTextReader, read_chunk_layout
from .constants import TEXT_TABLE_CHUNK, TOKEN_MAP_CHUNK, WORDBOOK_HEADER_CHUNK


class GaluchatWordBookReader:
    def __init__(
        self,
        reader_factory: ReaderFactory,
        source_size: int,
        token_cache_size: int = 64,
    ) -> None:
        header_chunk, token_chunk, text_chunk = read_chunk_layout(
            reader_factory,
            source_size,
            (WORDBOOK_HEADER_CHUNK, TOKEN_MAP_CHUNK, TEXT_TABLE_CHUNK),
        )
        with reader_factory.create(header_chunk.data_start) as reader:
            self._header = read_nm00_data(reader, header_chunk.size)
        self._text_reader = WordBookTextReader(
            reader_factory,
            token_chunk,
            text_chunk,
            token_cache_size,
        )

    @classmethod
    def fromBytes(
        cls,
        src: bytes,
        token_cache_size: int = 64,
    ) -> "GaluchatWordBookReader":
        return cls(
            BytesReaderFactory(src),
            len(src),
            token_cache_size=token_cache_size,
        )

    @classmethod
    def fromFile(
        cls,
        file_path: str | PathLike[str],
        buffer_size: int = 8192,
        token_cache_size: int = 64,
    ) -> "GaluchatWordBookReader":
        return cls(
            FileReaderFactory(file_path, buffer_size=buffer_size),
            os_path.getsize(file_path),
            token_cache_size=token_cache_size,
        )

    @property
    def record_count(self) -> int:
        return self._text_reader.record_count

    @property
    def token_count(self) -> int:
        return self._text_reader.token_count

    def readBytes(self, code: int) -> bytes:
        return self._text_reader.readBytes(code)

    def read(self, code: int) -> str:
        return self.readBytes(code).decode("utf-8")
