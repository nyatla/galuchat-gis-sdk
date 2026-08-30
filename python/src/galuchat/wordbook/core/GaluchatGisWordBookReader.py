from __future__ import annotations

from os import PathLike, path as os_path
from typing import Iterable, Iterator

from ...io import BytesReaderFactory, FileReaderFactory, ReaderFactory
from ..chunk.WordBookHeaderChunk import read_gw00_data
from ..chunk.HierarchicalIndexChunk import required_code_bits
from ..chunk.HierarchicalIndexChunkReader import HierarchicalIndexChunkReader
from ._ReaderSupport import WordBookTextReader, iter_index_batches, read_chunk_layout
from .constants import (
    GISWORDBOOK_HEADER_CHUNK,
    HIERARCHICAL_INDEX_CHUNK,
    TEXT_TABLE_CHUNK,
    TOKEN_MAP_CHUNK,
)
from .WordBookModel import normalize_text_token_encoding


class GaluchatGisWordBookReader:
    def __init__(
        self,
        reader_factory: ReaderFactory,
        source_size: int,
        token_cache_size: int = 64,
    ) -> None:
        header_chunk, token_chunk, text_chunk, index_chunk = read_chunk_layout(
            reader_factory,
            source_size,
            (
                GISWORDBOOK_HEADER_CHUNK,
                TOKEN_MAP_CHUNK,
                TEXT_TABLE_CHUNK,
                HIERARCHICAL_INDEX_CHUNK,
            ),
        )
        with reader_factory.create(header_chunk.data_start) as reader:
            self._header = read_gw00_data(reader, header_chunk.size)
        self._text_reader = WordBookTextReader(
            reader_factory,
            token_chunk,
            text_chunk,
            token_cache_size,
        )
        with reader_factory.create(index_chunk.data_start) as reader:
            index = HierarchicalIndexChunkReader.unpack(reader, index_chunk.size)
            self._record_count = index.record_count
            self._depth = index.max_depth
            index_code_bits = index.code_bits
        if index_code_bits < required_code_bits(self._text_reader.record_count):
            raise ValueError("TI00 code_bits is smaller than TT00 text table requires")
        self._reader_factory = reader_factory
        self._index_chunk = index_chunk
        self._code_buffer = [0] * self._depth

    @classmethod
    def fromBytes(
        cls,
        src: bytes,
        token_cache_size: int = 64,
    ) -> "GaluchatGisWordBookReader":
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
    ) -> "GaluchatGisWordBookReader":
        return cls(
            FileReaderFactory(file_path, buffer_size=buffer_size),
            os_path.getsize(file_path),
            token_cache_size=token_cache_size,
        )

    @property
    def record_count(self) -> int:
        return self._record_count

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def component_count(self) -> int:
        return self._text_reader.record_count

    def readCodeSet(self, index: int, out: list[int] | None = None) -> list[int]:
        with self._reader_factory.create(self._index_chunk.data_start) as reader:
            return HierarchicalIndexChunkReader.unpack(
                reader,
                self._index_chunk.size,
            ).readCodeSet(index, out)

    def iterCodeSetsFor(
        self,
        indices: Iterable[int],
        reuse_out: bool = False,
        run_buffer_limit: int = 256,
    ) -> Iterator[list[int]]:
        shared_out: list[int] = []
        for batch in iter_index_batches(indices, run_buffer_limit):
            with self._reader_factory.create(self._index_chunk.data_start) as reader:
                index_reader = HierarchicalIndexChunkReader.unpack(
                    reader,
                    self._index_chunk.size,
                )
                for codes in index_reader.iterCodeSetsFor(batch, reuse_out=reuse_out):
                    if reuse_out:
                        shared_out[:] = codes
                        yield shared_out
                    else:
                        yield codes

    def readComponentBytes(self, code: int) -> bytes:
        return self._text_reader.readBytes(code)

    def readComponent(self, code: int, encoding: str = "utf-8") -> str:
        return self.readComponentBytes(code).decode(normalize_text_token_encoding(encoding))

    def readStringSet(
        self,
        index: int,
        out: list[str] | None = None,
        encoding: str = "utf-8",
    ) -> list[str]:
        codes = self.readCodeSet(index, self._code_buffer)
        return self._decodeStringSet(codes, out, encoding)

    def _decodeStringSet(
        self,
        codes: list[int],
        out: list[str] | None,
        encoding: str,
    ) -> list[str]:
        components = self._text_reader.readByteSets(codes)
        normalized_encoding = normalize_text_token_encoding(encoding)
        if out is None:
            out = []
        else:
            out.clear()
        for code in codes:
            out.append(components[code].decode(normalized_encoding))
        return out

    def iterStringSetsFor(
        self,
        indices: Iterable[int],
        encoding: str = "utf-8",
        reuse_out: bool = False,
        run_buffer_limit: int = 256,
    ) -> Iterator[list[str]]:
        out: list[str] = []
        for codes in self.iterCodeSetsFor(
            indices,
            reuse_out=True,
            run_buffer_limit=run_buffer_limit,
        ):
            self._decodeStringSet(codes, out, encoding)
            yield out if reuse_out else list(out)
