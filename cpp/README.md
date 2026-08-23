# Galuchat C++ port

- `src/galuchat`: プラットフォーム非依存のReaderとArduino FSアダプタ
- `src/Galuchat.h`: Arduinoライブラリの公開エントリポイント
- `platform/gcc`: PC向けサンプル
- `platform/arduino`: Arduino IDE/CLI向けサンプル
- `dev`: coreリポジトリ専用の検証コード（SDKには収録しない）

現在のPC向け入門サンプルは`platform/gcc/reverse-geocoding`です。

Arduino向けには、N03-20240101の1/100度版MapSetとGisWordBookを
`src/galuchat/data/n03_20240101_100_mapset.hpp`と
`src/galuchat/data/n03_20240101_wordbook.hpp`へ分けて収録しています。データは
`galuchat::data::n03_20240101_100`名前空間のFlash ROM用配列として参照できます。

`cpp`自体はArduinoライブラリとしてインストール可能です。一方、
`platform/arduino`の各スケッチは同じディレクトリにある転送ヘッダから`src`を参照するため、
ライブラリをインストールせずArduino IDEで`.ino`を直接開いてコンパイルできます。
GCC版も同じ`src/galuchat`を参照します。

## Readerの入力方式

WGSMap/3、WGSMapSet/3、GisWordBookのReaderは`ReaderFactory`を共有し、公開読出し
メソッドを呼ぶたびに独立した`ByteReader`を生成します。オンメモリ入力とファイル入力は
同じデコード経路を使います。

```cpp
// オンメモリ。bytesの寿命はreaderより長く保つ。
galuchat::GaluchatWGSMapSet3Reader memory_reader(bytes);

// ファイルを全量展開せず、8 KiBの固定長バッファで読む。
auto file_reader = galuchat::GaluchatWGSMapSet3Reader::fromFile(path, 8192);
auto wordbook = galuchat::GaluchatGisWordBookReader::fromFile(wordbook_path, 8192);
```

WGSMapSetとGisWordBookは地図チャンクや語彙ページの索引を保持せず、要求ごとに先頭から
順に走査します。したがってファイルサイズに比例する一時メモリは不要で、主要な作業領域は
ファイルバッファ、GI01デコーダ、結果ラスタ、WordBookのトークンキャッシュです。
トークンキャッシュの既定値は64件で、呼び出し側から変更または無効化できます。
`GaluchatImageDataChunk01Reader`自体は1回のシーケンシャル読出し専用ですが、上位Readerは
呼出しごとに再生成するため反復して利用できます。

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
