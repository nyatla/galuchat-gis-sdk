# Map Render Types

## `MapFillRenderOptions`

```python
@dataclass(frozen=True)
class MapFillRenderOptions:
    defaultColor: Color = Color(0, 0, 0, 0)
    colors: Mapping[int, Color] = field(default_factory=dict)
    colorResolver: Callable[[int, int, int], Color | None] | None = None
```

| フィールド | 内容 |
| --- | --- |
| `defaultColor` | `colors` に存在しない値を描画する色 |
| `colors` | ラスタ値から描画色への対応表 |
| `colorResolver` | `colors` に存在しない値を動的に色へ変換する関数。引数は `(value, x, y)` |

`colors` のキーは `IRaster` の値である。特定の地名コード、小区域コード、内部インデックスなどを直接色に対応させる。

## `MapEdgeRenderOptions`

```python
@dataclass(frozen=True)
class MapEdgeRenderOptions:
    edgeColor: Color = Color(0, 0, 0, 255)
    backgroundColor: Color = Color(0, 0, 0, 0)
    edgeWidth: int = 1
    includeZero: bool = False
```

| フィールド | 内容 |
| --- | --- |
| `edgeColor` | 境界線の色 |
| `backgroundColor` | 境界線以外の背景色 |
| `edgeWidth` | 境界線の太さ。1以上の整数 |
| `includeZero` | `0` 値との境界を描画対象に含めるか |

## `MapImageRenderOptions`

```python
@dataclass(frozen=True)
class MapImageRenderOptions:
    fillOptions: MapFillRenderOptions = field(default_factory=MapFillRenderOptions)
    edgeOptions: MapEdgeRenderOptions | None = field(default_factory=MapEdgeRenderOptions)
```

| フィールド | 内容 |
| --- | --- |
| `fillOptions` | 塗分け描画Options |
| `edgeOptions` | 境界線描画Options。`None` の場合は境界線を描画しない |

## `RectAnchor`

```python
class RectAnchor(Enum):
    CENTER = "center"
    NORTHWEST = "northwest"
    SOUTHWEST = "southwest"
    NORTHEAST = "northeast"
    SOUTHEAST = "southeast"
```

`RectAnchor` は、基準点が矩形のどの位置を示すかを表す。

## `Color`

```python
@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
    a: int = 255
```

各成分は `0..255` の整数とする。

## `IImage`

画像データを表す型。

具体的な画像型は実装環境に委ねる。Python実装では `PIL.Image.Image`、Java実装では `BufferedImage` のような環境標準の画像型に対応してよい。

## `IRaster`

描画元ラスタを表すインタフェイス。

`IRaster` は低レベルAPIの [`IWgsMapset3Reader`](../lowlevel/IWgsMapset3Reader.md) で定義する。
