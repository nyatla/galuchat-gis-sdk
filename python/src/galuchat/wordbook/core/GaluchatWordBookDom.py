from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ...chunk import Chunk
from ...io import BytesBufferReader, BytesWriter
from ..chunk.WordBookHeaderChunk import WordBookHeaderChunk, parse_nm00_data, write_nm00_data
from ..chunk.TokenMapChunk import TokenMapChunk, parse_tm00_data, write_tm00_data
from ..chunk.TextTableChunk import (
    TextTableChunk,
    build_text_table,
    decode_page_records_as_token_ids,
    parse_tt00_data,
    write_tt00_data,
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

    def toBytes(self) -> bytes:
        writer = BytesWriter()
        Chunk.pack(WORDBOOK_HEADER_CHUNK, write_nm00_data(self.header), writer)
        Chunk.pack(TOKEN_MAP_CHUNK, write_tm00_data(self.token_map), writer)
        Chunk.pack(TEXT_TABLE_CHUNK, write_tt00_data(self.text_table), writer)
        return bytes(writer.buffer)

    @classmethod
    def fromBytes(cls, src: bytes) -> "GaluchatWordBookDom":
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
