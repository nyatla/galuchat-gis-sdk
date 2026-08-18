# Galuchat API ドキュメント

[ドキュメント索引](../README.md)

アプリケーション向けAPIは、Readerの基本操作と画像描画を分離して定義する。

## Low-level API

[Low-level API](lowlevel/README.md)は、WGSMapSet/3とGisWordBookを読み取るための最小インタフェイスを定義する。

- [IWgsMapset3Reader](lowlevel/IWgsMapset3Reader.md)
- [IWordBookReader](lowlevel/IWordBookReader.md)

## Map Render API

[Map Render API](maprender/README.md)は、Readerから矩形ラスタを取得し、プラットフォームの画像型へ描画するインタフェイスを定義する。

- [IMapRender](maprender/IMapRender.md)
- [IWgsMapset3Selector](maprender/IWgsMapset3Selector.md)
- [IMapFillRenderer](maprender/IMapFillRenderer.md)
- [IMapEdgeRenderer](maprender/IMapEdgeRenderer.md)
- [IMapImageRenderer](maprender/IMapImageRenderer.md)
- [共通型とOptions](maprender/types.md)

