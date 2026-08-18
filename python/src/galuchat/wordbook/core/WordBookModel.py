from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .constants import DEFAULT_PAGE_SIZE


def required_token_bits(token_count: int) -> int:
    if token_count < 0:
        raise ValueError("token_count must not be negative")
    if token_count > (1 << 16):
        raise ValueError("token_count exceeds 16 bit token id capacity")
    if token_count <= 1:
        return 1
    return (token_count - 1).bit_length()


@dataclass(frozen=True)
class WordBookModel:
    page_size: int
    tokens: tuple[bytes, ...]
    records: tuple[tuple[int, ...], ...]

    @classmethod
    def from_texts(
        cls,
        texts: Iterable[str],
        page_size: int = DEFAULT_PAGE_SIZE,
        encoding: str = "utf-8",
    ) -> "WordBookModel":
        token_encoding = normalize_text_token_encoding(encoding)
        sequences = [tuple(ch.encode(token_encoding) for ch in text) for text in texts]
        return cls.from_token_sequences(sequences, page_size=page_size)

    @classmethod
    def from_items(
        cls,
        items: Iterable[tuple[int, str]],
        page_size: int = DEFAULT_PAGE_SIZE,
        encoding: str = "utf-8",
    ) -> "WordBookModel":
        return cls.from_texts(
            (text for _, text in items),
            page_size=page_size,
            encoding=encoding,
        )

    @classmethod
    def from_token_text_sequences(
        cls,
        sequences: Iterable[Iterable[str]],
        page_size: int = DEFAULT_PAGE_SIZE,
        encoding: str = "utf-8",
    ) -> "WordBookModel":
        token_encoding = normalize_text_token_encoding(encoding)
        return cls.from_token_sequences(
            (
                tuple(token.encode(token_encoding) for token in sequence)
                for sequence in sequences
            ),
            page_size=page_size,
        )

    @classmethod
    def from_token_sequences(
        cls,
        sequences: Iterable[tuple[bytes, ...]],
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> "WordBookModel":
        if page_size <= 0:
            raise ValueError("page_size must be positive")
        rows = list(sequences)
        if not rows:
            raise ValueError("WordBook requires at least one record")
        tokens, token_to_id = build_token_table(rows)
        records = tuple(
            tuple(token_to_id[token] for token in sequence)
            for sequence in rows
        )
        return cls(page_size=page_size, tokens=tokens, records=records)

    @property
    def record_count(self) -> int:
        return len(self.records)

    @property
    def page_count(self) -> int:
        record_counts = Counter(len(record) for record in self.records)
        return sum(
            (count + self.page_size - 1) // self.page_size
            for count in record_counts.values()
        )

    def to_token_sequences(self) -> list[tuple[bytes, ...]]:
        return [
            tuple(self.tokens[token_id] for token_id in record)
            for record in self.records
        ]

    def rebuild_from_token_sequences(
        self,
        sequences: Iterable[tuple[bytes, ...]],
    ) -> "WordBookModel":
        return self.from_token_sequences(sequences, page_size=self.page_size)


def build_token_table(sequences: list[tuple[bytes, ...]]) -> tuple[tuple[bytes, ...], dict[bytes, int]]:
    counts = Counter(token for sequence in sequences for token in sequence)
    tokens = tuple(
        token
        for token, _ in sorted(counts.items(), key=lambda item: (len(item[0]), -item[1], item[0]))
    )
    return tokens, {token: index for index, token in enumerate(tokens)}


def normalize_text_token_encoding(encoding: str) -> str:
    normalized = encoding.lower().replace("_", "-")
    if normalized in ("utf8", "utf-8"):
        return "utf-8"
    if normalized in ("sjis", "shift-jis", "shift-jisx0213", "cp932", "ms932"):
        return "cp932"
    if normalized in ("utf16", "utf-16", "utf-16le", "utf-16-le"):
        return "utf-16-le"
    return encoding
