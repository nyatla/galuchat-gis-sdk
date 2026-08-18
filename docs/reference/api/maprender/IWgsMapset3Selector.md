# IWgsMapset3Selector

`IWgsMapset3Reader` からどの矩形ラスタを読むかを決定するインタフェイス。

`IWgsMapset3Selector` は矩形の指定方法だけを表す。座標変換と実際のラスタ読出しは `IWgsMapset3Reader` に委譲する。

```python
class IWgsMapset3Selector(Protocol):
    def readRaster(
        self,
        reader: IWgsMapset3Reader,
    ) -> IRaster:
        ...
```

| メソッド | 内容 |
| --- | --- |
| `readRaster` | `reader` から描画対象の矩形ラスタを読み出す |

## 責務

```text
IWgsMapset3Reader
  -> WGSMapSet/3 の読出し、座標変換、範囲解決

IWgsMapset3Selector
  -> どの矩形を読むかの指定

IMapRender
  -> 読み出された IRaster の画像化
```

`IWgsMapset3Selector` は `IRaster` ローカル座標を扱わない。LonLat指定もピクセル座標指定も、最終的には `IWgsMapset3Reader` の `readRect`, `readWgsRect`, `readWgsBounds` に委譲する。

## Selector例

### `PointRectSelector`

ピクセル座標基点とピクセルサイズから矩形を指定するSelector。

```python
@dataclass(frozen=True)
class PointRectSelector:
    x: int
    y: int
    width: int
    height: int
    anchor: RectAnchor | None = None

    def readRaster(self, reader: IWgsMapset3Reader) -> IRaster:
        return reader.readRect(
            self.x,
            self.y,
            self.width,
            self.height,
            self.anchor,
        )
```

`anchor` が `None` の場合は `RectAnchor.SOUTHWEST` と同じ意味とする。

### `WgsPointRectSelector`

LonLat基準地点とピクセルサイズから矩形を指定するSelector。

```python
@dataclass(frozen=True)
class WgsPointRectSelector:
    lon: float
    lat: float
    width: int
    height: int
    anchor: RectAnchor | None = None

    def readRaster(self, reader: IWgsMapset3Reader) -> IRaster:
        return reader.readWgsRect(
            self.lon,
            self.lat,
            self.width,
            self.height,
            self.anchor,
        )
```

`lon, lat` は、`anchor` が示す矩形上のLonLat座標である。`width, height` はピクセル数で指定する。

### `WgsBoundsSelector`

LonLat境界から矩形を指定するSelector。

```python
@dataclass(frozen=True)
class WgsBoundsSelector:
    west: float
    south: float
    east: float
    north: float

    def readRaster(self, reader: IWgsMapset3Reader) -> IRaster:
        return reader.readWgsBounds(
            self.west,
            self.south,
            self.east,
            self.north,
        )
```

LonLat境界は次の意味とする。

```text
west  = 西端経度
south = 南端緯度
east  = 東端経度
north = 北端緯度
```

### `FullMapsetSelector`

`IWgsMapset3Reader` の定義範囲全体を指定するSelector。

```python
@dataclass(frozen=True)
class FullMapsetSelector:
    def readRaster(self, reader: IWgsMapset3Reader) -> IRaster:
        bounds = reader.pixelBounds
        return reader.readRect(
            bounds.x,
            bounds.y,
            bounds.width,
            bounds.height,
        )
```
