from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence

from ...io import ReaderFactory
from ..chunk.TextTableChunkReader import TextTableChunkReader
from ..chunk.TokenMapChunkReader import TokenMapChunkReader
from .WordBookModel import required_token_bits


@dataclass(frozen=True)
class ChunkLocation:
    name: bytes
    data_start: int
    size: int

    @property
    def end(self) -> int:
        return self.data_start + self.size


def read_chunk_layout(
    reader_factory: ReaderFactory,
    source_size: int,
    expected_names: Sequence[bytes],
) -> tuple[ChunkLocation, ...]:
    if source_size < 0:
        raise ValueError("source_size must not be negative")
    chunks: list[ChunkLocation] = []
    with reader_factory.create() as reader:
        for expected_name in expected_names:
            name = reader.readAsBytes(4)
            size = reader.readMbUInt()
            if name != expected_name:
                raise ValueError(
                    f"WordBook expected {expected_name.decode('ascii')} chunk, got {name!r}"
                )
            chunk = ChunkLocation(name=name, data_start=reader.pos, size=size)
            if chunk.end > source_size:
                raise ValueError("chunk data exceeds source size")
            chunks.append(chunk)
            reader.skipInByte(size)
        if reader.pos != source_size:
            raise ValueError("WordBook has trailing bytes")
    return tuple(chunks)


class WordBookTextReader:
    """Shared TM00/TT00 access with bounded token caching and no page index."""

    def __init__(
        self,
        reader_factory: ReaderFactory,
        token_chunk: ChunkLocation,
        text_chunk: ChunkLocation,
        token_cache_size: int,
    ) -> None:
        if token_cache_size < 0:
            raise ValueError("token_cache_size must not be negative")
        self._reader_factory = reader_factory
        self._token_chunk = token_chunk
        self._text_chunk = text_chunk
        self._token_cache_size = token_cache_size
        self._token_cache: OrderedDict[int, bytes] | None = (
            OrderedDict() if token_cache_size > 0 else None
        )

        with reader_factory.create(token_chunk.data_start) as reader:
            token_reader = TokenMapChunkReader(reader)
            self.token_count = token_reader.token_count
        with reader_factory.create(text_chunk.data_start) as reader:
            text_reader = TextTableChunkReader(reader)
            self.record_count = text_reader.record_count
            self.token_bits = text_reader.token_bits
        if self.token_bits < required_token_bits(self.token_count):
            raise ValueError("TT00 token_bits is smaller than TM00 token table requires")

    def readBytes(self, code: int) -> bytes:
        return self.readByteSets((code,))[code]

    def readByteSets(self, codes: Sequence[int]) -> dict[int, bytes]:
        unique_codes = tuple(sorted(set(codes)))
        if not unique_codes:
            return {}
        with self._reader_factory.create(self._text_chunk.data_start) as reader:
            token_id_sets = TextTableChunkReader(reader).readTokenIdSets(unique_codes)

        token_ids = sorted({
            token_id
            for record in token_id_sets.values()
            for token_id in record
        })
        resolved: dict[int, bytes] = {}
        missing: list[int] = []
        cache = self._token_cache
        for token_id in token_ids:
            if cache is not None and token_id in cache:
                resolved[token_id] = cache[token_id]
            else:
                missing.append(token_id)
        if missing:
            with self._reader_factory.create(self._token_chunk.data_start) as reader:
                resolved.update(
                    TokenMapChunkReader(reader).readTokens(missing)
                )

        results: dict[int, bytes] = {}
        for code in unique_codes:
            result = bytearray()
            for token_id in token_id_sets[code]:
                token = resolved[token_id]
                result.extend(token)
                self._rememberToken(token_id, token)
            results[code] = bytes(result)
        return results

    def _rememberToken(self, token_id: int, token: bytes) -> None:
        cache = self._token_cache
        if cache is None:
            return
        cache[token_id] = token
        cache.move_to_end(token_id)
        while len(cache) > self._token_cache_size:
            cache.popitem(last=False)


def iter_index_batches(
    indices: Iterable[int],
    run_buffer_limit: int,
) -> Iterator[list[int]]:
    run: list[int] = []
    previous: int | None = None
    for index in indices:
        if previous is not None and index < previous:
            yield run
            run = []
        if run_buffer_limit > 0 and len(run) >= run_buffer_limit:
            yield run
            run = []
        run.append(index)
        previous = index
    if run:
        yield run
