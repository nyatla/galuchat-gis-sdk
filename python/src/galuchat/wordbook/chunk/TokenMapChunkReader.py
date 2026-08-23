from __future__ import annotations

from collections.abc import Sequence

from ...io import ABytesReader


class TokenMapChunkReader:
    """One-shot sequential reader for a TM00 chunk body."""

    def __init__(self, reader: ABytesReader):
        self._reader = reader
        self.token_count = reader.readMbUInt()
        self.page_count = reader.readMbUInt()
        self._used = False

    def get(self, token_id: int) -> bytes:
        return self.readTokens((token_id,))[token_id]

    def readTokens(self, token_ids: Sequence[int]) -> dict[int, bytes]:
        """Read strictly increasing token ids in one forward pass."""
        self._begin_operation()
        if not token_ids:
            return {}
        previous = -1
        for token_id in token_ids:
            if not 0 <= token_id < self.token_count:
                raise IndexError("TM00 token id out of range")
            if token_id <= previous:
                raise ValueError("TM00 token ids must be strictly increasing")
            previous = token_id

        results: dict[int, bytes] = {}
        target_pos = 0
        token_base = 0
        previous_token_byte_size = -1
        for _ in range(self.page_count):
            page_header = self._reader.readByte()
            if page_header != 0:
                raise ValueError("unsupported TM00 PageHeader")
            token_byte_size = self._reader.readMbUInt()
            page_token_count = self._reader.readMbUInt()
            token_stream_size = self._reader.readMbUInt()
            self._validatePageHeader(
                token_byte_size,
                page_token_count,
                token_stream_size,
                previous_token_byte_size,
            )
            previous_token_byte_size = token_byte_size
            page_end = token_base + page_token_count
            consumed = 0
            while target_pos < len(token_ids) and token_ids[target_pos] < page_end:
                token_id = token_ids[target_pos]
                if token_id < token_base:
                    raise IndexError("TM00 token id out of range")
                token_offset = (token_id - token_base) * token_byte_size
                self._reader.skipInByte(token_offset - consumed)
                results[token_id] = self._reader.readAsBytes(token_byte_size)
                consumed = token_offset + token_byte_size
                target_pos += 1
            if target_pos == len(token_ids):
                return results
            self._reader.skipInByte(token_stream_size - consumed)
            token_base = page_end
        raise IndexError("TM00 token id out of range")

    def _begin_operation(self) -> None:
        if self._used:
            raise RuntimeError("TokenMapChunkReader supports one operation")
        self._used = True

    @staticmethod
    def _validatePageHeader(
        token_byte_size: int,
        page_token_count: int,
        token_stream_size: int,
        previous_token_byte_size: int,
    ) -> None:
        if token_byte_size < previous_token_byte_size:
            raise ValueError("TM00 token pages must be sorted by token_byte_size")
        if token_byte_size == 0:
            raise ValueError("TM00 token_byte_size must be positive")
        if page_token_count == 0:
            raise ValueError("TM00 page_token_count must be positive")
        if token_stream_size != token_byte_size * page_token_count:
            raise ValueError("TM00 token stream size mismatch")
