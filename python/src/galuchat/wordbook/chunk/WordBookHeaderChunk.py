from __future__ import annotations

from dataclasses import dataclass

from ...io import ABytesReader, BytesBufferReader, BytesWriter
from ..core.constants import GISWORDBOOK_VERSION, WORDBOOK_VERSION


@dataclass(frozen=True)
class WordBookHeaderChunk:
    metadata: str | None = None


def _write_header_data(header: WordBookHeaderChunk, version: bytes) -> bytes:
    writer = BytesWriter()
    writer.writeBytesAsBStr(version, 16)
    if header.metadata is None:
        writer.writeMbUInt(0)
    else:
        metadata = header.metadata.encode("utf-8")
        writer.writeMbUInt(len(metadata))
        writer.writeBytes(metadata)
    return bytes(writer.buffer)


def _read_header_data(
    reader: ABytesReader,
    size: int,
    expected_version: bytes,
    format_name: str,
) -> WordBookHeaderChunk:
    start = reader.pos
    version = reader.readBytesAsBStr(16)
    if version != expected_version:
        raise ValueError(f"invalid {format_name} version: {version!r}")
    metadata_size = reader.readMbUInt()
    metadata = None if metadata_size == 0 else reader.readAsBytes(metadata_size).decode("utf-8")
    if reader.pos - start != size:
        raise ValueError(f"{format_name} header has trailing bytes")
    return WordBookHeaderChunk(metadata=metadata)


def _parse_header_data(
    data: bytes,
    version: bytes,
    format_name: str,
) -> WordBookHeaderChunk:
    return _read_header_data(BytesBufferReader(data), len(data), version, format_name)


def write_nm00_data(header: WordBookHeaderChunk) -> bytes:
    return _write_header_data(header, WORDBOOK_VERSION)


def parse_nm00_data(data: bytes) -> WordBookHeaderChunk:
    return _parse_header_data(data, WORDBOOK_VERSION, "WordBook")


def read_nm00_data(reader: ABytesReader, size: int) -> WordBookHeaderChunk:
    return _read_header_data(reader, size, WORDBOOK_VERSION, "WordBook")


def write_gw00_data(header: WordBookHeaderChunk) -> bytes:
    return _write_header_data(header, GISWORDBOOK_VERSION)


def parse_gw00_data(data: bytes) -> WordBookHeaderChunk:
    return _parse_header_data(data, GISWORDBOOK_VERSION, "GisWordBook")


def read_gw00_data(reader: ABytesReader, size: int) -> WordBookHeaderChunk:
    return _read_header_data(reader, size, GISWORDBOOK_VERSION, "GisWordBook")
