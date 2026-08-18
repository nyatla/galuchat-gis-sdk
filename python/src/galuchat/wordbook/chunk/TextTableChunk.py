from __future__ import annotations

from dataclasses import dataclass
from ...io import BytesBufferReader, BytesWriter
from .record_stream import (
    decode_record_stream_as_token_ids,
    decode_record_stream_with_token_getter,
    write_record_stream,
)


@dataclass(frozen=True)
class TextTablePage:
    record_token_count: int
    page_record_count: int
    record_stream: bytes
    page_header: int = 0


@dataclass(frozen=True)
class TextTableChunk:
    record_count: int
    page_size: int
    page_count: int
    token_bits: int
    pages: tuple[TextTablePage, ...]


def build_text_table(
    records: tuple[tuple[int, ...], ...],
    page_size: int,
    token_bits: int,
) -> TextTableChunk:
    pages = build_pages(records, page_size, token_bits)
    return TextTableChunk(
        record_count=len(records),
        page_size=page_size,
        page_count=len(pages),
        token_bits=token_bits,
        pages=pages,
    )


def write_tt00_data(text_table: TextTableChunk) -> bytes:
    writer = BytesWriter()
    writer.writeMbUInt(text_table.record_count)
    writer.writeMbUInt(text_table.page_size)
    writer.writeMbUInt(len(text_table.pages))
    writer.writeMbUInt(text_table.token_bits)
    for page in text_table.pages:
        write_page(writer, page)
    return bytes(writer.buffer)


def parse_tt00_data(data: bytes) -> TextTableChunk:
    reader = BytesBufferReader(data)
    record_count = reader.readMbUInt()
    page_size = reader.readMbUInt()
    page_count = reader.readMbUInt()
    token_bits = reader.readMbUInt()
    if not 1 <= token_bits <= 16:
        raise ValueError("invalid TT00 token_bits")
    pages = tuple(read_page(reader) for _ in range(page_count))
    if reader.pos != len(data):
        raise ValueError("TT00 has trailing bytes")
    if sum(page.page_record_count for page in pages) != record_count:
        raise ValueError("TT00 record count mismatch")
    assert_pages_sorted(pages)
    return TextTableChunk(
        record_count=record_count,
        page_size=page_size,
        page_count=page_count,
        token_bits=token_bits,
        pages=pages,
    )


def assert_pages_sorted(pages) -> None:
    previous_token_count = -1
    for page in pages:
        if page.record_token_count < previous_token_count:
            raise ValueError("TT00 pages must be sorted by record_token_count")
        previous_token_count = page.record_token_count


def build_pages(
    records: tuple[tuple[int, ...], ...],
    page_size: int,
    token_bits: int,
) -> tuple[TextTablePage, ...]:
    pages = []
    for _, group_records in iter_token_count_groups(records):
        for start in range(0, len(group_records), page_size):
            page_records = group_records[start:start + page_size]
            record_token_count = len(page_records[0]) if page_records else 0
            pages.append(TextTablePage(
                record_token_count=record_token_count,
                page_record_count=len(page_records),
                record_stream=write_record_stream(page_records, token_bits),
            ))
    return tuple(pages)


def iter_token_count_groups(
    records: tuple[tuple[int, ...], ...],
) -> list[tuple[int, tuple[tuple[int, ...], ...]]]:
    groups: dict[int, list[tuple[int, ...]]] = {}
    for record in records:
        groups.setdefault(len(record), []).append(record)
    return [
        (record_token_count, tuple(groups[record_token_count]))
        for record_token_count in sorted(groups)
    ]


def write_page(writer: BytesWriter, page: TextTablePage) -> None:
    writer.writeByte(page.page_header)
    writer.writeMbUInt(page.record_token_count)
    writer.writeMbUInt(page.page_record_count)
    writer.writeMbUInt(len(page.record_stream))
    writer.writeBytes(page.record_stream)


def read_page(reader: BytesBufferReader) -> TextTablePage:
    page_header = reader.readByte()
    if page_header != 0:
        raise ValueError("unsupported TT00 PageHeader")
    record_token_count = reader.readMbUInt()
    page_record_count = reader.readMbUInt()
    record_stream_size = reader.readMbUInt()
    record_stream = reader.readAsBytes(record_stream_size)
    return TextTablePage(
        record_token_count=record_token_count,
        page_record_count=page_record_count,
        record_stream=record_stream,
        page_header=page_header,
    )


def decode_page_record(
    page: TextTablePage,
    index_in_page: int,
    token_bits: int,
    tokens: tuple[bytes, ...],
) -> bytes:
    return decode_page_record_with_token_getter(
        page,
        index_in_page,
        token_bits,
        lambda token_id: tokens[token_id],
    )


def decode_page_record_with_token_getter(
    page: TextTablePage,
    index_in_page: int,
    token_bits: int,
    token_getter,
) -> bytes:
    if not 0 <= index_in_page < page.page_record_count:
        raise IndexError("TT00 page record index out of range")
    records = decode_record_stream_with_token_getter(
        page.record_stream,
        page.page_record_count,
        token_bits,
        token_getter,
    )
    return records[index_in_page]


def decode_page_records_as_token_ids(
    page: TextTablePage,
    token_bits: int,
) -> list[tuple[int, ...]]:
    return decode_record_stream_as_token_ids(
        page.record_stream,
        page.page_record_count,
        token_bits,
    )
