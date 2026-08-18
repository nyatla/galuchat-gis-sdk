# GI01 Reader

## 1. 目的

GI01 Readerは、GI01データをDOM構造へ展開せず、入力バイト列を先頭から逐次走査しながら必要な画素だけを復元するための参照実装である。

主な想定環境は、GI01またはWGSMap/3のバイト列を組込機器のROMへ直接配置し、RAM上に大きな中間構造を作らずに読み出すケースである。

現在のGI01実装は、GI00におけるDOM形式に近く、ブロックをNode構造へ復元してからラスタへ展開する。
Reader実装では、Node構造を作らず、必要範囲に関係しないノードやブロックを読み飛ばすことで、ワークメモリを数KB単位に抑えることを目標とする。

## 2. 基本方針

Readerは、入力バイト列をランダムアクセス可能なROM上の配列として扱う。
ただし、ノード単位では後方参照や索引表を作らず、対象ブロックへ到達するたびにチャンク先頭側から逐次読み直す方式を許容する。

この方式は、対象ブロックの探索コストが増える一方で、次の利点を持つ。

* ブロック索引表をRAMへ展開しない。
* NodeツリーをRAMへ構築しない。
* 不要な子ノードは`skipToEnd`で読み飛ばす。
* 必要矩形だけを出力ラスタへ直接書き込む。
* ワークメモリ使用量を入力サイズやNode数に比例させない。

## 3. 対象API

Readerは次のAPIを持つ。

```
readPoint(x, y) -> int
readRect(x, y, dest: IWritableRaster) -> IWritableRaster
toRaster() -> Raster
```

`readPoint`は1画素だけを復元する。
`readRect`は指定位置から`dest`と同じサイズの矩形を復元し、`dest`へ直接書き込む。
`toRaster`は全体を復元する補助APIであり、組込用途では必須ではない。

## 4. クラス構成案

実装は`src/galuchat/chunk/gi01/reader/`以下へ配置する。

想定クラスは次の通りである。

| クラス | 役割 |
|---|---|
| `GaluchatImageDataChunk01Reader` | GI01チャンク全体のReader。サイズ、square_unit、ブロック開始offsetを保持する。 |
| `BlockReader` | ブロック列を先頭から走査し、目的ブロックのNodeReaderを返す。 |
| `NodeReader` | Node Readerの抽象基底。`readPixel`、`readRect`、`skipToEnd`を定義する。 |
| `ContainerNodeReader` | ContainerNodeを逐次読みし、対象子以外をskipする。 |
| `RawNodeReader` | RawNodeを構造化せずに画素または矩形へ復元する。 |
| `RleNodeReader` | RleNodeを構造化せずに画素または矩形へ復元する。 |

## 5. ブロック読み取り

GI01のブロックは`BlockHeader`で始まる。

ReaderはBlockHeaderから次を判定する。

* `compressionType`
* `paletteDelta`

`compressionType`ごとの扱いは次の通りである。

| compressionType | 読み取り方針 |
|---|---|
| `CC_RAW` | BlockSizeがないため、NodeReaderで構造を読みながら必要範囲を復元またはskipする。 |
| `CC_RAWS` | BlockSizeを読み、不要ブロックはBlockSizeぶん読み飛ばす。必要ブロックはpayload範囲をReaderで読む。 |
| `CC_LZSS` | BlockSizeを読み、必要ブロックのみLZSSを逐次展開しながら読む。不要ブロックは圧縮payloadを読み飛ばす。 |

`CC_RAWS`と`CC_LZSS`はBlockSizeを持つため、不要ブロックのskipはO(1)に近い。
`CC_RAW`はBlockSizeを持たないため、ノード構造を逐次読んで末尾までskipする。

## 6. パレット状態

GI01ではカスケードパレットがブロック内で共有される。
そのため、不要ノードをskipする場合でも、パレット更新値は読み取り、Reader内の`PalletMgr`へ反映しなければならない。

Readerはブロックごとに`PalletMgr(16)`を作成する。
Container、Raw、RLEの各Readerは、`skipToEnd`でも通常読み取りと同じパレット更新処理を行う。

`paletteDelta=True`の場合、パレット更新値列は更新前スロット値との差分として記録される。
Readerは通常ReaderとDelta Readerを分けるか、パレット値読み取り関数だけを差し替える。

## 7. ContainerNode Reader

ContainerNode Readerは、CellHeaderと必要ならNodePalletを読み取る。

対象子が即値であれば、その値を直接返す、または対象矩形を塗りつぶす。
対象子がNodeであれば、子NodeReaderを生成して再帰的に読む。
対象外のNode子は、CellHeaderを読んだうえで対応するNodeReaderを作成し、`skipToEnd`で末尾まで読み飛ばす。

この方式により、目的画素または目的矩形に関係しないサブツリーをRAMへ展開しない。

## 8. RawNode Reader

RawNode Readerは、RawデータをNodeオブジェクト化しない。

画素単位読み取りでは、目的位置より前の値をskipし、目的値だけを読む。
矩形読み取りでは、行単位で不要部分をskipし、対象範囲だけを`dest`へ書き込む。

Raw/Pの場合は、先にパレット更新値列を読み取り、カスケードパレットを更新する。
その後、パレットインデックス列をbit単位で読み、必要位置だけ値へ変換する。

## 9. RleNode Reader

RleNode Readerは、RLEノードをラン長列とパレットインデックス列へ完全展開しない。

画素単位読み取りでは、走査順IndexMap上の目的位置に到達するまでランを読み進める。
矩形読み取りでは、ランの範囲と対象矩形の交差を判定し、交差する画素だけを`dest`へ書き込む。

ただし、GI01では複数のラン長エンコーディングが存在する。
ReaderはDataEncodingごとに、ラン長を1個ずつ逐次復元できる内部イテレータを持つ。

対象となるDataEncodingは次の通りである。

| DataEncoding | Reader方針 |
|---|---|
| `00` MBUInt | `readMbUInt`で1ランずつ読む。 |
| `01` ShortValueEncoding | 先頭の`run_count`を読み、末尾を除くtokenを逐次復号する。最後のランは画素数から復元する。 |
| `10` SingleEdgeRowEncoding | 先頭の`run_count`を読み、末尾を除くtokenを逐次復号する。MBUIntReduceではさらに`first`を読み、中間tokenを復号する。最後のランは画素数から復元する。 |

RLE/P3、RLE/P5、RLE/P16では、ラン長列の後にパレットインデックス差分列または即値列が続く。
ラン長列がbit streamの場合、Readerはラン長列末尾のbyte paddingを処理してから、後続のインデックス列を読む。

## 10. ワークメモリ

Readerのワークメモリは、原則として次の小さな状態に限定する。

* 現在のReader位置
* 現在ブロックの`PalletMgr`
* NodeReaderの再帰スタック
* RLEラン長tokenの小バッファ
* LZSS展開時の辞書バッファ

RLEラン長列全体、パレットインデックス列全体、Nodeツリー全体は保持しない。

## 11. 制約と注意点

Readerは低メモリを優先するため、同じ矩形を複数ブロックから読む場合、ブロック列を先頭から再走査する可能性がある。
これはCPU時間と引き換えにRAM使用量を削減する設計である。

GI01のBlockSizeを利用できる`CC_RAWS`と`CC_LZSS`では、不要ブロックのskipは高速である。
一方、`CC_RAW`はBlockSizeを持たないため、ノード構造を読みながらskipする必要がある。

ReaderはDOM実装と同じ復元結果を返さなければならない。
ただし、内部でNodeクラスを生成する必要はない。

## 12. 実装順序

実装は次の順序で進める。

1. `reader/`ディレクトリとReader基底クラスを作成する。
2. `BlockReader`で`CC_RAW`、`CC_RAWS`、`CC_LZSS`のブロック走査を実装する。
3. `ContainerNodeReader.skipToEnd`を実装する。
4. `RawNodeReader.skipToEnd`と`readRect`を実装する。
5. `RleNodeReader.skipToEnd`を実装する。
6. `readPoint`を実装する。
7. `readRect`を実装する。
8. DOM実装の`toRaster`結果と比較するテストを追加する。
