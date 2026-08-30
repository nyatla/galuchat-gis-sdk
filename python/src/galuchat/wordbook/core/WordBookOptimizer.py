from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass

from ...io.MBIntDef import MBIntDef
from .constants import PALETTE_SIZE
from .WordBookModel import WordBookModel, required_token_bits


@dataclass(frozen=True)
class TokenMergeRecord:
    merge_index: int
    left: str
    right: str
    merged: str
    count: int
    estimated_gain_bits: int
    token_count: int
    before_bytes: int = 0
    after_bytes: int = 0


@dataclass
class WordBookOptimizer:
    max_merge: int = 1000
    min_gain_bits: int = 1
    max_token_bytes: int = 32
    candidate_limit: int = 64
    token_bits: int | None = None
    size_priority: bool = False
    size_candidate_limit: int = 8
    page_order_strategy: str = "cluster"

    def optimizeTokens(
        self,
        model: WordBookModel,
        report: list[TokenMergeRecord] | None = None,
    ) -> WordBookModel:
        sequences = model.to_token_sequences()
        current_size = self.estimateModelSize(model) if self.size_priority else 0
        for merge_index in range(1, self.max_merge + 1):
            if self.size_priority:
                candidate = _select_size_priority_merge(
                    model,
                    sequences,
                    current_size=current_size,
                    token_bits=self.token_bits,
                    min_gain_bits=self.min_gain_bits,
                    max_token_bytes=self.max_token_bytes,
                    candidate_limit=self.candidate_limit,
                    size_candidate_limit=self.size_candidate_limit,
                )
            else:
                candidate = _select_merge_candidate(
                    sequences,
                    min_gain_bits=self.min_gain_bits,
                    max_token_bytes=self.max_token_bytes,
                    candidate_limit=self.candidate_limit,
                )
            if candidate is None:
                break
            left, right, merged, count, gain_bits, before_bytes, after_bytes = candidate
            sequences = _merge_pair(sequences, (left, right), merged)
            next_model = model.rebuild_from_token_sequences(sequences)
            if report is not None:
                report.append(TokenMergeRecord(
                    merge_index=merge_index,
                    left=_display_token(left),
                    right=_display_token(right),
                    merged=_display_token(merged),
                    count=count,
                    estimated_gain_bits=gain_bits,
                    token_count=len(next_model.tokens),
                    before_bytes=before_bytes,
                    after_bytes=after_bytes,
                ))
            model = next_model
            if self.size_priority:
                current_size = after_bytes
        return model

    def optimizePageOrder(
        self,
        model: WordBookModel,
        strategy: str | None = None,
    ) -> WordBookModel:
        page_order_strategy = strategy if strategy is not None else self.page_order_strategy
        order = grouped_page_order(model.records, page_order_strategy)
        return WordBookModel(
            page_size=model.page_size,
            tokens=model.tokens,
            records=tuple(model.records[index] for index in order),
        )

    def estimateModelSize(
        self,
        model: WordBookModel,
        token_bits: int | None = None,
    ) -> int:
        return _estimate_model_size(
            model,
            self.token_bits if token_bits is None else token_bits,
        )

def _select_merge_candidate(
    sequences: list[tuple[bytes, ...]],
    min_gain_bits: int,
    max_token_bytes: int,
    candidate_limit: int,
) -> tuple[bytes, bytes, bytes, int, int, int, int] | None:
    transition_counts = _transition_counts(sequences)
    if not transition_counts:
        return None
    best = None
    for (left, right), count in transition_counts.most_common(candidate_limit):
        merged = left + right
        if len(merged) > max_token_bytes:
            continue
        gain_bits = _estimate_merge_gain_bits(count, merged)
        if gain_bits < min_gain_bits:
            continue
        candidate = (left, right, merged, count, gain_bits, 0, 0)
        if best is None or _candidate_key(candidate) > _candidate_key(best):
            best = candidate
    return best


def _select_size_priority_merge(
    model: WordBookModel,
    sequences: list[tuple[bytes, ...]],
    current_size: int,
    token_bits: int | None,
    min_gain_bits: int,
    max_token_bytes: int,
    candidate_limit: int,
    size_candidate_limit: int,
) -> tuple[bytes, bytes, bytes, int, int, int, int] | None:
    transition_counts = _transition_counts(sequences)
    rough_candidates: list[tuple[bytes, bytes, bytes, int, int]] = []
    for (left, right), count in transition_counts.most_common(candidate_limit):
        merged = left + right
        if len(merged) > max_token_bytes:
            continue
        gain_bits = _estimate_merge_gain_bits(count, merged)
        if gain_bits < min_gain_bits:
            continue
        rough_candidates.append((left, right, merged, count, gain_bits))
    rough_candidates.sort(key=lambda item: (item[4], item[3], item[0], item[1]), reverse=True)

    best = None
    for left, right, merged, count, gain_bits in rough_candidates[:size_candidate_limit]:
        merged_sequences = _merge_pair(sequences, (left, right), merged)
        next_model = model.rebuild_from_token_sequences(merged_sequences)
        next_size = _estimate_model_size(next_model, token_bits)
        actual_gain_bits = (current_size - next_size) * 8
        if actual_gain_bits < min_gain_bits:
            continue
        candidate = (left, right, merged, count, actual_gain_bits, current_size, next_size)
        if best is None or candidate[6] < best[6]:
            best = candidate
    return best


def _candidate_key(candidate: tuple[bytes, bytes, bytes, int, int, int, int]) -> tuple[int, int, bytes, bytes]:
    left, right, _, count, gain_bits, _, _ = candidate
    return (gain_bits, count, left, right)


def _estimate_merge_gain_bits(count: int, merged: bytes) -> int:
    token_payload_gain = count * 4
    token_table_cost = (MBIntDef.sizeOfMbUint(len(merged)) + len(merged)) * 8
    return token_payload_gain - token_table_cost


def _estimate_model_size(model: WordBookModel, token_bits: int | None = None) -> int:
    actual_token_bits = _resolve_token_bits(model, token_bits)
    nm00_data_size = 16 + 1
    tm00_data_size = _estimate_tm00_data_size(model.tokens)
    tt00_data_size = _estimate_tt00_data_size(model.records, model.page_size, actual_token_bits)
    return (
        _chunk_size(nm00_data_size)
        + _chunk_size(tm00_data_size)
        + _chunk_size(tt00_data_size)
    )


def _resolve_token_bits(model: WordBookModel, token_bits: int | None) -> int:
    required_bits = required_token_bits(len(model.tokens))
    if token_bits is None:
        return required_bits
    if token_bits < required_bits:
        raise ValueError("token_bits is smaller than token table requires")
    if token_bits > 16:
        raise ValueError("token_bits must be in 1..16")
    return token_bits


def _chunk_size(data_size: int) -> int:
    return 4 + MBIntDef.sizeOfMbUint(data_size) + data_size


def _estimate_tm00_data_size(tokens: tuple[bytes, ...]) -> int:
    return (
        MBIntDef.sizeOfMbUint(len(tokens))
        + MBIntDef.sizeOfMbUint(_token_page_count(tokens))
        + sum(_estimate_token_page_size(token_byte_size, page_token_count) for token_byte_size, page_token_count in _token_pages(tokens))
    )


def _token_pages(tokens: tuple[bytes, ...]) -> list[tuple[int, int]]:
    pages: list[tuple[int, int]] = []
    current_token_byte_size = -1
    current_count = 0
    for token in tokens:
        token_byte_size = len(token)
        if current_count > 0 and token_byte_size != current_token_byte_size:
            pages.append((current_token_byte_size, current_count))
            current_count = 0
        current_token_byte_size = token_byte_size
        current_count += 1
    if current_count > 0:
        pages.append((current_token_byte_size, current_count))
    return pages


def _token_page_count(tokens: tuple[bytes, ...]) -> int:
    return len(_token_pages(tokens))


def _estimate_token_page_size(token_byte_size: int, page_token_count: int) -> int:
    token_stream_size = token_byte_size * page_token_count
    return (
        1
        + MBIntDef.sizeOfMbUint(token_byte_size)
        + MBIntDef.sizeOfMbUint(page_token_count)
        + MBIntDef.sizeOfMbUint(token_stream_size)
        + token_stream_size
    )


def _estimate_tt00_data_size(
    records: tuple[tuple[int, ...], ...],
    page_size: int,
    token_bits: int,
) -> int:
    page_sizes = []
    for _, group_records in _iter_token_count_groups(records):
        page_sizes.extend(
            _estimate_page_size(group_records[start:start + page_size], token_bits)
            for start in range(0, len(group_records), page_size)
        )
    return (
        MBIntDef.sizeOfMbUint(len(records))
        + MBIntDef.sizeOfMbUint(page_size)
        + MBIntDef.sizeOfMbUint(len(page_sizes))
        + MBIntDef.sizeOfMbUint(token_bits)
        + sum(page_sizes)
    )


def _estimate_page_size(records: tuple[tuple[int, ...], ...], token_bits: int) -> int:
    record_stream_size = _estimate_record_stream_size(records, token_bits)
    record_token_count = len(records[0]) if records else 0
    return (
        1
        + MBIntDef.sizeOfMbUint(record_token_count)
        + MBIntDef.sizeOfMbUint(len(records))
        + MBIntDef.sizeOfMbUint(record_stream_size)
        + record_stream_size
    )


def _estimate_record_stream_size(records: tuple[tuple[int, ...], ...], token_bits: int) -> int:
    packet_value_bits: list[int] = []
    palette: list[int | None] = [None] * (PALETTE_SIZE + 1)
    base_tokens = _select_base_palette(records)
    for slot, token in enumerate(base_tokens, start=1):
        palette[slot] = token
    packet_value_bits.append(15 + len(base_tokens) * token_bits)
    stream = _flatten_records(records)
    future_positions = _build_future_positions(stream)

    local_code_count = 0

    def flush_payload() -> None:
        nonlocal local_code_count
        if local_code_count:
            packet_value_bits.append(local_code_count * 4)
            local_code_count = 0

    for position, token in enumerate(stream):
        if token is None:
            local_code_count += 1
            continue
        _consume_current_position(future_positions[token], position)
        try:
            palette.index(token)
        except ValueError:
            flush_payload()
            slot = _select_update_slot(palette, future_positions)
            palette[slot] = token
            packet_value_bits.append(4 + token_bits)
        local_code_count += 1
    flush_payload()

    bit_size = MBIntDef.sizeOfMbUint(len(packet_value_bits)) * 8
    for value_bits in packet_value_bits:
        bit_size += 2 + MBIntDef.sizeOfMbUint(value_bits) * 8 + value_bits
    return (bit_size + 7) // 8


def _select_base_palette(records: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    tokens = []
    seen = set()
    for record in records:
        for token in record:
            if token in seen:
                continue
            seen.add(token)
            tokens.append(token)
            if len(tokens) == PALETTE_SIZE:
                return tuple(tokens)
    return tuple(tokens)


def _flatten_records(records: tuple[tuple[int, ...], ...]) -> list[int | None]:
    stream: list[int | None] = []
    for record in records:
        stream.extend(record)
        stream.append(None)
    return stream


def _build_future_positions(stream: list[int | None]) -> defaultdict[int, deque[int]]:
    future_positions: defaultdict[int, deque[int]] = defaultdict(deque)
    for position, token in enumerate(stream):
        if token is not None:
            future_positions[token].append(position)
    return future_positions


def _consume_current_position(positions: deque[int], position: int) -> None:
    if positions and positions[0] == position:
        positions.popleft()


def _select_update_slot(
    palette: list[int | None],
    future_positions: defaultdict[int, deque[int]],
) -> int:
    for slot in range(1, PALETTE_SIZE + 1):
        if palette[slot] is None:
            return slot
    return max(
        range(1, PALETTE_SIZE + 1),
        key=lambda slot: (
            _next_position(palette[slot], future_positions),
            palette[slot] if palette[slot] is not None else -1,
        ),
    )


def _next_position(
    token: int | None,
    future_positions: defaultdict[int, deque[int]],
) -> int:
    if token is None:
        return 10**18
    positions = future_positions[token]
    return positions[0] if positions else 10**18


def _transition_counts(sequences: list[tuple[bytes, ...]]) -> Counter[tuple[bytes, bytes]]:
    counts: Counter[tuple[bytes, bytes]] = Counter()
    for sequence in sequences:
        counts.update(zip(sequence, sequence[1:]))
    return counts


def _merge_pair(
    sequences: list[tuple[bytes, ...]],
    pair: tuple[bytes, bytes],
    merged_token: bytes,
) -> list[tuple[bytes, ...]]:
    merged_sequences = []
    for sequence in sequences:
        row = []
        index = 0
        while index < len(sequence):
            if (
                index + 1 < len(sequence)
                and sequence[index] == pair[0]
                and sequence[index + 1] == pair[1]
            ):
                row.append(merged_token)
                index += 2
            else:
                row.append(sequence[index])
                index += 1
        merged_sequences.append(tuple(row))
    return merged_sequences


def rare_key_order(records: tuple[tuple[int, ...], ...]) -> list[int]:
    sets = _record_sets(records)
    frequencies = _token_frequencies(records)

    def key(index: int) -> tuple[int, float, int]:
        tokens = sets[index]
        if not tokens:
            return (10**18, 0.0, index)
        representative_frequency = min(frequencies[token] for token in tokens)
        return (representative_frequency, -_rare_score(tokens, frequencies), index)

    return sorted(range(len(records)), key=key)


def grouped_page_order(records: tuple[tuple[int, ...], ...], strategy: str) -> list[int]:
    order = []
    for _, group_indexes in _iter_token_count_index_groups(records):
        group_records = tuple(records[index] for index in group_indexes)
        if strategy == "current":
            local_order = list(range(len(group_records)))
        elif strategy == "rare":
            local_order = rare_key_order(group_records)
        elif strategy == "cluster":
            local_order = rare_cluster_order(group_records)
        else:
            raise ValueError(f"unsupported page order strategy: {strategy}")
        order.extend(group_indexes[index] for index in local_order)
    return order


def _iter_token_count_groups(
    records: tuple[tuple[int, ...], ...],
) -> list[tuple[int, tuple[tuple[int, ...], ...]]]:
    groups: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for record in records:
        groups[len(record)].append(record)
    return [
        (record_token_count, tuple(groups[record_token_count]))
        for record_token_count in sorted(groups)
    ]


def _iter_token_count_index_groups(
    records: tuple[tuple[int, ...], ...],
) -> list[tuple[int, list[int]]]:
    groups: dict[int, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        groups[len(record)].append(index)
    return [
        (record_token_count, groups[record_token_count])
        for record_token_count in sorted(groups)
    ]


def rare_cluster_order(records: tuple[tuple[int, ...], ...]) -> list[int]:
    sets = _record_sets(records)
    frequencies = _token_frequencies(records)
    clusters: dict[int, list[int]] = defaultdict(list)
    empty_records = []
    for index, tokens in enumerate(sets):
        if not tokens:
            empty_records.append(index)
            continue
        representative = min(tokens, key=lambda token: (frequencies[token], token))
        clusters[representative].append(index)

    def record_signature(index: int) -> tuple[tuple[int, ...], int, int]:
        rare_tokens = tuple(sorted(
            sets[index],
            key=lambda token: (frequencies[token], token),
        )[:6])
        return (rare_tokens, -len(sets[index]), index)

    ordered_clusters = sorted(
        clusters.items(),
        key=lambda item: (
            frequencies[item[0]],
            -len(item[1]),
            item[0],
        ),
    )
    order = []
    for _, cluster_records in ordered_clusters:
        order.extend(sorted(cluster_records, key=record_signature))
    order.extend(empty_records)
    return order


def _record_sets(records: tuple[tuple[int, ...], ...]) -> list[frozenset[int]]:
    return [frozenset(record) for record in records]


def _token_frequencies(records: tuple[tuple[int, ...], ...]) -> Counter[int]:
    return Counter(token for record in records for token in record)


def _rare_score(tokens: frozenset[int], frequencies: Counter[int]) -> float:
    return sum(1.0 / frequencies[token] for token in tokens)


def _display_token(token: bytes) -> str:
    try:
        return token.decode("utf-8")
    except UnicodeDecodeError:
        return token.hex()
