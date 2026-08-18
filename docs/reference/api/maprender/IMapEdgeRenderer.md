# IMapEdgeRenderer

`IRaster` の値境界から境界線画像を生成するインタフェイス。

```python
class IMapEdgeRenderer(
    IMapRender[MapEdgeRenderOptions, ImageT],
    Protocol[ImageT],
):
    ...
```

`IMapEdgeRenderer` は `IMapRender` の `OptionsT` を `MapEdgeRenderOptions` に固定する。

```python
def render(
    self,
    reader: IWgsMapset3Reader,
    selector: IWgsMapset3Selector,
    options: MapEdgeRenderOptions | None = None,
) -> ImageT:
    ...
```

| 引数 | 内容 |
| --- | --- |
| `reader` | 描画元WGSMapSet/3 Reader |
| `selector` | 境界線生成対象の矩形ラスタを読み出すSelector |
| `options` | 境界線描画Options。`None` の場合は `defaultOptions` を使う |

境界線は、`selector.readRaster(reader)` で得た矩形ラスタ内で上下左右に隣接するピクセルの値が異なる箇所として描画する。

境界線判定の具体的なアルゴリズムは実装に委ねる。ただし、境界線生成は画像から復元せず、必ず元の `IRaster` の値差分を入力にする。

PythonのPIL実装では、東または北の隣接ピクセルと値が異なるラスタピクセルを単側の境界ピクセルとして `edgeColor` で描画する。`edgeWidth` が2以上の場合は、この境界ピクセルを `edgeWidth x edgeWidth` のブロックへ拡大して描画する。`includeZero` が `False` の場合、`0` 値を含む境界は描画しない。

## Options

`MapEdgeRenderOptions` は [`types`](./types.md) で定義する。
