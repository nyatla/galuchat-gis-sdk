from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ...io import BytesBufferReader
from .record_stream import decode_record_stream_reader_target_with_token_getter
from .TextTableChunk import assert_pages_sorted


@dataclass(frozen=True)
class MappedTextTablePage:
    record_token_count: int
    page_record_count: int
    record_stream_start: int
    record_stream_size: int
    page_header: int = 0


@dataclass(frozen=True)
class TextTableChunkReader:
    record_count: int
    page_size: int
    page_count: int
    token_bits: int
    pages: tuple[MappedTextTablePage, ...]

    @classmethod
    def unpack(cls, src: bytes, offset: int, size: int) -> "TextTableChunkReader":
        reader = BytesBufferReader(src, offset=offset)
        record_count = reader.readMbUInt()
        page_size = reader.readMbUInt()
        page_count = reader.readMbUInt()
        token_bits = reader.readMbUInt()
        if not 1 <= token_bits <= 16:
            raise ValueError("invalid TT00 token_bits")
        pages = tuple(read_mapped_page(reader, offset) for _ in range(page_count))
        if reader.pos != size:
            raise ValueError("TT00 has trailing bytes")
        if sum(page.page_record_count for page in pages) != record_count:
            raise ValueError("TT00 record count mismatch")
        assert_pages_sorted(pages)
        return cls(
            record_count=record_count,
            page_size=page_size,
            page_count=page_count,
            token_bits=token_bits,
            pages=pages,
        )


MappedTextTableChunk = TextTableChunkReader


def parse_mapped_tt00_data(src: bytes, offset: int, size: int) -> TextTableChunkReader:
    return TextTableChunkReader.unpack(src, offset, size)


def read_mapped_page(reader: BytesBufferReader, chunk_offset: int) -> MappedTextTablePage:
    page_header = reader.readByte()
    if page_header != 0:
        raise ValueError("unsupported TT00 PageHeader")
    record_token_count = reader.readMbUInt()
    page_record_count = reader.readMbUInt()
    record_stream_size = reader.readMbUInt()
    record_stream_start = chunk_offset + reader.pos
    reader.skipInByte(record_stream_size)
    return MappedTextTablePage(
        record_token_count=record_token_count,
        page_record_count=page_record_count,
        record_stream_start=record_stream_start,
        record_stream_size=record_stream_size,
        page_header=page_header,
    )


def decode_mapped_page_record_with_token_getter(
    src: bytes,
    page: MappedTextTablePage,
    index_in_page: int,
    token_bits: int,
    token_getter: Callable[[int], bytes],
) -> bytes:
    if not 0 <= index_in_page < page.page_record_count:
        raise IndexError("TT00 page record index out of range")
    reader = BytesBufferReader(src, offset=page.record_stream_start)
    result = decode_record_stream_reader_target_with_token_getter(
        reader,
        page.page_record_count,
        index_in_page,
        token_bits,
        token_getter,
    )
    if reader.pos > page.record_stream_size:
        raise ValueError("TT00 mapped RecordStream overread")
    return result
