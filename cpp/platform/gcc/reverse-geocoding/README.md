# Reverse geocoding example for GCC

N03-20240101の1/1000度版WGSMapSetとGisWordBookを使い、経度・緯度から行政区域名を取得する最小構成のサンプルです。
2ファイルは全量をメモリへ読み込まず、4 KiBの固定長バッファを介して必要な部分を順次読み取ります。WordBookのトークンキャッシュも無効にしています。

Reader本体はArduinoライブラリと共通の`cpp/src/galuchat`にあり、Makefileが
`cpp/src`をインクルードパスへ追加します。

## Build

```sh
make
```

## Run

必要に応じてデータファイルを指定して起動します。

```sh
./reverse-geocoding \
  N03-20240101-grid-4096-1000.remap.wgsmapset.glc \
  N03-20240101.giswordbook
```

データファイルを実行ディレクトリへ置いた場合は、ファイル名を省略できます。

```sh
./reverse-geocoding
```

起動直後に皇居付近を検索します。その後は `lon lat>` に経度と緯度を空白区切りで入力すると、繰り返し検索できます。EOFで終了します。

出力例:

```text
sample: Imperial Palace
coordinate: 139.752800, 35.685200
code: 672
place: 東京都 / 千代田区
reversegeo: 6.236 ms
wordbook: 11.216 ms
lon lat> 135.5023 34.6937
coordinate: 135.502300, 34.693700
code: 1226
place: 大阪府 / 大阪市 / 北区
reversegeo: 8.184 ms
wordbook: 11.866 ms
lon lat>
```

時間は環境やファイルキャッシュ状態で変わります。`reversegeo` はWGSMapSet検索だけ、`wordbook` は地名復元だけの所要時間です。Reader初期化時間は含みません。

指定する座標は、経度、緯度の順です。N03の行政区域外にある座標では`not found`を返します。
