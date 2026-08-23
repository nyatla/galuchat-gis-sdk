# Reverse geocoding example for Arduino

N03のMapSetとGisWordBookをファイルシステムへ置かず、C++配列としてFlash ROMへ組み込むサンプルです。
最初の対象は、FlashがメモリマップされるESP32系ボードです。

## 1. 収録データ

2024年1月1日時点、1/100度版のデータを共通`src`ディレクトリへ収録しています。
スケッチからはローカルの転送ヘッダを1つ読み込みます。

```cpp
#include "galuchat_bridge.hpp"
```

| 配列 | 元ファイル | サイズ |
| --- | --- | ---: |
| `galuchat::data::n03_20240101_100::mapset` | `N03-20240101-grid-512-100.remap.wgsmapset.glc` | 52,982 bytes |
| `galuchat::data::n03_20240101_100::wordbook` | `N03-20240101.giswordbook` | 31,922 bytes |

別の年度または解像度を組み込む場合は、バイナリファイルごとにROMヘッダを生成します。名前空間と配列変数名は必須です。

```sh
python3 make_rom_header.py \
  N03-20240101-grid-512-100.remap.wgsmapset.glc \
  --namespace my_n03_data \
  --variable mapset \
  --mode uint32-le \
  --literal shortest \
  --layout compact \
  --output my_n03_mapset.hpp

python3 make_rom_header.py \
  N03-20240101.giswordbook \
  --namespace my_n03_data \
  --variable wordbook \
  --mode uint32-le \
  --literal shortest \
  --layout compact \
  --output my_n03_wordbook.hpp
```

`--output`を省略した場合は、現在のディレクトリに`<変数名>.hpp`を生成します。上の例では、それぞれ次の配列とサイズ定数を定義します。

```cpp
my_n03_data::mapset
my_n03_data::mapset_size
my_n03_data::wordbook
my_n03_data::wordbook_size
```

任意のバイナリファイルを同じ方法で変換でき、MapSetとWordBookの組み合わせには限定されません。
外部には格納方式にかかわらず`const uint8_t*`と元のバイト数を公開します。

| オプション | 選択肢 | 既定値 |
| --- | --- | --- |
| `--mode` | `uint8`, `uint32-le`, `uint32-be` | `uint8` |
| `--literal` | `hex`, `decimal`, `shortest` | `hex` |
| `--layout` | `readable`, `compact`, `minified` | `readable` |

`uint32-le`と`uint32-be`は対象CPUのメモリエンディアンを指定します。末尾は内部で
4バイト境界までゼロ埋めしますが、`<変数名>_size`は元ファイルの正確なサイズです。
オンラインエミュレータへ貼り付ける場合は、上例の`uint32-le`、`shortest`、
`compact`の組み合わせを推奨します。`minified`はさらに空白を削りますが、巨大な
1行を生成します。

## 2. ビルド

Arduino IDEで`platform/arduino/reverse-geocoding/reverse-geocoding.ino`を直接開きます。
同じディレクトリの`galuchat_bridge.hpp`が共通実装と収録データを参照するため、
Galuchatライブラリの事前インストールや追加のインクルードパス指定は不要です。

Arduino CLIではリポジトリのルートから次のコマンドでコンパイルできます。

```sh
make -C cpp/platform/arduino reverse-geocoding
```

現在のReaderはC++17、STL、C++例外を使用します。ボード設定またはビルド設定でC++17と例外を有効にしてください。

## 3. 実行

シリアルモニタを115200bpsで開くと、最初に皇居付近の検索結果を表示します。その後は `lon lat>` に経度と緯度を空白区切りで送信すると、繰り返し検索できます。

```text
WGSMapSet metadata:
{"...":"...","approval":"測量法に基づく国土地理院長承認（使用）R 8JHs 319"}
code: 672
place: 東京都 / 千代田区
reversegeo: <elapsed> ms
wordbook: <elapsed> ms
lon lat>
```

検索座標は`reverse-geocoding.ino`の`LONGITUDE`と`LATITUDE`で変更できます。
表示時間は実行環境で変わります。Reader初期化時間は含みません。

## メモリ

- MapSet: 52,982 bytes
- GisWordBook: 31,922 bytes
- 合計: 84,904 bytes

データ本体はFlash ROMに置かれ、Readerへコピーしません。ReaderはMapSetやWordBookの
索引を保持せず、検索結果と復号状態、WordBookのトークンキャッシュにRAMを使用します。
