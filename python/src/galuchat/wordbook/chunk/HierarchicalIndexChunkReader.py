from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

from ...io import BytesBufferReader
from .HierarchicalIndexChunk import HierarchicalIndexChunk, _validate_header


@dataclass(frozen=True)
class HierarchicalIndexChunkReader:
    data: bytes
    max_depth: int
    record_count: int
    code_bits: int
    root_count: int
    index_stream_start: int
    index_stream_size: int

    @classmethod
    def unpack(cls, src: bytes, offset: int, size: int) -> "HierarchicalIndexChunkReader":
        reader = BytesBufferReader(src, offset=offset)
        max_depth = reader.readMbUInt()
        record_count = reader.readMbUInt()
        code_bits = reader.readMbUInt()
        root_count = reader.readMbUInt()
        stream_size = reader.readMbUInt()
        stream_start = offset + reader.pos
        reader.skipInByte(stream_size)
        if reader.pos != size:
            raise ValueError("TI00 has trailing bytes")
        _validate_header(max_depth, record_count, code_bits, root_count, stream_size)
        return cls(
            data=src,
            max_depth=max_depth,
            record_count=record_count,
            code_bits=code_bits,
            root_count=root_count,
            index_stream_start=stream_start,
            index_stream_size=stream_size,
        )

    def toChunk(self) -> HierarchicalIndexChunk:
        start = self.index_stream_start
        end = start + self.index_stream_size
        return HierarchicalIndexChunk(
            max_depth=self.max_depth,
            record_count=self.record_count,
            code_bits=self.code_bits,
            root_count=self.root_count,
            index_stream=self.data[start:end],
        )

    def readCodeSet(self, index: int, out: list[int] | None = None) -> list[int]:
        if not 0 <= index < self.record_count:
            raise IndexError("TI00 index out of range")
        if out is None:
            out = [0] * self.max_depth
        else:
            if len(out) < self.max_depth:
                out.extend(0 for _ in range(self.max_depth - len(out)))
            del out[self.max_depth:]
        reader = BytesBufferReader(self.data, offset=self.index_stream_start)
        if self.max_depth == 1:
            self._read_leaf_blocks_by_count(reader, self.root_count, index, out)
        else:
            self._read_prefixes_by_count(reader, 0, self.root_count, index, out)
        return out

    def iterCodeSetsFor(
        self,
        indices: Iterable[int],
        reuse_out: bool = False,
        run_buffer_limit: int = 4096,
    ) -> Iterator[list[int]]:
        """Yield code sets for indices, preserving input order.

        Non-decreasing runs are processed by a single forward scan over TI00.
        When an index is smaller than the previous one, the scan is restarted
        from the root.  If reuse_out is True, the yielded list object is reused
        across results and must be consumed before the next iteration step.
        run_buffer_limit bounds the temporary sorted-run index buffer.  Set it
        to 0 or a negative value to process a whole non-decreasing run at once.
        """
        run: list[int] = []
        previous: int | None = None
        for index in indices:
            if not 0 <= index < self.record_count:
                raise IndexError("TI00 index out of range")
            if previous is not None and index < previous:
                yield from self._iter_sorted_code_sets(run, reuse_out)
                run.clear()
            run.append(index)
            if run_buffer_limit > 0 and len(run) >= run_buffer_limit:
                yield from self._iter_sorted_code_sets(run, reuse_out)
                run.clear()
            previous = index
        if run:
            yield from self._iter_sorted_code_sets(run, reuse_out)

    def _read_prefixes_by_count(
        self,
        reader: BytesBufferReader,
        depth: int,
        prefix_count: int,
        target: int,
        out: list[int],
    ) -> None:
        for _ in range(prefix_count):
            code = reader.readBitsAsInt32(self.code_bits)
            leaf_count = reader.readMbUInt()
            payload_bits = reader.readMbUInt()
            if target < leaf_count:
                out[depth] = code
                self._read_children_by_leaf_count(reader, depth + 1, leaf_count, target, out)
                return
            self._skip_payload(reader, depth + 1, leaf_count, payload_bits)
            target -= leaf_count
        raise IndexError("TI00 index not found")

    def _read_children_by_leaf_count(
        self,
        reader: BytesBufferReader,
        depth: int,
        leaf_count: int,
        target: int,
        out: list[int],
    ) -> None:
        if depth == self.max_depth - 1:
            self._read_leaf_blocks_by_leaf_count(reader, leaf_count, target, out)
            return
        consumed = 0
        while consumed < leaf_count:
            code = reader.readBitsAsInt32(self.code_bits)
            child_leaf_count = reader.readMbUInt()
            payload_bits = reader.readMbUInt()
            if target < consumed + child_leaf_count:
                out[depth] = code
                self._read_children_by_leaf_count(
                    reader,
                    depth + 1,
                    child_leaf_count,
                    target - consumed,
                    out,
                )
                return
            self._skip_payload(reader, depth + 1, child_leaf_count, payload_bits)
            consumed += child_leaf_count
        raise IndexError("TI00 child index not found")

    def _read_leaf_blocks_by_count(
        self,
        reader: BytesBufferReader,
        block_count: int,
        target: int,
        out: list[int],
    ) -> None:
        for _ in range(block_count):
            leaf_count = reader.readMbUInt()
            if target < leaf_count:
                reader.skipBits(target * self.code_bits)
                out[self.max_depth - 1] = reader.readBitsAsInt32(self.code_bits)
                return
            reader.skipBits(leaf_count * self.code_bits)
            target -= leaf_count
        raise IndexError("TI00 leaf index not found")

    def _read_leaf_blocks_by_leaf_count(
        self,
        reader: BytesBufferReader,
        leaf_count: int,
        target: int,
        out: list[int],
    ) -> None:
        consumed = 0
        while consumed < leaf_count:
            block_leaf_count = reader.readMbUInt()
            if target < consumed + block_leaf_count:
                reader.skipBits((target - consumed) * self.code_bits)
                out[self.max_depth - 1] = reader.readBitsAsInt32(self.code_bits)
                return
            reader.skipBits(block_leaf_count * self.code_bits)
            consumed += block_leaf_count
        raise IndexError("TI00 leaf index not found")

    def _skip_payload(
        self,
        reader: BytesBufferReader,
        depth: int,
        leaf_count: int,
        payload_bits: int,
    ) -> None:
        if payload_bits > 0:
            reader.skipBits(payload_bits)
            return
        self._skip_children_by_leaf_count(reader, depth, leaf_count)

    def _skip_children_by_leaf_count(
        self,
        reader: BytesBufferReader,
        depth: int,
        leaf_count: int,
    ) -> None:
        consumed = 0
        if depth == self.max_depth - 1:
            while consumed < leaf_count:
                block_leaf_count = reader.readMbUInt()
                reader.skipBits(block_leaf_count * self.code_bits)
                consumed += block_leaf_count
            return
        while consumed < leaf_count:
            reader.readBitsAsInt32(self.code_bits)
            child_leaf_count = reader.readMbUInt()
            payload_bits = reader.readMbUInt()
            self._skip_payload(reader, depth + 1, child_leaf_count, payload_bits)
            consumed += child_leaf_count

    def _iter_sorted_code_sets(
        self,
        targets: list[int],
        reuse_out: bool,
    ) -> Iterator[list[int]]:
        cursor = _TargetCursor(targets)
        out = [0] * self.max_depth
        reader = BytesBufferReader(self.data, offset=self.index_stream_start)
        if self.max_depth == 1:
            yield from self._iter_leaf_blocks_for_targets(
                reader,
                self.record_count,
                0,
                cursor,
                out,
                reuse_out,
            )
        else:
            yield from self._iter_prefixes_for_targets(
                reader,
                0,
                self.root_count,
                0,
                cursor,
                out,
                reuse_out,
            )

    def _iter_prefixes_for_targets(
        self,
        reader: BytesBufferReader,
        depth: int,
        prefix_count: int,
        base_index: int,
        cursor: "_TargetCursor",
        out: list[int],
        reuse_out: bool,
    ) -> Iterator[list[int]]:
        current_base = base_index
        for _ in range(prefix_count):
            code = reader.readBitsAsInt32(self.code_bits)
            leaf_count = reader.readMbUInt()
            payload_bits = reader.readMbUInt()
            next_base = current_base + leaf_count
            if cursor.has() and cursor.current < next_base:
                out[depth] = code
                yield from self._iter_children_for_targets(
                    reader,
                    depth + 1,
                    leaf_count,
                    current_base,
                    cursor,
                    out,
                    reuse_out,
                )
            else:
                self._skip_payload(reader, depth + 1, leaf_count, payload_bits)
            current_base = next_base

    def _iter_children_for_targets(
        self,
        reader: BytesBufferReader,
        depth: int,
        leaf_count: int,
        base_index: int,
        cursor: "_TargetCursor",
        out: list[int],
        reuse_out: bool,
    ) -> Iterator[list[int]]:
        if depth == self.max_depth - 1:
            yield from self._iter_leaf_blocks_for_targets(
                reader,
                leaf_count,
                base_index,
                cursor,
                out,
                reuse_out,
            )
            return
        consumed = 0
        while consumed < leaf_count:
            code = reader.readBitsAsInt32(self.code_bits)
            child_leaf_count = reader.readMbUInt()
            payload_bits = reader.readMbUInt()
            child_base = base_index + consumed
            child_end = child_base + child_leaf_count
            if cursor.has() and cursor.current < child_end:
                out[depth] = code
                yield from self._iter_children_for_targets(
                    reader,
                    depth + 1,
                    child_leaf_count,
                    child_base,
                    cursor,
                    out,
                    reuse_out,
                )
            else:
                self._skip_payload(reader, depth + 1, child_leaf_count, payload_bits)
            consumed += child_leaf_count

    def _iter_leaf_blocks_for_targets(
        self,
        reader: BytesBufferReader,
        leaf_count: int,
        base_index: int,
        cursor: "_TargetCursor",
        out: list[int],
        reuse_out: bool,
    ) -> Iterator[list[int]]:
        consumed = 0
        while consumed < leaf_count:
            block_leaf_count = reader.readMbUInt()
            block_base = base_index + consumed
            block_end = block_base + block_leaf_count
            if not cursor.has() or cursor.current >= block_end:
                reader.skipBits(block_leaf_count * self.code_bits)
                consumed += block_leaf_count
                continue
            local_offset = 0
            while cursor.has() and cursor.current < block_end:
                target = cursor.current
                target_offset = target - block_base
                if target_offset > local_offset:
                    reader.skipBits((target_offset - local_offset) * self.code_bits)
                out[self.max_depth - 1] = reader.readBitsAsInt32(self.code_bits)
                local_offset = target_offset + 1
                while cursor.has() and cursor.current == target:
                    cursor.advance()
                    yield out if reuse_out else list(out)
            if local_offset < block_leaf_count:
                reader.skipBits((block_leaf_count - local_offset) * self.code_bits)
            consumed += block_leaf_count


class _TargetCursor:
    def __init__(self, targets: list[int]) -> None:
        self.targets = targets
        self.pos = 0

    def has(self) -> bool:
        return self.pos < len(self.targets)

    @property
    def current(self) -> int:
        return self.targets[self.pos]

    def advance(self) -> None:
        self.pos += 1


def parse_mapped_ti00_data(src: bytes, offset: int, size: int) -> HierarchicalIndexChunkReader:
    return HierarchicalIndexChunkReader.unpack(src, offset, size)
