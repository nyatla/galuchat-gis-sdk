
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, TypeAlias
import json


@dataclass(frozen=True)
class Inline:
    """
    scalar / scalarのみの dict,array を1行で出力する。
    """
    value: "CustomPrettyJsonType"


@dataclass(frozen=True)
class RowObject:
    """
    オブジェクトのメンバを行単位で出力する。
    """
    rows: tuple[tuple[tuple[str, "CustomPrettyJsonType"], ...], ...]


@dataclass(frozen=True)
class RowArray:
    """
    配列を group 個ずつ行分割して出力する。
    """
    values: tuple["CustomPrettyJsonType", ...]
    group: int


CustomPrettyJsonScalar: TypeAlias = str | int | float | bool | None
CustomPrettyJsonClass: TypeAlias = Inline | RowObject | RowArray

CustomPrettyJsonType: TypeAlias = (
    CustomPrettyJsonClass
    | CustomPrettyJsonScalar
    | list["CustomPrettyJsonType"]
    | tuple["CustomPrettyJsonType", ...]
    | dict[str, "CustomPrettyJsonType"]
)


class CustomPrettyWriter:
    def __init__(self, indent: int = 2):
        if indent < 0:
            raise ValueError("indent must be non-negative")
        self.indent = indent

    def dumps(self, obj: Any) -> str:
        return self._write(obj, 0) + "\n"

    def _write(self, obj: Any, level: int) -> str:
        if isinstance(obj, Inline):
            return self._write_inline(obj.value)

        if isinstance(obj, RowObject):
            return self._write_row_object(obj, level)

        if isinstance(obj, RowArray):
            return self._write_row_array(obj, level)

        if is_dataclass(obj):
            obj = self._dataclass_to_ordered_dict(obj)

        if isinstance(obj, dict):
            return self._write_object(obj, level)

        if isinstance(obj, list | tuple):
            return self._write_array(obj, level)

        if self._is_scalar(obj):
            return self._dump(obj)

        raise TypeError(f"unsupported JSON value: {type(obj).__name__}")

    def _write_object(self, obj: dict[str, Any], level: int) -> str:
        if not obj:
            return "{}"

        pad = self._pad(level)
        child_pad = self._pad(level + 1)

        lines = ["{"]
        items = list(obj.items())  # 挿入順維持

        for i, (k, v) in enumerate(items):
            if not isinstance(k, str):
                raise TypeError(f"object key must be str: {type(k).__name__}")

            comma = "," if i + 1 < len(items) else ""
            key = self._dump(k)
            value = self._write(v, level + 1)
            lines.append(f"{child_pad}{key}: {value}{comma}")

        lines.append(f"{pad}}}")
        return "\n".join(lines)

    def _write_array(self, arr: list | tuple, level: int) -> str:
        if not arr:
            return "[]"

        pad = self._pad(level)
        child_pad = self._pad(level + 1)

        lines = ["["]

        for i, v in enumerate(arr):
            comma = "," if i + 1 < len(arr) else ""
            value = self._write(v, level + 1)
            lines.append(f"{child_pad}{value}{comma}")

        lines.append(f"{pad}]")
        return "\n".join(lines)

    def _write_inline(self, obj: Any) -> str:
        if is_dataclass(obj):
            obj = self._dataclass_to_ordered_dict(obj)

        if not self._is_inline_value(obj):
            raise TypeError(f"not an inline JSON value: {type(obj).__name__}")

        return self._dump(obj)

    def _write_row_object(self, obj: RowObject, level: int) -> str:
        if not obj.rows:
            return "{}"

        pad = self._pad(level)
        child_pad = self._pad(level + 1)

        lines = ["{"]

        for row_index, row in enumerate(obj.rows):
            parts: list[str] = []

            for k, v in row:
                if not isinstance(k, str):
                    raise TypeError(f"object key must be str: {type(k).__name__}")

                key = self._dump(k)
                value = self._write_row_value(v, level + 1)
                parts.append(f"{key}:{value}")

            comma = "," if row_index + 1 < len(obj.rows) else ""
            lines.append(child_pad + ",".join(parts) + comma)

        lines.append(f"{pad}}}")
        return "\n".join(lines)

    def _write_row_array(self, obj: RowArray, level: int) -> str:
        if obj.group <= 0:
            raise ValueError("RowArray.group must be positive")

        if not obj.values:
            return "[]"

        pad = self._pad(level)
        child_pad = self._pad(level + 1)

        values = list(obj.values)
        lines = ["["]

        for i in range(0, len(values), obj.group):
            row = values[i:i + obj.group]
            parts = [self._write_row_value(v, level + 1) for v in row]

            comma = "," if i + obj.group < len(values) else ""
            lines.append(child_pad + ",".join(parts) + comma)

        lines.append(f"{pad}]")
        return "\n".join(lines)

    def _write_row_value(self, v: Any, level: int) -> str:
        """
        RowObject / RowArray 内で許可する値:
        - scalar
        - Inline
        - RowObject
        - RowArray

        通常 dict/list/tuple は不可。
        """
        if isinstance(v, Inline):
            return self._write_inline(v.value)

        if isinstance(v, RowObject):
            return self._write_row_object(v, level)

        if isinstance(v, RowArray):
            return self._write_row_array(v, level)

        if self._is_scalar(v):
            return self._dump(v)

        if isinstance(v, dict):
            raise TypeError("plain dict is not allowed in RowObject/RowArray")

        if isinstance(v, list | tuple):
            raise TypeError("plain list/tuple is not allowed in RowObject/RowArray")

        if is_dataclass(v):
            raise TypeError(f"dataclass is not allowed in RowObject/RowArray: {type(v).__name__}")

        raise TypeError(f"unsupported RowObject/RowArray value: {type(v).__name__}")

    def _is_inline_value(self, obj: Any) -> bool:
        if self._is_scalar(obj):
            return True

        if isinstance(obj, list | tuple):
            return all(self._is_scalar(v) for v in obj)

        if isinstance(obj, dict):
            return all(
                isinstance(k, str) and self._is_scalar(v)
                for k, v in obj.items()
            )

        return False

    def _dataclass_to_ordered_dict(self, obj: Any) -> dict[str, Any]:
        out: dict[str, Any] = {}

        for f in fields(obj):
            if f.name.startswith("_"):
                continue

            name = f.metadata.get("json", f.name.replace("_", "-"))
            out[name] = getattr(obj, f.name)

        return out

    def _is_scalar(self, v: Any) -> bool:
        return v is None or isinstance(v, str | int | float | bool)

    def _dump(self, obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

    def _pad(self, level: int) -> str:
        return " " * (self.indent * level)