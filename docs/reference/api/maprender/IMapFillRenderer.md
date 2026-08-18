# IMapFillRenderer

`IRaster` の値を色へ変換し、境界線なしの塗分け画像を生成するインタフェイス。

```python
class IMapFillRenderer(
    IMapRender[MapFillRenderOptions, ImageT],
    Protocol[ImageT],
):
    ...
```

`IMapFillRenderer` は `IMapRender` の `OptionsT` を `MapFillRenderOptions` に固定する。

```python
def render(
    self,
    reader: IWgsMapset3Reader,
    selector: IWgsMapset3Selector,
    options: MapFillRenderOptions | None = None,
) -> ImageT:
    ...
```

| 引数 | 内容 |
| --- | --- |
| `reader` | 描画元WGSMapSet/3 Reader |
| `selector` | 塗分け対象の矩形ラスタを読み出すSelector |
| `options` | 塗分け描画Options。`None` の場合は `defaultOptions` を使う |

塗分け規則は次の通り。

```text
value in colors
  -> colors[value]

otherwise
  -> defaultColor
```

`0` 値も通常の値と同じく `colors` で指定する。`0` 専用色が必要な場合は、`colors[0]` に色を設定する。

## Options

`MapFillRenderOptions` は [`types`](./types.md) で定義する。
