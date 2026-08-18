from __future__ import annotations

from collections import defaultdict, deque
from typing import Callable

from ...io import BytesBufferReader, BytesWriter
from ..core.constants import PALETTE_SIZE


def write_record_stream(
    records: tuple[tuple[int, ...], ...],
    token_bits: int,
) -> bytes:
    packets: list[tuple[int, tuple[int, ...] | tuple[int, int]]] = []
    palette: list[int | None] = [None] * (PALETTE_SIZE + 1)
    base_tokens = select_base_palette(records)
    for slot, token in enumerate(base_tokens, start=1):
        palette[slot] = token
    packets.append((0, tuple(token for token in base_tokens)))
    stream = flatten_records(records)
    future_positions = build_future_positions(stream)

    local_codes: list[int] = []

    def flush_payload() -> None:
        if local_codes:
            packets.append((2, tuple(local_codes)))
            local_codes.clear()

    for position, token in enumerate(stream):
        if token is None:
            local_codes.append(0)
            continue
        consume_current_position(future_positions[token], position)
        try:
            slot = palette.index(token)
        except ValueError:
            flush_payload()
            slot = select_update_slot(palette, future_positions)
            palette[slot] = token
            packets.append((1, (slot, token)))
        local_codes.append(slot)
    flush_payload()

    writer = BytesWriter()
    writer.writeMbUInt(len(packets))
    for packet_type, value in packets:
        write_packet(writer, packet_type, value, token_bits)
    return bytes(writer.buffer)


def select_base_palette(records: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
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


def flatten_records(records: tuple[tuple[int, ...], ...]) -> list[int | None]:
    stream: list[int | None] = []
    for record in records:
        stream.extend(record)
        stream.append(None)
    return stream


def build_future_positions(stream: list[int | None]) -> defaultdict[int, deque[int]]:
    future_positions: defaultdict[int, deque[int]] = defaultdict(deque)
    for position, token in enumerate(stream):
        if token is not None:
            future_positions[token].append(position)
    return future_positions


def consume_current_position(positions: deque[int], position: int) -> None:
    if positions and positions[0] == position:
        positions.popleft()


def select_update_slot(
    palette: list[int | None],
    future_positions: defaultdict[int, deque[int]],
) -> int:
    for slot in range(1, PALETTE_SIZE + 1):
        if palette[slot] is None:
            return slot
    return max(
        range(1, PALETTE_SIZE + 1),
        key=lambda slot: (
            next_position(palette[slot], future_positions),
            palette[slot] if palette[slot] is not None else -1,
        ),
    )


def next_position(
    token: int | None,
    future_positions: defaultdict[int, deque[int]],
) -> int:
    if token is None:
        return 10**18
    positions = future_positions[token]
    return positions[0] if positions else 10**18


def write_packet(
    writer: BytesWriter,
    packet_type: int,
    value: tuple[int, ...] | tuple[int, int],
    token_bits: int,
) -> None:
    writer.writeBitsFromInt32(packet_type, 2)
    if packet_type == 0:
        tokens = value
        value_bit_size = 15 + len(tokens) * token_bits
        writer.writeMbUInt(value_bit_size)
        entry_slots = (1 << len(tokens)) - 1
        writer.writeBitsFromInt32(entry_slots, 15)
        for token in tokens:
            writer.writeBitsFromInt32(token, token_bits)
        return
    if packet_type == 1:
        slot, token = value
        value_bit_size = 4 + token_bits
        writer.writeMbUInt(value_bit_size)
        writer.writeBitsFromInt32(slot, 4)
        writer.writeBitsFromInt32(token, token_bits)
        return
    if packet_type == 2:
        local_codes = value
        value_bit_size = len(local_codes) * 4
        writer.writeMbUInt(value_bit_size)
        for local_code in local_codes:
            writer.writeBitsFromInt32(local_code, 4)
        return
    raise ValueError(f"unsupported packet_type: {packet_type}")


def decode_record_stream(
    record_stream: bytes,
    page_record_count: int,
    token_bits: int,
    tokens: tuple[bytes, ...],
) -> list[bytes]:
    return decode_record_stream_with_token_getter(
        record_stream,
        page_record_count,
        token_bits,
        lambda token_id: tokens[token_id],
    )


def decode_record_stream_with_token_getter(
    record_stream: bytes,
    page_record_count: int,
    token_bits: int,
    token_getter: Callable[[int], bytes],
) -> list[bytes]:
    reader = BytesBufferReader(record_stream)
    return decode_record_stream_reader_with_token_getter(
        reader,
        page_record_count,
        token_bits,
        token_getter,
    )


def decode_record_stream_reader_with_token_getter(
    reader: BytesBufferReader,
    page_record_count: int,
    token_bits: int,
    token_getter: Callable[[int], bytes],
) -> list[bytes]:
    packet_count = reader.readMbUInt()
    palette: list[int | None] = [None] * (PALETTE_SIZE + 1)
    records: list[bytes] = []
    current = bytearray()
    for _ in range(packet_count):
        packet_type = reader.readBitsAsInt32(2)
        value_bit_size = reader.readMbUInt()
        if packet_type == 0:
            start_pos = bit_pos(reader)
            entry_slots = reader.readBitsAsInt32(15)
            palette = [None] * (PALETTE_SIZE + 1)
            for bit_index in range(PALETTE_SIZE):
                if entry_slots & (1 << bit_index):
                    palette[bit_index + 1] = reader.readBitsAsInt32(token_bits)
            assert_consumed_bits(reader, start_pos, value_bit_size)
        elif packet_type == 1:
            start_pos = bit_pos(reader)
            slot = reader.readBitsAsInt32(4)
            if slot == 0:
                raise ValueError("TT00 UpdatePalettePacket slot must be non-zero")
            palette[slot] = reader.readBitsAsInt32(token_bits)
            assert_consumed_bits(reader, start_pos, value_bit_size)
        elif packet_type == 2:
            if value_bit_size % 4 != 0:
                raise ValueError("TT00 TokenPayloadPacket bit size must be multiple of 4")
            for _ in range(value_bit_size // 4):
                local_code = reader.readBitsAsInt32(4)
                if local_code == 0:
                    records.append(bytes(current))
                    current.clear()
                else:
                    token_id = palette[local_code]
                    if token_id is None:
                        raise ValueError("TT00 token payload references empty palette slot")
                    current.extend(token_getter(token_id))
        else:
            reader.readAsBitBytes(value_bit_size)
    if len(records) != page_record_count:
        raise ValueError("TT00 record terminator count mismatch")
    return records


def decode_record_stream_reader_target_with_token_getter(
    reader: BytesBufferReader,
    page_record_count: int,
    target_record: int,
    token_bits: int,
    token_getter: Callable[[int], bytes],
) -> bytes:
    if not 0 <= target_record < page_record_count:
        raise IndexError("TT00 page record index out of range")
    packet_count = reader.readMbUInt()
    palette: list[int | None] = [None] * (PALETTE_SIZE + 1)
    current = bytearray()
    record_index = 0
    for _ in range(packet_count):
        packet_type = reader.readBitsAsInt32(2)
        value_bit_size = reader.readMbUInt()
        if packet_type == 0:
            start_pos = bit_pos(reader)
            entry_slots = reader.readBitsAsInt32(15)
            palette = [None] * (PALETTE_SIZE + 1)
            for bit_index in range(PALETTE_SIZE):
                if entry_slots & (1 << bit_index):
                    palette[bit_index + 1] = reader.readBitsAsInt32(token_bits)
            assert_consumed_bits(reader, start_pos, value_bit_size)
        elif packet_type == 1:
            start_pos = bit_pos(reader)
            slot = reader.readBitsAsInt32(4)
            if slot == 0:
                raise ValueError("TT00 UpdatePalettePacket slot must be non-zero")
            palette[slot] = reader.readBitsAsInt32(token_bits)
            assert_consumed_bits(reader, start_pos, value_bit_size)
        elif packet_type == 2:
            if value_bit_size % 4 != 0:
                raise ValueError("TT00 TokenPayloadPacket bit size must be multiple of 4")
            for _ in range(value_bit_size // 4):
                local_code = reader.readBitsAsInt32(4)
                if local_code == 0:
                    if record_index == target_record:
                        return bytes(current)
                    record_index += 1
                    current.clear()
                elif record_index == target_record:
                    token_id = palette[local_code]
                    if token_id is None:
                        raise ValueError("TT00 token payload references empty palette slot")
                    current.extend(token_getter(token_id))
        else:
            reader.readAsBitBytes(value_bit_size)
    raise ValueError("TT00 target record terminator not found")


def decode_record_stream_as_token_ids(
    record_stream: bytes,
    page_record_count: int,
    token_bits: int,
) -> list[tuple[int, ...]]:
    reader = BytesBufferReader(record_stream)
    packet_count = reader.readMbUInt()
    palette: list[int | None] = [None] * (PALETTE_SIZE + 1)
    records: list[tuple[int, ...]] = []
    current: list[int] = []
    for _ in range(packet_count):
        packet_type = reader.readBitsAsInt32(2)
        value_bit_size = reader.readMbUInt()
        if packet_type == 0:
            start_pos = bit_pos(reader)
            entry_slots = reader.readBitsAsInt32(15)
            palette = [None] * (PALETTE_SIZE + 1)
            for bit_index in range(PALETTE_SIZE):
                if entry_slots & (1 << bit_index):
                    palette[bit_index + 1] = reader.readBitsAsInt32(token_bits)
            assert_consumed_bits(reader, start_pos, value_bit_size)
        elif packet_type == 1:
            start_pos = bit_pos(reader)
            slot = reader.readBitsAsInt32(4)
            if slot == 0:
                raise ValueError("TT00 UpdatePalettePacket slot must be non-zero")
            palette[slot] = reader.readBitsAsInt32(token_bits)
            assert_consumed_bits(reader, start_pos, value_bit_size)
        elif packet_type == 2:
            if value_bit_size % 4 != 0:
                raise ValueError("TT00 TokenPayloadPacket bit size must be multiple of 4")
            for _ in range(value_bit_size // 4):
                local_code = reader.readBitsAsInt32(4)
                if local_code == 0:
                    records.append(tuple(current))
                    current.clear()
                else:
                    token_id = palette[local_code]
                    if token_id is None:
                        raise ValueError("TT00 token payload references empty palette slot")
                    current.append(token_id)
        else:
            reader.readAsBitBytes(value_bit_size)
    if len(records) != page_record_count:
        raise ValueError("TT00 record terminator count mismatch")
    return records


def bit_pos(reader: BytesBufferReader) -> int:
    return reader.pos * 8 - reader.bitOffset


def assert_consumed_bits(reader: BytesBufferReader, start_pos: int, expected_bits: int) -> None:
    consumed = bit_pos(reader) - start_pos
    if consumed != expected_bits:
        raise ValueError(f"TT00 packet size mismatch: {consumed} != {expected_bits}")
