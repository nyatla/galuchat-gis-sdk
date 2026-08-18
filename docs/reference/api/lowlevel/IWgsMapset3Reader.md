# IWgsMapset3Reader

`WGSMapSet/3` を読み取るためのアプリケーション向けインタフェイス。

## プロパティ

```python
class IWgsMapset3Reader(Protocol):
    @property
    def unitInvX(self) -> int:
        ...

    @property
    def unitInvY(self) -> int:
        ...

    @property
    def mapCount(self) -> int:
        ...

    @property
    def pixelBounds(self) -> PixelRect:
        ...

    @property
    def lonLatBounds(self) -> LonLatRect:
        ...

    @property
    def metadata(self) -> str | None:
        ...
```

| プロパティ | 内容 |
| --- | --- |
| `unitInvX` | 経度方向の単位逆数 |
| `unitInvY` | 緯度方向の単位逆数 |
| `mapCount` | WGSMapSetに含まれるWGSMap数 |
| `pixelBounds` | WGSMapSet全体のピクセル座標範囲 |
| `lonLatBounds` | WGSMapSet全体のLonLat範囲 |
| `metadata` | WGSMapSetヘッダのメタデータ |

## 座標変換

```python
class IWgsMapset3Reader(Protocol):
    def wgsToPoint(
        self,
        lon: float,
        lat: float,
    ) -> PixelPoint:
        ...

    def pointToWgs(
        self,
        x: int,
        y: int,
    ) -> LonLatPoint:
        ...
```

| メソッド | 内容 |
| --- | --- |
| `wgsToPoint` | LonLat座標をピクセル座標へ変換する |
| `pointToWgs` | ピクセル座標をLonLat座標へ変換する |

変換規則は次の通り。

```text
wgsToPoint:
  x = round(lon * unitInvX)
  y = round(lat * unitInvY)

pointToWgs:
  lon = x / unitInvX
  lat = y / unitInvY
```

## 範囲判定

```python
class IWgsMapset3Reader(Protocol):
    def containsPoint(
        self,
        x: int,
        y: int,
    ) -> bool:
        ...

    def containsWgsPoint(
        self,
        lon: float,
        lat: float,
    ) -> bool:
        ...
```

| メソッド | 内容 |
| --- | --- |
| `containsPoint` | ピクセル座標がWGSMapSet全体の定義範囲内かを返す |
| `containsWgsPoint` | LonLat座標がWGSMapSet全体の定義範囲内かを返す |

`containsPoint` は `pixelBounds` を基準に判定する。

```text
pixelBounds.x <= x < pixelBounds.x + pixelBounds.width
pixelBounds.y <= y < pixelBounds.y + pixelBounds.height
```

`containsWgsPoint` は `wgsToPoint` で変換したピクセル座標を `containsPoint` で判定する。

この判定はWGSMapSet全体の定義範囲だけを対象とし、該当WGSMapの有無やピクセル値の有無は判定しない。

## 点読出し

```python
class IWgsMapset3Reader(Protocol):
    def readPoint(
        self,
        x: int,
        y: int,
    ) -> int | None:
        ...

    def readWgsPoint(
        self,
        lon: float,
        lat: float,
    ) -> int | None:
        ...
```

| メソッド | 内容 |
| --- | --- |
| `readPoint` | ピクセル座標で1点を読む |
| `readWgsPoint` | LonLat座標で1点を読む |

戻り値:

| 戻り値 | 内容 |
| --- | --- |
| `None` | 範囲外、または該当WGSMapなし |
| `0` | 範囲内だが未設定 |
| `> 0` | 地図データの値 |

`containsPoint` と `readPoint` の関係は次の通り。

```text
containsPoint == false
  -> 完全に範囲外

containsPoint == true and readPoint == None
  -> 範囲内だが該当WGSMapなし、または内部データなし

containsPoint == true and readPoint == 0
  -> 範囲内、有効読出し、値は未設定

containsPoint == true and readPoint > 0
  -> 範囲内、有効値
```

## 矩形読出し

```python
class IWgsMapset3Reader(Protocol):
    def readRect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        anchor: RectAnchor | None = None,
    ) -> IRaster:
        ...

    def readWgsRect(
        self,
        lon: float,
        lat: float,
        width: int,
        height: int,
        anchor: RectAnchor | None = None,
    ) -> IRaster:
        ...

    def readWgsBounds(
        self,
        west: float,
        south: float,
        east: float,
        north: float,
    ) -> IRaster:
        ...
```

| メソッド | 内容 |
| --- | --- |
| `readRect` | ピクセル座標基点とピクセルサイズから矩形ラスタを読む |
| `readWgsRect` | LonLat基点とピクセルサイズから矩形ラスタを読む |
| `readWgsBounds` | LonLat境界から矩形ラスタを読む |

`anchor` が `None` の場合は `RectAnchor.SOUTHWEST` と同じ意味とする。

`readRect` の `x, y` は、`anchor` が示す矩形上のピクセル座標である。

`readWgsRect` の `lon, lat` は、`anchor` が示す矩形上のLonLat座標である。`width, height` はピクセル数で指定する。

`readWgsRect` は次の規則で `readRect` に変換する。

```text
p = wgsToPoint(lon, lat)
readRect(p.x, p.y, width, height, anchor)
```

`readRect` は `anchor` から左下ピクセル座標を次のように解決する。

```text
anchor == None or SOUTHWEST:
  left   = x
  bottom = y

anchor == CENTER:
  left   = x - width // 2
  bottom = y - height // 2

anchor == NORTHWEST:
  left   = x
  bottom = y - height

anchor == NORTHEAST:
  left   = x - width
  bottom = y - height

anchor == SOUTHEAST:
  left   = x - width
  bottom = y
```

`readWgsBounds` はLonLatの矩形境界を受け取る。

```text
west  = 西端経度
south = 南端緯度
east  = 東端経度
north = 北端緯度
```

`readWgsBounds` のピクセル化は次の規則とする。

```text
sw = wgsToPoint(west, south)
ne = wgsToPoint(east, north)

x      = sw.x
y      = sw.y
width  = ne.x - sw.x
height = ne.y - sw.y
```

## 型

### `RectAnchor`

```python
class RectAnchor(Enum):
    CENTER = "center"
    NORTHWEST = "northwest"
    SOUTHWEST = "southwest"
    NORTHEAST = "northeast"
    SOUTHEAST = "southeast"
```

### `PixelPoint`

```python
@dataclass(frozen=True)
class PixelPoint:
    x: int
    y: int
```

### `LonLatPoint`

```python
@dataclass(frozen=True)
class LonLatPoint:
    lon: float
    lat: float
```

### `PixelRect`

```python
@dataclass(frozen=True)
class PixelRect:
    x: int
    y: int
    width: int
    height: int
```

### `LonLatRect`

```python
@dataclass(frozen=True)
class LonLatRect:
    west: float
    south: float
    east: float
    north: float
```

### `IRaster`

矩形読出し結果を表すラスタインタフェイス。

この文書では最小要件だけを定義する。

```python
class IRaster(Protocol):
    @property
    def width(self) -> int:
        ...

    @property
    def height(self) -> int:
        ...

    def get(self, x: int, y: int) -> int:
        ...
```
