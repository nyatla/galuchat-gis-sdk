from __future__ import annotations

from dataclasses import dataclass

from ...io import BytesBufferReader, BytesWriter


@dataclass(frozen=True)
class TokenMapChunk:
    tokens: tuple[bytes, ...]


@dataclass(frozen=True)
class TokenMapPage:
    token_byte_size: int
    page_token_count: int
    token_stream: bytes
    page_header: int = 0


def write_tm00_data(token_map: TokenMapChunk) -> bytes:
    writer = BytesWriter()
    writer.writeMbUInt(len(token_map.tokens))
    token_pages = build_token_pages(token_map.tokens)
    writer.writeMbUInt(len(token_pages))
    for page in token_pages:
        write_token_page(writer, page)
    return bytes(writer.buffer)


def parse_tm00_data(data: bytes) -> TokenMapChunk:
    reader = BytesBufferReader(data)
    token_count = reader.readMbUInt()
    token_page_count = reader.readMbUInt()
    tokens = []
    previous_token_byte_size = -1
    for _ in range(token_page_count):
        page = read_token_page(reader)
        if page.token_byte_size < previous_token_byte_size:
            raise ValueError("TM00 token pages must be sorted by token_byte_size")
        previous_token_byte_size = page.token_byte_size
        if page.token_byte_size == 0:
            raise ValueError("TM00 token_byte_size must be positive")
        if page.page_token_count == 0:
            raise ValueError("TM00 page_token_count must be positive")
        if len(page.token_stream) != page.token_byte_size * page.page_token_count:
            raise ValueError("TM00 token stream size mismatch")
        for index in range(page.page_token_count):
            start = index * page.token_byte_size
            end = start + page.token_byte_size
            tokens.append(page.token_stream[start:end])
    if len(tokens) != token_count:
        raise ValueError("TM00 token count mismatch")
    if reader.pos != len(data):
        raise ValueError("TM00 has trailing bytes")
    return TokenMapChunk(tokens=tuple(tokens))


def build_token_pages(tokens: tuple[bytes, ...]) -> tuple[TokenMapPage, ...]:
    pages = []
    current_token_byte_size = -1
    current_tokens = []
    for token in tokens:
        token_byte_size = len(token)
        if token_byte_size == 0:
            raise ValueError("TM00 token must not be empty")
        if token_byte_size < current_token_byte_size:
            raise ValueError("TM00 tokens must be sorted by byte size")
        if current_tokens and token_byte_size != current_token_byte_size:
            pages.append(make_token_page(current_token_byte_size, current_tokens))
            current_tokens = []
        current_token_byte_size = token_byte_size
        current_tokens.append(token)
    if current_tokens:
        pages.append(make_token_page(current_token_byte_size, current_tokens))
    return tuple(pages)


def make_token_page(token_byte_size: int, tokens: list[bytes]) -> TokenMapPage:
    return TokenMapPage(
        token_byte_size=token_byte_size,
        page_token_count=len(tokens),
        token_stream=b"".join(tokens),
    )


def write_token_page(writer: BytesWriter, page: TokenMapPage) -> None:
    if len(page.token_stream) != page.token_byte_size * page.page_token_count:
        raise ValueError("TM00 token stream size mismatch")
    writer.writeByte(page.page_header)
    writer.writeMbUInt(page.token_byte_size)
    writer.writeMbUInt(page.page_token_count)
    writer.writeMbUInt(len(page.token_stream))
    writer.writeBytes(page.token_stream)


def read_token_page(reader: BytesBufferReader) -> TokenMapPage:
    page_header = reader.readByte()
    if page_header != 0:
        raise ValueError("unsupported TM00 PageHeader")
    token_byte_size = reader.readMbUInt()
    page_token_count = reader.readMbUInt()
    token_stream_size = reader.readMbUInt()
    token_stream = reader.readAsBytes(token_stream_size)
    return TokenMapPage(
        token_byte_size=token_byte_size,
        page_token_count=page_token_count,
        token_stream=token_stream,
        page_header=page_header,
    )
