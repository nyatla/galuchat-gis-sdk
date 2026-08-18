from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field

from ...io import BytesBufferReader


@dataclass(frozen=True)
class MappedTokenMapPage:
    token_base: int
    token_byte_size: int
    page_token_count: int
    token_stream_start: int
    token_stream_size: int


@dataclass
class TokenMapChunkReader:
    data: bytes
    token_count: int
    pages: tuple[MappedTokenMapPage, ...]
    cache_size: int = 64
    _cache: OrderedDict[int, bytes] = field(default_factory=OrderedDict)

    def get(self, token_id: int) -> bytes:
        if not 0 <= token_id < self.token_count:
            raise IndexError("TM00 token id out of range")
        cached = self._cache.get(token_id)
        if cached is not None:
            self._cache.move_to_end(token_id)
            return cached
        page = self.find_page(token_id)
        index_in_page = token_id - page.token_base
        start = page.token_stream_start + index_in_page * page.token_byte_size
        end = start + page.token_byte_size
        token = self.data[start:end]
        if len(token) != page.token_byte_size:
            raise ValueError("TM00 token stream truncated")
        if self.cache_size > 0:
            self._cache[token_id] = token
            self._cache.move_to_end(token_id)
            while len(self._cache) > self.cache_size:
                self._cache.popitem(last=False)
        return token

    def find_page(self, token_id: int) -> MappedTokenMapPage:
        for page in self.pages:
            if token_id < page.token_base + page.page_token_count:
                return page
        raise IndexError("TM00 token id out of range")

    @classmethod
    def unpack(cls, src: bytes, offset: int, size: int, cache_size: int = 64) -> "TokenMapChunkReader":
        reader = BytesBufferReader(src, offset=offset)
        token_count = reader.readMbUInt()
        token_page_count = reader.readMbUInt()
        pages = []
        token_base = 0
        previous_token_byte_size = -1
        for _ in range(token_page_count):
            page_header = reader.readByte()
            if page_header != 0:
                raise ValueError("unsupported TM00 PageHeader")
            token_byte_size = reader.readMbUInt()
            page_token_count = reader.readMbUInt()
            token_stream_size = reader.readMbUInt()
            if token_byte_size < previous_token_byte_size:
                raise ValueError("TM00 token pages must be sorted by token_byte_size")
            previous_token_byte_size = token_byte_size
            if token_byte_size == 0:
                raise ValueError("TM00 token_byte_size must be positive")
            if page_token_count == 0:
                raise ValueError("TM00 page_token_count must be positive")
            if token_stream_size != token_byte_size * page_token_count:
                raise ValueError("TM00 token stream size mismatch")
            token_stream_start = offset + reader.pos
            reader.skipInByte(token_stream_size)
            pages.append(MappedTokenMapPage(
                token_base=token_base,
                token_byte_size=token_byte_size,
                page_token_count=page_token_count,
                token_stream_start=token_stream_start,
                token_stream_size=token_stream_size,
            ))
            token_base += page_token_count
        if token_base != token_count:
            raise ValueError("TM00 token count mismatch")
        if reader.pos != size:
            raise ValueError("TM00 has trailing bytes")
        return cls(
            data=src,
            token_count=token_count,
            pages=tuple(pages),
            cache_size=cache_size,
        )


MappedTokenMap = TokenMapChunkReader


def parse_mapped_tm00_data(
    src: bytes,
    offset: int,
    size: int,
    cache_size: int = 64,
) -> TokenMapChunkReader:
    return TokenMapChunkReader.unpack(src, offset, size, cache_size=cache_size)
