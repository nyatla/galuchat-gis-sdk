from typing import Any, ClassVar, Self
from dataclasses import dataclass

from .JsonContainer import JsonContainer
from .writer import CustomPrettyJsonType, Inline, RowArray


@dataclass
class GridInfoContainer(JsonContainer):
    """グリッド分割されたファイル群の配置情報を格納するコンテナ。"""

    @dataclass(frozen=True)
    class FileName:
        pattern: str
        empty: str | None = None

        def toPrettyJson(self) -> CustomPrettyJsonType:
            return {
                "pattern": self.pattern,
                "empty": self.empty,
            }

        @classmethod
        def parse(cls, src: Any) -> Self:
            return cls(
                str(src["pattern"]),
                None if src.get("empty") is None else str(src["empty"]),
            )

    @dataclass(frozen=True)
    class GridSet:
        x: int
        y: int

        def toPrettyJson(self) -> CustomPrettyJsonType:
            return {
                "x": self.x,
                "y": self.y,
            }

        @classmethod
        def parse(cls, src: Any) -> Self:
            return cls(int(src["x"]), int(src["y"]))

    CHUNK_TYPE: ClassVar[str] = "GridInfo:1"
    extension: str
    filename: FileName
    gridset: GridSet
    grids: tuple[tuple[str | None, ...], ...]

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def toPrettyJson(self) -> CustomPrettyJsonType:
        return {
            "type": self.CHUNK_TYPE,
            "extension": self.extension,
            "filename": self.filename.toPrettyJson(),
            "gridset": self.gridset.toPrettyJson(),
            "grids": RowArray(tuple(Inline(row) for row in self.grids), group=1),
        }

    @classmethod
    def parse(cls, src: Any) -> Self:
        if src["type"] != cls.CHUNK_TYPE:
            raise RuntimeError()

        grids = tuple(
            tuple(None if cell is None else str(cell) for cell in row)
            for row in src["grids"]
        )
        return cls(
            str(src["extension"]),
            cls.FileName.parse(src["filename"]),
            cls.GridSet.parse(src["gridset"]),
            grids,
        )

    @classmethod
    def create(
        cls,
        extension: str,
        grid_width: int,
        grid_height: int,
        grids: list[list[str | None]] | tuple[tuple[str | None, ...], ...],
        pattern: str = "{x:03}_{y:03}.{extension}",
        empty: str | None = None,
    ) -> Self:
        return cls(
            extension,
            cls.FileName(pattern, empty),
            cls.GridSet(grid_width, grid_height),
            tuple(tuple(row) for row in grids),
        )

    def _validate(self):
        if self.gridset.x < 0 or self.gridset.y < 0:
            raise ValueError("gridset dimensions must be non-negative.")
        if len(self.grids) != self.gridset.y:
            raise ValueError("grids row count must match gridset.y.")
        for row in self.grids:
            if len(row) != self.gridset.x:
                raise ValueError("grids column count must match gridset.x.")
