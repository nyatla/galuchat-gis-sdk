# Map Render API

[APIドキュメント](../README.md) / [ドキュメント索引](../../README.md)

## 目的

この文書は、`IWgsMapset3Reader` から矩形ラスタを読み出し、プラットフォーム依存の地図画像を生成するAPIを定義する。

地図画像生成は、低レベルReader APIとは分離する。低レベルReader APIは [`../lowlevel`](../lowlevel/README.md) で定義する。

Map Render APIは、次の3つを組み合わせて画像を生成する。

- `IWgsMapset3Reader`: WGSMapSet/3 の読出しと座標変換
- `IWgsMapset3Selector`: `IWgsMapset3Reader` からどの矩形ラスタを読むか
- `Options`: 読み出した矩形ラスタをどのように描画するか

レンダラは [`IMapRender`](./IMapRender.md) を基底インタフェイスとし、各描画バリエーションは `Options` 型を固定した派生インタフェイスとして定義する。

## インタフェイス

- [`IMapRender`](./IMapRender.md)
- [`IWgsMapset3Selector`](./IWgsMapset3Selector.md)
- [`IMapFillRenderer`](./IMapFillRenderer.md)
- [`IMapEdgeRenderer`](./IMapEdgeRenderer.md)
- [`IMapImageRenderer`](./IMapImageRenderer.md)

共通型とOptionsは [`types`](./types.md) で定義する。

## Python実装

Python APIでは、Pillowの `PIL.Image.Image` を返す具体実装を提供する。

```python
from galuchat.api.maprender import (
    PilMapEdgeRenderer,
    PilMapFillRenderer,
    PilMapImageRenderer,
)
```

| クラス | 内容 |
| --- | --- |
| `PilMapFillRenderer` | `IRaster` の値を色へ変換した塗分け画像を生成する |
| `PilMapEdgeRenderer` | `IRaster` の値境界から境界線画像を生成する |
| `PilMapImageRenderer` | 塗分け画像に境界線画像を重ねた地図画像を生成する |

## 基本形

```python
image = renderer.render(
    reader,
    selector,
    options,
)
```

`selector` は `reader` から切り出す矩形ラスタを決定する。`options` は描画方法を決定する。

`options` に `None` を指定した場合、レンダラは自身の `defaultOptions` を使用する。

Selectorには、ピクセル座標基点、LonLat基準点、LonLat境界、WGSMapSet全体などのバリエーションを定義できる。
