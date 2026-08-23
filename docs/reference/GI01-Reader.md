# GI01 Reader

## 1. 目的

GI01 Readerは、GI01データをDOM構造へ展開せず、入力バイト列を先頭から逐次走査しながら必要な画素だけを復元するための参照実装である。

主な想定環境は、GI01またはWGSMap/3をメモリ上のバイト列、組込機器のROM、またはファイルから読み、RAM上に大きな中間構造を作らずに復号するケースである。

現在のGI01実装は、GI00におけるDOM形式に近く、ブロックをNode構造へ復元してからラスタへ展開する。
Reader実装では、Node構造を作らず、必要範囲に関係しないノードやブロックを読み飛ばすことで、ワークメモリを数KB単位に抑えることを目標とする。

## 2. 基本方針

`GaluchatImageDataChunk01Reader`は、現在位置がGI01チャンク先頭にある`ABytesReader`を受け取り、前方向への逐次読み取りだけを行う。Reader内部ではseek、後方参照、入力Readerの再生成を行わない。

1個の`GaluchatImageDataChunk01Reader`で実行できる復号処理は、`readPoint`または`readRect`のいずれか1回だけである。複数回呼び出す必要がある場合は、呼び出し側がGI01チャンク先頭から新しいReaderを生成する。

WGSMap/3では`GaluchatWGSMap3Reader`が`ReaderFactory`を保持し、`readPoint`や`readRect`を呼ぶたびに独立した`ABytesReader`と`GaluchatImageDataChunk01Reader`を生成する。このため、WGSMap/3の公開Readerは反復読み取り可能だが、GI01 Reader自体は一回限りという責務分担になる。

WGSMapSet/3でも公開読出しごとに`ABytesReader`を1個だけ生成するが、チャンクごとの索引は保持しない。同じReaderでGI01チャンクを格納順に確認し、各チャンクの復号または末尾への読み飛ばしを繰り返す。これにより、読出し時間との引き換えに、ワークメモリをMap数に依存させない。

この方式は、対象ブロックの探索コストが増える一方で、次の利点を持つ。

* ブロック索引表をRAMへ展開しない。
* NodeツリーをRAMへ構築しない。
* 不要な子ノードは`skipToEnd`で読み飛ばす。
* 必要矩形だけを出力ラスタへ直接書き込む。
* ワークメモリ使用量を入力サイズやNode数に比例させない。

## 3. 対象API

`GaluchatImageDataChunk01Reader`は次の復号APIを持つ。

```
readPoint(x, y) -> int
readRect(x, y, dest: IWritableRaster) -> None
```

`readPoint`は1画素だけを復元する。
`readRect`は指定位置から`dest`と同じサイズの矩形を復元し、`dest`へ直接書き込む。
同じインスタンスに対して両方を呼び出したり、同じメソッドを複数回呼び出したりすることはできない。

`GaluchatWGSMap3Reader`はReaderを呼び出しごとに再生成するため、`readPoint`、`readRect`、`toRaster`を反復して利用できる。メモリ上のWGSMap/3は`fromBytes(bytes)`、ファイル上のWGSMap/3は`fromFile(path)`で生成する。

## 4. クラス構成

主なクラスは次の通りである。

| クラス | 役割 |
|---|---|
| `ABytesReader` | 前方向の逐次読み取り、相対位置、closeの共通インターフェース。 |
| `BytesBufferReader` | メモリ上のbytesを読むReader。生成時に起点offsetを指定できる。 |
| `FileBytesBufferedReader` | ローカルファイルを固定長バッファで読み、前方skipをseekで処理するReader。 |
| `ReaderFactory` | 指定offsetを起点とする独立した`ABytesReader`を生成する。 |
| `GaluchatWGSMap3Reader` | ReaderFactoryを保持し、公開読出しのたびにGI01復号セッションを作る。 |
| `GaluchatWGSMapSet3Reader` | チャンク索引を保持せず、公開読出しごとに1個のReaderでGI01列を逐次走査する。 |
| `GaluchatImageDataChunk01Reader` | GI01チャンクのヘッダとブロック列を、受け取ったReaderから一回だけ逐次読み出す。 |
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

`CC_RAWS`と`CC_LZSS`はBlockSizeを持つため、不要ブロックはNode構造や圧縮payloadを復号せずに読み飛ばせる。メモリReaderでは位置だけを進め、ローカルファイルReaderではseekできる。
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

GI01 Readerは一回限りであり、復号開始後に同じReaderをチャンク先頭へ戻すことはできない。反復読み取りは、WGSMap/3 ReaderがReaderFactoryから新しいReaderを生成することで実現する。

各復号セッションはGI01チャンク先頭から対象位置まで逐次走査する。このため、単一画素の反復読み取りでは呼び出しごとにReader生成と先行ブロックの走査が発生する。一方、ReaderやNodeツリーを長期間保持せず、入力サイズに比例するメモリ消費を避けられる。

Readerの所有期間は各公開読出し関数内で閉じ、処理の正常終了・異常終了にかかわらず`close`する。メモリReaderの`close`は何も行わず、ファイルReaderでは所有するファイルを閉じる。

WGSMapSet/3はチャンクoffsetや領域の配列をキャッシュしない。単一点では非0値が見つかるまで、矩形では合成順序を保つため最後まで、GI01列を先頭から確認する。メモリReaderのチャンクskipは位置更新だけであるが、前方向ファイルReaderでは対象byteの読み捨てが発生する。

GI01のBlockSizeを利用できる`CC_RAWS`と`CC_LZSS`では、不要ブロックのskipは高速である。
一方、`CC_RAW`はBlockSizeを持たないため、ノード構造を読みながらskipする必要がある。

ReaderはDOM実装と同じ復元結果を返さなければならない。
ただし、内部でNodeクラスを生成する必要はない。

## 12. 検証方針

Readerの変更では次を確認する。

1. `CC_RAW`、`CC_RAWS`、`CC_LZSS`の復元結果がメモリReaderとファイルReaderで一致すること。
2. 同じ`GaluchatWGSMap3Reader`から`readPoint`と`readRect`を反復して呼び出せること。
3. 同じ`GaluchatImageDataChunk01Reader`で2回目の復号を試みると失敗すること。
4. ファイルReaderが正常時と例外時のどちらでもcloseされること。
5. DOM実装の`toRaster`結果と一致すること。
6. WGSMapSet/3の点・矩形読出しがチャンク索引なしの逐次走査で同じ合成結果を返すこと。
