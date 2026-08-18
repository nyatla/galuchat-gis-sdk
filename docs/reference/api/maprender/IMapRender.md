# IMapRender

Map Render APIの共通基底インタフェイス。

`IMapRender` は、`IWgsMapset3Reader` と `IWgsMapset3Selector` と `Options` を受け取り、プラットフォーム依存の画像オブジェクトを返す。

```python
OptionsT = TypeVar("OptionsT")
ImageT = TypeVar("ImageT")

class IMapRender(Protocol[OptionsT, ImageT]):
    @property
    def defaultOptions(self) -> OptionsT:
        ...

    def render(
        self,
        reader: IWgsMapset3Reader,
        selector: IWgsMapset3Selector,
        options: OptionsT | None = None,
    ) -> ImageT:
        ...
```

| メンバ | 内容 |
| --- | --- |
| `defaultOptions` | `options` が `None` の場合に使用するデフォルトOptions |
| `render` | `selector` が読み出す矩形ラスタを `options` に従って画像化する |

`render` は内部で次の処理を行う。

```python
raster = selector.readRaster(reader)
```

`render` の出力画像サイズは、`selector.readRaster(reader)` が返す `IRaster.width` と `IRaster.height` に一致する。

`IRaster` の `y` は北方向を正とする。出力画像は north-up とし、画像の上端行は `raster.height - 1` に対応する。

## Options

`OptionsT` は派生インタフェイスごとに固定する。

```text
IMapEdgeRenderer
  -> MapEdgeRenderOptions

IMapFillRenderer
  -> MapFillRenderOptions

IMapImageRenderer
  -> MapImageRenderOptions
```

`options` が `None` の場合の処理は次の通り。

```python
effectiveOptions = options if options is not None else self.defaultOptions
```

## 出力画像

`ImageT` は実装環境の標準的なラスタ画像型である。

```text
Python -> PIL.Image.Image
Java   -> BufferedImage
JS     -> ImageData / Canvas / Blob など
```
