from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from ...io import BytesBufferReader, BytesWriter


@dataclass(frozen=True)
class HierarchicalIndexChunk:
    max_depth: int
    record_count: int
    code_bits: int
    root_count: int
    index_stream: bytes


def required_code_bits(code_count: int) -> int:
    if code_count < 0:
        raise ValueError("code_count must not be negative")
    if code_count <= 1:
        return 1
    return (code_count - 1).bit_length()


def build_hierarchical_index(
    code_paths: Iterable[Sequence[int]],
    code_bits: int,
    write_payload_bits: bool = True,
) -> HierarchicalIndexChunk:
    paths = tuple(tuple(path) for path in code_paths)
    if not paths:
        raise ValueError("TI00 requires at least one path")
    max_depth = len(paths[0])
    if max_depth <= 0:
        raise ValueError("TI00 path depth must be positive")
    for path in paths:
        if len(path) != max_depth:
            raise ValueError("TI00 paths must have fixed depth")
        for code in path:
            if code < 0:
                raise ValueError("TI00 code must not be negative")
            if code >= (1 << code_bits):
                raise ValueError("TI00 code exceeds code_bits")

    writer = BytesWriter()
    root_count = _write_nodes(writer, paths, 0, max_depth, code_bits, write_payload_bits)
    return HierarchicalIndexChunk(
        max_depth=max_depth,
        record_count=len(paths),
        code_bits=code_bits,
        root_count=root_count,
        index_stream=bytes(writer.buffer),
    )


def write_ti00_data(index: HierarchicalIndexChunk) -> bytes:
    writer = BytesWriter()
    writer.writeMbUInt(index.max_depth)
    writer.writeMbUInt(index.record_count)
    writer.writeMbUInt(index.code_bits)
    writer.writeMbUInt(index.root_count)
    writer.writeMbUInt(len(index.index_stream))
    writer.writeBytes(index.index_stream)
    return bytes(writer.buffer)


def parse_ti00_data(data: bytes) -> HierarchicalIndexChunk:
    reader = BytesBufferReader(data)
    max_depth = reader.readMbUInt()
    record_count = reader.readMbUInt()
    code_bits = reader.readMbUInt()
    root_count = reader.readMbUInt()
    stream_size = reader.readMbUInt()
    index_stream = reader.readAsBytes(stream_size)
    if reader.pos != len(data):
        raise ValueError("TI00 has trailing bytes")
    _validate_header(max_depth, record_count, code_bits, root_count, stream_size)
    return HierarchicalIndexChunk(
        max_depth=max_depth,
        record_count=record_count,
        code_bits=code_bits,
        root_count=root_count,
        index_stream=index_stream,
    )


def _validate_header(
    max_depth: int,
    record_count: int,
    code_bits: int,
    root_count: int,
    stream_size: int,
) -> None:
    if max_depth <= 0:
        raise ValueError("TI00 max_depth must be positive")
    if record_count <= 0:
        raise ValueError("TI00 record_count must be positive")
    if not 1 <= code_bits <= 31:
        raise ValueError("TI00 code_bits must be in 1..31")
    if root_count <= 0:
        raise ValueError("TI00 root_count must be positive")
    if stream_size <= 0:
        raise ValueError("TI00 IndexStream must not be empty")


def _write_nodes(
    writer: BytesWriter,
    paths: tuple[tuple[int, ...], ...],
    depth: int,
    max_depth: int,
    code_bits: int,
    write_payload_bits: bool,
) -> int:
    if depth == max_depth - 1:
        _write_leaf_block(writer, paths, depth, code_bits)
        return 1

    count = 0
    start = 0
    while start < len(paths):
        code = paths[start][depth]
        end = start + 1
        while end < len(paths) and paths[end][depth] == code:
            end += 1
        _write_prefix_container(
            writer,
            code,
            paths[start:end],
            depth,
            max_depth,
            code_bits,
            write_payload_bits,
        )
        count += 1
        start = end
    return count


def _write_prefix_container(
    writer: BytesWriter,
    code: int,
    paths: tuple[tuple[int, ...], ...],
    depth: int,
    max_depth: int,
    code_bits: int,
    write_payload_bits: bool,
) -> None:
    child_writer = BytesWriter()
    _write_nodes(child_writer, paths, depth + 1, max_depth, code_bits, write_payload_bits)
    child_bits = _written_bit_count(child_writer)
    child_bytes = bytes(child_writer.buffer)

    writer.writeBitsFromInt32(code, code_bits)
    writer.writeMbUInt(len(paths))
    writer.writeMbUInt(child_bits if write_payload_bits else 0)
    writer.writeBitBytes(child_bytes, child_bits)


def _write_leaf_block(
    writer: BytesWriter,
    paths: tuple[tuple[int, ...], ...],
    depth: int,
    code_bits: int,
) -> None:
    writer.writeMbUInt(len(paths))
    for path in paths:
        writer.writeBitsFromInt32(path[depth], code_bits)


def _written_bit_count(writer: BytesWriter) -> int:
    byte_count = len(writer.buffer)
    if writer.bitOffset == 0:
        return byte_count * 8
    return (byte_count - 1) * 8 + writer.bitOffset

