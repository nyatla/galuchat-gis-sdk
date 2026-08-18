from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence

from ...chunk import Chunk
from ...io import BytesBufferReader, BytesWriter
from ..chunk.common import read_mapped_chunk
from ..chunk.GisWordBookHeaderChunk import (
    GisWordBookHeaderChunk,
    parse_gw00_data,
    write_gw00_data,
)
from ..chunk.GisWordBookHeaderChunkReader import parse_mapped_gw00_data
from ..chunk.HierarchicalIndexChunk import (
    HierarchicalIndexChunk,
    build_hierarchical_index,
    parse_ti00_data,
    required_code_bits,
    write_ti00_data,
)
from ..chunk.HierarchicalIndexChunkReader import parse_mapped_ti00_data
from ..chunk.TextTableChunk import TextTableChunk, parse_tt00_data, write_tt00_data
from ..chunk.TextTableChunkReader import (
    decode_mapped_page_record_with_token_getter,
    parse_mapped_tt00_data,
)
from ..chunk.TokenMapChunk import TokenMapChunk, parse_tm00_data, write_tm00_data
from ..chunk.TokenMapChunkReader import parse_mapped_tm00_data
from .constants import (
    DEFAULT_PAGE_SIZE,
    GISWORDBOOK_HEADER_CHUNK,
    HIERARCHICAL_INDEX_CHUNK,
    TEXT_TABLE_CHUNK,
    TOKEN_MAP_CHUNK,
)
from .WordBookModel import WordBookModel, normalize_text_token_encoding, required_token_bits
from .WordBookOptimizer import TokenMergeRecord, WordBookOptimizer, grouped_page_order


@dataclass(frozen=True)
class GaluchatGisWordBookDom:
    header: GisWordBookHeaderChunk
    token_map: TokenMapChunk
    text_table: TextTableChunk
    index: HierarchicalIndexChunk

    @classmethod
    def createFromPaths(
        cls,
        paths: Iterable[Sequence[str]],
        page_size: int = DEFAULT_PAGE_SIZE,
        metadata: str | None = None,
        token_bits: int | None = None,
        code_bits: int | None = None,
        write_payload_bits: bool = True,
        text_encoding: str = "utf-8",
        optimize_tokens: bool = False,
        token_optimizer: WordBookOptimizer | None = None,
        token_merge_report: list[TokenMergeRecord] | None = None,
        page_order_strategy: str | None = None,
    ) -> "GaluchatGisWordBookDom":
        rows = tuple(tuple(component for component in path) for path in paths)
        if not rows:
            raise ValueError("GisWordBook requires at least one path")
        depth = len(rows[0])
        if depth <= 0:
            raise ValueError("GisWordBook path depth must be positive")
        for row in rows:
            if len(row) != depth:
                raise ValueError("GisWordBook paths must have fixed depth")

        texts = _unique_components(rows)
        model = WordBookModel.from_texts(
            texts,
            page_size=page_size,
            encoding=text_encoding,
        )
        if optimize_tokens:
            optimizer = token_optimizer if token_optimizer is not None else WordBookOptimizer(
                size_priority=True,
            )
            model = optimizer.optimizeTokens(model, report=token_merge_report)
        if page_order_strategy is not None:
            order = grouped_page_order(model.records, page_order_strategy)
            texts = tuple(texts[index] for index in order)
            model = WordBookModel(
                page_size=model.page_size,
                tokens=model.tokens,
                records=tuple(model.records[index] for index in order),
            )

        required_tbits = required_token_bits(len(model.tokens))
        if token_bits is None:
            token_bits = required_tbits
        if token_bits < required_tbits:
            raise ValueError("token_bits is smaller than token table requires")

        required_cbits = required_code_bits(len(texts))
        if code_bits is None:
            code_bits = required_cbits
        if code_bits < required_cbits:
            raise ValueError("code_bits is smaller than text table requires")

        text_table = _build_text_table_from_model(model, token_bits)
        code_by_text = _build_text_code_map(texts, model.records)
        code_paths = tuple(
            tuple(code_by_text[component] for component in row)
            for row in rows
        )
        index = build_hierarchical_index(
            code_paths,
            code_bits=code_bits,
            write_payload_bits=write_payload_bits,
        )
        return cls(
            header=GisWordBookHeaderChunk(metadata=metadata),
            token_map=TokenMapChunk(tokens=model.tokens),
            text_table=text_table,
            index=index,
        )

    @classmethod
    def createFromAddressComponentTree(
        cls,
        tree: dict,
        page_size: int = DEFAULT_PAGE_SIZE,
        metadata: str | None = None,
        token_bits: int | None = None,
        code_bits: int | None = None,
        write_payload_bits: bool = True,
        text_encoding: str = "utf-8",
        optimize_tokens: bool = False,
        token_optimizer: WordBookOptimizer | None = None,
        token_merge_report: list[TokenMergeRecord] | None = None,
        page_order_strategy: str | None = None,
    ) -> "GaluchatGisWordBookDom":
        depth = int(tree["depth"])
        paths = paths_from_address_component_tree(tree["data"], depth)
        return cls.createFromPaths(
            paths,
            page_size=page_size,
            metadata=metadata,
            token_bits=token_bits,
            code_bits=code_bits,
            write_payload_bits=write_payload_bits,
            text_encoding=text_encoding,
            optimize_tokens=optimize_tokens,
            token_optimizer=token_optimizer,
            token_merge_report=token_merge_report,
            page_order_strategy=page_order_strategy,
        )

    @classmethod
    def pack(cls, src: "GaluchatGisWordBookDom") -> bytes:
        writer = BytesWriter()
        Chunk.pack(GISWORDBOOK_HEADER_CHUNK, write_gw00_data(src.header), writer)
        Chunk.pack(TOKEN_MAP_CHUNK, write_tm00_data(src.token_map), writer)
        Chunk.pack(TEXT_TABLE_CHUNK, write_tt00_data(src.text_table), writer)
        Chunk.pack(HIERARCHICAL_INDEX_CHUNK, write_ti00_data(src.index), writer)
        return bytes(writer.buffer)

    @classmethod
    def unpack(cls, src: bytes) -> "GaluchatGisWordBookDom":
        reader = BytesBufferReader(src)
        header_chunk = Chunk.unpack(reader)
        if header_chunk.name != GISWORDBOOK_HEADER_CHUNK:
            raise ValueError("GisWordBook must start with GW00")
        token_chunk = Chunk.unpack(reader)
        if token_chunk.name != TOKEN_MAP_CHUNK:
            raise ValueError("GisWordBook must contain TM00 after GW00")
        text_chunk = Chunk.unpack(reader)
        if text_chunk.name != TEXT_TABLE_CHUNK:
            raise ValueError("GisWordBook must contain TT00 after TM00")
        index_chunk = Chunk.unpack(reader)
        if index_chunk.name != HIERARCHICAL_INDEX_CHUNK:
            raise ValueError("GisWordBook must contain TI00 after TT00")
        if reader.pos != len(src):
            raise ValueError("GisWordBook has trailing bytes")

        header = parse_gw00_data(header_chunk.data)
        token_map = parse_tm00_data(token_chunk.data)
        text_table = parse_tt00_data(text_chunk.data)
        index = parse_ti00_data(index_chunk.data)
        _validate_relations(token_map, text_table, index)
        return cls(header=header, token_map=token_map, text_table=text_table, index=index)


class GaluchatGisWordBookReader:
    def __init__(self, header, token_map, text_table, index):
        self._header = header
        self._token_map = token_map
        self._text_table = text_table
        self._index = index
        self._code_buffer = [0] * index.max_depth

    @classmethod
    def unpack(
        cls,
        src: bytes,
        token_cache_size: int = 64,
    ) -> "GaluchatGisWordBookReader":
        reader = BytesBufferReader(src)
        header_chunk = read_mapped_chunk(reader, len(src))
        if header_chunk.name != GISWORDBOOK_HEADER_CHUNK:
            raise ValueError("GisWordBook must start with GW00")
        token_chunk = read_mapped_chunk(reader, len(src))
        if token_chunk.name != TOKEN_MAP_CHUNK:
            raise ValueError("GisWordBook must contain TM00 after GW00")
        text_chunk = read_mapped_chunk(reader, len(src))
        if text_chunk.name != TEXT_TABLE_CHUNK:
            raise ValueError("GisWordBook must contain TT00 after TM00")
        index_chunk = read_mapped_chunk(reader, len(src))
        if index_chunk.name != HIERARCHICAL_INDEX_CHUNK:
            raise ValueError("GisWordBook must contain TI00 after TT00")
        if reader.pos != len(src):
            raise ValueError("GisWordBook has trailing bytes")

        header = parse_mapped_gw00_data(src, header_chunk.data_start, header_chunk.size)
        token_map = parse_mapped_tm00_data(
            src,
            token_chunk.data_start,
            token_chunk.size,
            cache_size=token_cache_size,
        )
        text_table = parse_mapped_tt00_data(src, text_chunk.data_start, text_chunk.size)
        index = parse_mapped_ti00_data(src, index_chunk.data_start, index_chunk.size)
        if text_table.token_bits < required_token_bits(token_map.token_count):
            raise ValueError("TT00 token_bits is smaller than TM00 token table requires")
        if index.code_bits < required_code_bits(text_table.record_count):
            raise ValueError("TI00 code_bits is smaller than TT00 text table requires")
        return cls(header, token_map, text_table, index)

    @property
    def record_count(self) -> int:
        return self._index.record_count

    @property
    def depth(self) -> int:
        return self._index.max_depth

    @property
    def component_count(self) -> int:
        return self._text_table.record_count

    def recordCount(self) -> int:
        return self.record_count

    def readCodeSet(self, index: int, out: list[int] | None = None) -> list[int]:
        return self._index.readCodeSet(index, out)

    def iterCodeSetsFor(
        self,
        indices: Iterable[int],
        reuse_out: bool = False,
        run_buffer_limit: int = 4096,
    ) -> Iterator[list[int]]:
        return self._index.iterCodeSetsFor(
            indices,
            reuse_out=reuse_out,
            run_buffer_limit=run_buffer_limit,
        )

    def readComponentBytes(self, code: int) -> bytes:
        return _read_text_bytes(self._text_table, self._token_map, code)

    def readComponent(self, code: int, encoding: str = "utf-8") -> str:
        return self.readComponentBytes(code).decode(normalize_text_token_encoding(encoding))

    def readStringSet(
        self,
        index: int,
        out: list[str] | None = None,
        encoding: str = "utf-8",
    ) -> list[str]:
        codes = self.readCodeSet(index, self._code_buffer)
        if out is None:
            out = []
        else:
            out.clear()
        for code in codes:
            out.append(self.readComponent(code, encoding=encoding))
        return out

    def iterStringSetsFor(
        self,
        indices: Iterable[int],
        encoding: str = "utf-8",
        reuse_out: bool = False,
        run_buffer_limit: int = 4096,
    ) -> Iterator[list[str]]:
        out: list[str] = []
        for codes in self.iterCodeSetsFor(
            indices,
            reuse_out=True,
            run_buffer_limit=run_buffer_limit,
        ):
            out.clear()
            for code in codes:
                out.append(self.readComponent(code, encoding=encoding))
            yield out if reuse_out else list(out)


def paths_from_address_component_tree(data: Sequence, depth: int) -> tuple[tuple[str, ...], ...]:
    if depth <= 0:
        raise ValueError("AddressComponentTree depth must be positive")
    paths: list[tuple[str, ...]] = []
    for node in data:
        _walk_address_node(node, depth, [], paths)
    return tuple(paths)


def _walk_address_node(
    node,
    max_depth: int,
    prefix: list[str],
    paths: list[tuple[str, ...]],
) -> None:
    if not isinstance(node, list) or not node:
        raise ValueError("AddressComponentTree node must be a non-empty list")
    name = node[0]
    if not isinstance(name, str):
        raise ValueError("AddressComponentTree node name must be a string")
    current = prefix + [name]
    if len(current) == max_depth:
        paths.append(tuple(current))
        return
    if len(node) < 2:
        raise ValueError("AddressComponentTree internal node must have children")
    children = node[1]
    if not isinstance(children, list):
        raise ValueError("AddressComponentTree children must be a list")
    for child in children:
        _walk_address_node(child, max_depth, current, paths)


def _unique_components(rows: tuple[tuple[str, ...], ...]) -> tuple[str, ...]:
    seen: dict[str, None] = {}
    for row in rows:
        for component in row:
            seen.setdefault(component, None)
    return tuple(seen.keys())


def _build_text_code_map(
    texts: tuple[str, ...],
    records: tuple[tuple[int, ...], ...],
) -> dict[str, int]:
    ordered_indices = sorted(range(len(records)), key=lambda index: len(records[index]))
    return {
        texts[text_index]: code
        for code, text_index in enumerate(ordered_indices)
    }


def _build_text_table_from_model(model: WordBookModel, token_bits: int) -> TextTableChunk:
    from ..chunk.TextTableChunk import build_text_table

    if not 1 <= token_bits <= 16:
        raise ValueError("token_bits must be in 1..16")
    return build_text_table(model.records, model.page_size, token_bits)


def _read_text_bytes(text_table, token_map, code: int) -> bytes:
    if not 0 <= code < text_table.record_count:
        raise KeyError(code)
    record_base = 0
    for page in text_table.pages:
        if code < record_base + page.page_record_count:
            return decode_mapped_page_record_with_token_getter(
                token_map.data,
                page,
                code - record_base,
                text_table.token_bits,
                token_map.get,
            )
        record_base += page.page_record_count
    raise KeyError(code)


def _validate_relations(
    token_map: TokenMapChunk,
    text_table: TextTableChunk,
    index: HierarchicalIndexChunk,
) -> None:
    if text_table.token_bits < required_token_bits(len(token_map.tokens)):
        raise ValueError("TT00 token_bits is smaller than TM00 token table requires")
    if index.code_bits < required_code_bits(text_table.record_count):
        raise ValueError("TI00 code_bits is smaller than TT00 text table requires")
