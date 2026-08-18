# Galuchat SDK 技術仕様

このディレクトリには、Galuchat GIS SDKに収録した実装とファイルを利用するための公開APIおよび現行ファイル形式仕様を収録する。

これらの文書は`galuchat-core`を正本としてSDK製造時に同期する。SDK側のコピーは直接編集しないこと。

## 公開API

- [言語共通API](api/README.md)
  - [Low-level API](api/lowlevel/README.md)
  - [Map Render API](api/maprender/README.md)

具体的なクラス名、配置方法、実行方法は、SDKに収録した各言語のGet Startedを参照する。

## 現行ファイル形式

- [WGSMap/3仕様](wgsmap3仕様書.md)
- [WGSMapSet/3仕様](wgsmapset3仕様書.md)
- [GI01仕様索引](GI01仕様索引.md)
- [WordBook格納仕様索引](wordbook/WordBookStorageIndex.md)
- [GisWordBook包括格納仕様](wordbook/GisWordBookStorageFormat.md)

旧形式、データセット製造仕様、実験レポートなど、SDKの利用に不要なcore内部文書は原則として収録しない。現行仕様から直接参照される補助仕様と設計資料だけは、リンクと定義の整合性を保つために含める。
