# IMapImageRenderer

塗分け画像と境界線画像を組み合わせて地図画像を生成する統合レンダラインタフェイス。

```python
class IMapImageRenderer(
    IMapRender[MapImageRenderOptions, ImageT],
    Protocol[ImageT],
):
    ...
```

`IMapImageRenderer` は `IMapRender` の `OptionsT` を `MapImageRenderOptions` に固定する。

```python
def render(
    self,
    reader: IWgsMapset3Reader,
    selector: IWgsMapset3Selector,
    options: MapImageRenderOptions | None = None,
) -> ImageT:
    ...
```

| 引数 | 内容 |
| --- | --- |
| `reader` | 描画元WGSMapSet/3 Reader |
| `selector` | 地図画像生成対象の矩形ラスタを読み出すSelector |
| `options` | 地図画像描画Options。`None` の場合は `defaultOptions` を使う |

`MapImageRenderOptions.edgeOptions` が `None` の場合は境界線を描画しない。

`MapImageRenderOptions.edgeOptions` が指定された場合は、次の処理と同等の結果を返す。

```text
fill = fillRenderer.render(reader, selector, options.fillOptions)
edge = edgeRenderer.render(reader, selector, options.edgeOptions)
image = overlay(fill, edge)
```

## Options

`MapImageRenderOptions` は [`types`](./types.md) で定義する。
