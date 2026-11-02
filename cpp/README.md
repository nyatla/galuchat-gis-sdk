# Galuchat C++ port

- `src/galuchat`: Reader、標準ファイルI/O、Arduino FSアダプタ
- `data`: Arduinoサンプルで使用する組込み向けデータ
- `src/Galuchat.h`: Arduinoライブラリの公開エントリポイント
- `platform/gcc`: PC向けサンプル
- `platform/arduino`: Arduino IDE/CLI向けサンプル
- `dev`: coreリポジトリ専用の検証コード（SDKには収録しない）
- `tests`: SDKにも同梱するReaderの互換性・索引・末尾走査省略の回帰テスト

現在のPC向け入門サンプルは`platform/gcc/reverse-geocoding`です。

`data`には、変換せずに直接インクルードできるFlash ROM用配列を収録しています。

| データ | 解像度 | 名前空間 | MapSet | WordBook |
| --- | ---: | --- | --- | --- |
| N03-20260101 | 1/1000度 | `galuchat::data::n03_20260101_1000` | `n03_20260101_1000_mapset.hpp` | `n03_20260101_wordbook.hpp` |

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

## 索引方式を明示的に選ぶC++ Reader

`GaluchatWGSMapSet3Reader`は従来どおり、各Mapの原点座標だけを保持し、取得要求ごとに
同じ入力ストリームでチャンクを順次走査します。既存のコンストラクタ、読出し経路、
保持情報は変更していません。チャンク位置索引やチャンク数制限を標準動作には追加しません。

索引方式を使う場合は、別クラス`GaluchatWGSMapSet3IndexedReader`を明示的に選択します。
直接使用する場合のヘッダは`galuchat/wgsmapset3_indexed_reader.hpp`です。
Arduino向けの公開エントリポイント`Galuchat.h`からも参照できます。

```cpp
#include "galuchat/wgsmapset3_indexed_reader.hpp"

// 従来方式: 原点座標だけを保持し、順次走査する。
galuchat::GaluchatWGSMapSet3Reader sequential(map_factory);

// 索引方式: 座標・寸法・ファイル位置を保持する。上限は1500チャンク。
galuchat::GaluchatWGSMapSet3IndexedReader indexed(map_factory, 1500);
```

索引クラスは初期化時に各GI01のヘッダを読み、原点座標・寸法・ファイル開始位置を保持します。
矩形取得ではRAM上で交差を判定し、必要なチャンクだけを独立したReaderで開きます。
地図データの全量展開、SDへの索引ファイルの生成、ブロック位置索引の作成は行いません。

32bit環境で保持情報は従来クラスが1チャンク8バイト、索引クラスが20バイトです。
索引クラスは両方の配列を保持する構成ではありません。配列の管理領域などは別途必要です。

索引クラスのコンストラクタは、従来クラスと同じvector・ポインタ＋サイズ・ReaderFactoryの
入力方式に対応し、最後に省略可能な`max_maps`を受け取ります。上限は指定値を含み、
既定値は`size_t`の最大値です。上限超過は原点配列の確保と原点列・GI01の走査より前に
`MapCountLimitExceeded`を送出します。例外の`count`と`limit`で実数と上限を確認できます。

索引クラスの`readWgsRect()`は、必要チャンクを開いた後、そのチャンクの末尾まで従来と
同じ復号・スキップ・全体長検証を行います。`readWgsRectf()`、`readRect()`、`toRaster()`も
この経路を使用します。点取得`readWgsPoint()`は先頭からの順次走査を維持しており、
索引で高速化するのは矩形取得です。正常データでは、従来クラスと取得画素・値0の透過合成・
重複時の優先順が一致します。

### 末尾走査を省くC++ API

必要範囲より後ろのブロック走査を省く場合は、追加APIを明示的に選択します。

```cpp
// 索引クラス: 呼び出し側のバッファへ取得する。
indexed.readWgsRectWithoutTail(target, raster);

// 索引クラス: 結果をRawRasterで受け取る。
auto result = indexed.readWgsRectWithoutTail(target);

// GI01: チャンク内の座標で取得する。
chunk.readRectWithoutTail(x, y, raster);
```

上位の`readWgsRectWithoutTail()`は索引クラス専用です。従来クラスには追加していません。
GI01の既存`readRect()`は、全ブロックの復号またはスキップと宣言ペイロード長の一致の
検証を維持します。正常終了後は同じ入力ストリームから次のチャンクを読み出せます。

追加APIはブロック順に先頭から読み進め、最後に必要なブロックの処理を完了した時点で
停止します。それより前の不要ブロックは従来どおりスキップします。必要ブロック内部の
復号、パレット状態の処理、バイト境界への整列、RAWS・LZSSの終端検証は省きません。
正常データの取得画素は既存APIと一致し、追加の画像キャッシュやブロック索引は確保しません。

後続ブロックとGI01全体のペイロード長の一致は検証しません。取得範囲が全ブロックに及ぶ
場合も、この全体長の検証は行いません。既存APIも、スキップ対象の圧縮ブロックの内容までは
復号・検証しないため、いずれのAPIもファイル全体の完全性検証を目的とするものではありません。

GI01の追加APIは正常終了時に入力をバイト境界へ揃えますが、次のチャンクの先頭まで進める
保証はありません。交差するブロックがなければヘッダ直後で終了します。低レベルAPIの
部分的な端ブロックの扱いは従来どおりで、画像寸法をブロック境界まで広げた領域を扱います。
GI01 Readerは追加APIでも1回限りの利用です。同じストリームで次のチャンクを読みたい場合は
明示的に`skipToEnd()`を呼べますが、この移動は残りのブロック構造を検証しません。

索引クラスの末尾走査なしの取得では、チャンクごとのReaderを末尾までスキップせず破棄します。
入力バッファによる先読みがあるため、論理的な停止位置より先のバイトがファイルI/Oで
読み込まれる場合はあります。これらの追加はC++版のみで、他言語版は変更していません。

### SDKの検証

リポジトリのルートで次を実行します。

```bash
g++ -std=c++17 -Wall -Wextra -Werror -pedantic -Icpp/src \
  cpp/tests/rect_without_tail_test.cpp -o /tmp/galuchat-rect-without-tail-test
/tmp/galuchat-rect-without-tail-test

g++ -std=c++17 -Wall -Wextra -Werror -pedantic -Icpp/src \
  cpp/tests/sequential_reader_compatibility_test.cpp -o /tmp/galuchat-sequential-compatibility-test
/tmp/galuchat-sequential-compatibility-test
```

前者は取得画素・停止位置・入力検証・合成・索引クラスの上限判定を検証します。
後者はSDKリポジトリ（`galuchat-gis-sdk`）の索引導入前コミット`de0258a`から採取した操作記録と比較し、従来クラスのReader生成・
読出し・スキップ・位置照会・終端判定・破棄、取得結果とエラーの一致を確認します。
LAYOの有無、複数チャンク、範囲外・空矩形、点取得、不正な末尾を含めた記録です。
