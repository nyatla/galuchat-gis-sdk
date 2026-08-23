from __future__ import annotations

from collections.abc import Sequence

from ...io import ABytesReader
from .record_stream import decode_record_stream_reader_targets_as_token_ids


class TextTableChunkReader:
    """One-shot sequential reader for a TT00 chunk body."""

    def __init__(self, reader: ABytesReader):
        self._reader = reader
        self.record_count = reader.readMbUInt()
        reader.readMbUInt()  # pack時のページ分割単位。読出しには不要。
        self.page_count = reader.readMbUInt()
        self.token_bits = reader.readMbUInt()
        if not 1 <= self.token_bits <= 16:
            raise ValueError("invalid TT00 token_bits")
        self._used = False

    def readTokenIds(self, code: int) -> tuple[int, ...]:
        return self.readTokenIdSets((code,))[code]

    def readTokenIdSets(self, codes: Sequence[int]) -> dict[int, tuple[int, ...]]:
        """Read strictly increasing record codes in one forward pass."""
        self._begin_operation()
        if not codes:
            return {}
        previous = -1
        for code in codes:
            if not 0 <= code < self.record_count:
                raise KeyError(code)
            if code <= previous:
                raise ValueError("TT00 record codes must be strictly increasing")
            previous = code

        results: dict[int, tuple[int, ...]] = {}
        target_pos = 0
        record_base = 0
        previous_token_count = -1
        for _ in range(self.page_count):
            page_header = self._reader.readByte()
            if page_header != 0:
                raise ValueError("unsupported TT00 PageHeader")
            record_token_count = self._reader.readMbUInt()
            page_record_count = self._reader.readMbUInt()
            record_stream_size = self._reader.readMbUInt()
            self._validatePageHeader(
                record_token_count,
                page_record_count,
                previous_token_count,
            )
            previous_token_count = record_token_count
            page_end = record_base + page_record_count
            page_target_start = target_pos
            while target_pos < len(codes) and codes[target_pos] < page_end:
                target_pos += 1
            if page_target_start == target_pos:
                self._reader.skipInByte(record_stream_size)
                record_base = page_end
                continue

            local_targets = tuple(
                code - record_base
                for code in codes[page_target_start:target_pos]
            )
            stream_start = self._reader.pos
            page_results = decode_record_stream_reader_targets_as_token_ids(
                self._reader,
                page_record_count,
                local_targets,
                self.token_bits,
            )
            if self._reader.pos - stream_start > record_stream_size:
                raise ValueError("TT00 RecordStream overread")
            for local_code, token_ids in page_results.items():
                if len(token_ids) != record_token_count:
                    raise ValueError("TT00 record token count mismatch")
                results[record_base + local_code] = token_ids
            if target_pos == len(codes):
                return results
            self._reader.skipBits(
                record_stream_size * 8
                - ((self._reader.pos - stream_start) * 8 - self._reader.bitOffset)
            )
            record_base = page_end
        raise KeyError(codes[target_pos])

    def _begin_operation(self) -> None:
        if self._used:
            raise RuntimeError("TextTableChunkReader supports one operation")
        self._used = True

    @staticmethod
    def _validatePageHeader(
        record_token_count: int,
        page_record_count: int,
        previous_token_count: int,
    ) -> None:
        if record_token_count < previous_token_count:
            raise ValueError("TT00 pages must be sorted by record_token_count")
        if page_record_count == 0:
            raise ValueError("TT00 page_record_count must be positive")
