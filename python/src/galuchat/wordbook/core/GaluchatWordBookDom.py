from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ...chunk import Chunk
from ...io import BytesBufferReader, BytesWriter
from ..chunk.common import read_mapped_chunk
from ..chunk.WordBookHeaderChunk import WordBookHeaderChunk, parse_nm00_data, write_nm00_data
from ..chunk.WordBookHeaderChunkReader import parse_mapped_nm00_data
from ..chunk.TokenMapChunk import TokenMapChunk, parse_tm00_data, write_tm00_data
from ..chunk.TokenMapChunkReader import parse_mapped_tm00_data
from ..chunk.TextTableChunk import (
    TextTableChunk,
    build_text_table,
    decode_page_records_as_token_ids,
    parse_tt00_data,
    write_tt00_data,
)
from ..chunk.TextTableChunkReader import (
    decode_mapped_page_record_with_token_getter,
    parse_mapped_tt00_data,
)
from .constants import DEFAULT_PAGE_SIZE, TEXT_TABLE_CHUNK, TOKEN_MAP_CHUNK, WORDBOOK_HEADER_CHUNK
from .WordBookModel import WordBookModel, required_token_bits


@dataclass(frozen=True)
class GaluchatWordBookDom:
    header: WordBookHeaderChunk
    token_map: TokenMapChunk
    text_table: TextTableChunk

    @classmethod
    def createFromTexts(
        cls,
        texts: Iterable[str],
        page_size: int = DEFAULT_PAGE_SIZE,
        metadata: str | None = None,
        token_bits: int | None = None,
    ) -> "GaluchatWordBookDom":
        return cls.createFromModel(
            WordBookModel.from_texts(texts, page_size=page_size),
            metadata=metadata,
            token_bits=token_bits,
        )

    @classmethod
    def createFromItems(
        cls,
        items: Iterable[tuple[int, str]],
        page_size: int = DEFAULT_PAGE_SIZE,
        metadata: str | None = None,
        token_bits: int | None = None,
    ) -> "GaluchatWordBookDom":
        return cls.createFromModel(
            WordBookModel.from_items(items, page_size=page_size),
            metadata=metadata,
            token_bits=token_bits,
        )

    @classmethod
    def createFromModel(
        cls,
        model: WordBookModel,
        metadata: str | None = None,
        token_bits: int | None = None,
    ) -> "GaluchatWordBookDom":
        required_bits = required_token_bits(len(model.tokens))
        if token_bits is None:
            token_bits = required_bits
        if not 1 <= token_bits <= 16:
            raise ValueError("token_bits must be in 1..16")
        if token_bits < required_bits:
            raise ValueError("token_bits is smaller than token table requires")
        return cls(
            header=WordBookHeaderChunk(metadata=metadata),
            token_map=TokenMapChunk(tokens=model.tokens),
            text_table=build_text_table(
                model.records,
                model.page_size,
                token_bits,
            ),
        )

    @classmethod
    def pack(cls, src: "GaluchatWordBookDom") -> bytes:
        writer = BytesWriter()
        Chunk.pack(WORDBOOK_HEADER_CHUNK, write_nm00_data(src.header), writer)
        Chunk.pack(TOKEN_MAP_CHUNK, write_tm00_data(src.token_map), writer)
        Chunk.pack(TEXT_TABLE_CHUNK, write_tt00_data(src.text_table), writer)
        return bytes(writer.buffer)

    @classmethod
    def unpack(cls, src: bytes) -> "GaluchatWordBookDom":
        reader = BytesBufferReader(src)
        header_chunk = Chunk.unpack(reader)
        if header_chunk.name != WORDBOOK_HEADER_CHUNK:
            raise ValueError("WordBook must start with NM00")
        token_chunk = Chunk.unpack(reader)
        if token_chunk.name != TOKEN_MAP_CHUNK:
            raise ValueError("WordBook must contain TM00 after NM00")
        text_chunk = Chunk.unpack(reader)
        if text_chunk.name != TEXT_TABLE_CHUNK:
            raise ValueError("WordBook must contain TT00 after TM00")
        if reader.pos != len(src):
            raise ValueError("WordBook has trailing bytes")
        header = parse_nm00_data(header_chunk.data)
        token_map = parse_tm00_data(token_chunk.data)
        text_table = parse_tt00_data(text_chunk.data)
        if text_table.token_bits < required_token_bits(len(token_map.tokens)):
            raise ValueError("TT00 token_bits is smaller than TM00 token table requires")
        return cls(header=header, token_map=token_map, text_table=text_table)

    def toModel(self) -> WordBookModel:
        records: list[tuple[int, ...]] = []
        table = self.text_table
        for page in table.pages:
            records.extend(decode_page_records_as_token_ids(
                page,
                table.token_bits,
            ))
        if len(records) != table.record_count:
            raise ValueError("WordBook record count mismatch while restoring model")
        return WordBookModel(
            page_size=table.page_size,
            tokens=self.token_map.tokens,
            records=tuple(records),
        )


class GaluchatWordBookReader:
    def __init__(self, header, token_map, text_table):
        self._header = header
        self._token_map = token_map
        self._text_table = text_table

    @classmethod
    def unpack(
        cls,
        src: bytes,
        token_cache_size: int = 64,
    ) -> "GaluchatWordBookReader":
        reader = BytesBufferReader(src)
        header_chunk = read_mapped_chunk(reader, len(src))
        if header_chunk.name != WORDBOOK_HEADER_CHUNK:
            raise ValueError("WordBook must start with NM00")
        token_chunk = read_mapped_chunk(reader, len(src))
        if token_chunk.name != TOKEN_MAP_CHUNK:
            raise ValueError("WordBook must contain TM00 after NM00")
        text_chunk = read_mapped_chunk(reader, len(src))
        if text_chunk.name != TEXT_TABLE_CHUNK:
            raise ValueError("WordBook must contain TT00 after TM00")
        if reader.pos != len(src):
            raise ValueError("WordBook has trailing bytes")
        header = parse_mapped_nm00_data(src, header_chunk.data_start, header_chunk.size)
        token_map = parse_mapped_tm00_data(
            src,
            token_chunk.data_start,
            token_chunk.size,
            cache_size=token_cache_size,
        )
        text_table = parse_mapped_tt00_data(src, text_chunk.data_start, text_chunk.size)
        if text_table.token_bits < required_token_bits(token_map.token_count):
            raise ValueError("TT00 token_bits is smaller than TM00 token table requires")
        return cls(header, token_map, text_table)

    @property
    def record_count(self) -> int:
        return self._text_table.record_count

    @property
    def page_size(self) -> int:
        return self._text_table.page_size

    @property
    def token_count(self) -> int:
        return self._token_map.token_count

    def readBytes(self, code: int) -> bytes:
        table = self._text_table
        if not 0 <= code < table.record_count:
            raise KeyError(code)
        record_base = 0
        for page in table.pages:
            if code < record_base + page.page_record_count:
                return decode_mapped_page_record_with_token_getter(
                    self._token_map.data,
                    page,
                    code - record_base,
                    table.token_bits,
                    self._token_map.get,
                )
            record_base += page.page_record_count
        raise KeyError(code)

    def read(self, code: int) -> str:
        return self.readBytes(code).decode("utf-8")
