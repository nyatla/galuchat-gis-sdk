# File-based reverse geocoding example for Arduino

N03-20260101の1/1000度版WGSMapSetとGisWordBookをLittleFSから直接読み、経度・緯度から行政区域名を取得するサンプルです。ファイル全体をRAMへ展開せず、各読出しセッションで4 KiBの固定長バッファを使用します。

## データファイル

次の2ファイルをLittleFSのルートへ配置します。

```text
/N03-20260101-grid-4096-1000.remap.wgsmapset.glc
/N03-20260101.giswordbook
```

元ファイルはデータセットの次の場所にあります。

```text
dataset/国土地理院.行政区域データ.N03-20260101/build/N03-20260101-grid-4096-1000.remap.wgsmapset.glc
dataset/国土地理院.行政区域データ.N03-20260101/build/giswordbook/N03-20260101.giswordbook
```

ボードに応じたLittleFSアップロードツールを使用してください。MapSetは490,349 bytes、GisWordBookは31,922 bytesです。

## ビルド

Arduino IDEで`platform/arduino/reverse-geocoding-file/reverse-geocoding-file.ino`を
直接開きます。同じディレクトリの`galuchat_bridge.hpp`が共通ReaderとArduino FS
アダプタを参照するため、Galuchatライブラリの事前インストールや追加の
インクルードパス指定は不要です。

Arduino CLIではリポジトリのルートから次のコマンドでコンパイルできます。

```sh
make -C cpp/platform/arduino reverse-geocoding-file
```

ESP32系、C++17、C++例外を前提とします。シリアルモニタを115200 bpsで開くと、最初に皇居付近の検索結果を表示します。その後は `lon lat>` に経度と緯度を空白区切りで送信すると、繰り返し検索できます。

```text
WGSMapSet metadata:
{"...":"...","approval":"測量法に基づく国土地理院長承認（使用）R 8JHs 319"}
code: 672
place: 東京都 / 千代田区
reversegeo: <elapsed> ms
wordbook: <elapsed> ms
lon lat>
```

WordBookのトークンキャッシュはRAM節約のため無効にしています。ファイルバッファ量を変更する場合は `FILE_BUFFER_SIZE` を調整してください。
表示時間はReader初期化を含まず、`reversegeo` はWGSMapSet検索、`wordbook` は地名復元だけを計測します。
