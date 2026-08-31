# Galuchat C++ port

- `src/galuchat`: Reader、標準ファイルI/O、Arduino FSアダプタ
- `data`: Arduinoサンプルで使用する組込み向けデータ
- `src/Galuchat.h`: Arduinoライブラリの公開エントリポイント
- `platform/gcc`: PC向けサンプル
- `platform/arduino`: Arduino IDE/CLI向けサンプル
- `dev`: coreリポジトリ専用の検証コード（SDKには収録しない）

現在のPC向け入門サンプルは`platform/gcc/reverse-geocoding`です。

`data`には、変換せずに直接インクルードできるFlash ROM用配列を収録しています。

| データ | 解像度 | 名前空間 | MapSet | WordBook |
| --- | ---: | --- | --- | --- |
| N03-20260101 | 1/1000度 | `galuchat::data::n03_20260101_1000` | `n03_20260101_1000_mapset.hpp` | `n03_20260101_wordbook.hpp` |
| geoBoundaries CGAZ | 1/100度 | `galuchat::data::geoboundaries_cgaz` | `geoboundaries_cgaz_100_mapset.hpp` | `geoboundaries_cgaz_wordbook.hpp` |

MapSetとWordBookのヘッダを同じ翻訳単位からインクルードして使用します。
geoBoundariesのMapSet変数名は`mapset_100`です。

`cpp`自体はArduinoライブラリとしてインストール可能です。一方、
`platform/arduino`の各スケッチは同じディレクトリにある転送ヘッダから`src`を参照するため、
ライブラリをインストールせずArduino IDEで`.ino`を直接開いてコンパイルできます。
GCC版も同じ`src/galuchat`を参照します。

## Readerの入力方式

WGSMap/3、WGSMapSet/3、GisWordBookのReaderは`ReaderFactory`を共有し、公開読出し
メソッドを呼ぶたびに独立した`ByteReader`を生成します。オンメモリ入力とファイル入力は
同じデコード経路を使います。

`ReaderFactory`は入力全体のサイズを要求しません。独自のストリームを接続する場合は、
`create(offset)`でReaderを再生成できることと、`ByteReader::atEnd()`で実際の終端を
判定できることだけが必要です。各チャンクの宣言サイズは境界付きReaderで検証されます。

```cpp
// オンメモリ。bytesの寿命はreaderより長く保つ。
galuchat::GaluchatWGSMapSet3Reader memory_reader(bytes);

// 標準ファイルを全量展開せず、8 KiBの固定長バッファで読む。
// この入力方式では galuchat/std_file_reader.hpp もインクルードする。
auto map_factory = std::make_shared<galuchat::FileReaderFactory>(path, 8192);
auto wordbook_factory = std::make_shared<galuchat::FileReaderFactory>(wordbook_path, 8192);
galuchat::GaluchatWGSMapSet3Reader file_reader(map_factory);
galuchat::GaluchatGisWordBookReader wordbook(wordbook_factory);
```

WGSMapSetとGisWordBookは地図チャンクや語彙ページの索引を保持せず、要求ごとに先頭から
順に走査します。したがってファイルサイズに比例する一時メモリは不要で、主要な作業領域は
ファイルバッファ、GI01デコーダ、結果ラスタ、WordBookのトークンキャッシュです。
トークンキャッシュの既定値は64件で、呼び出し側から変更または無効化できます。
`GaluchatImageDataChunk01Reader`自体は1回のシーケンシャル読出し専用ですが、上位Readerは
呼出しごとに再生成するため反復して利用できます。

厳格入力検証の単体テストは次のコマンドで実行できます。

```bash
g++ -std=c++17 -Wall -Wextra -pedantic -Icpp/src \
  cpp/dev/strict_input_validation_test.cpp \
  -o /tmp/galuchat-cpp-strict-input-test
/tmp/galuchat-cpp-strict-input-test
```

## WGSMapSetの矩形読み出し

`GaluchatWGSMapSet3Reader`は、複数のWGSMapを位置合わせし、値0を透過値として
指定矩形へ合成します。`RawRaster`を返すAPIのほか、呼び出し側が用意したバッファへ
直接読み出す`RasterView`を使用できます。後者はMapごとの一時ラスタを確保しません。

```cpp
#include <array>
#include <cstdint>

static std::array<uint16_t, 128 * 128> pixels{};
galuchat::RasterView<uint16_t> raster(128, 128, pixels.data());

// unit_inv_x/unit_inv_yで整数化したWGS座標を指定する。
galuchat::Rect target{13900, 3500, 128, 128};
mapset.readWgsRect(target, raster);
```

この例の出力バッファは32 KiBです。`uint16_t`を使う場合は、格納される地図値が
0..65535に収まるデータセットであることを呼び出し側で保証してください。値域が不明な
場合は`int64_t`を使用します。`toRaster()`はMapSet全体を確保するため、組込み用途では
使用せず、必要な矩形だけを`readWgsRect()`で読み出してください。
