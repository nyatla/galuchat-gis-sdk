# WordBook 包括格納仕様

## 1. 概要

`WordBook` は、内部コード `code` から全角文字列 `text` を引くための格納形式である。

`WordBook` は、ヘッダ情報と 2 つのデータチャンクを包括する。

```text
WordBook
  WordBookHeaderChunk: "NM00"
  TokenMapChunk:      "TM00"
  TextTableChunk:     "TT00"
```

`TM00` は token id から復元 byte 断片を得る辞書である。
`TT00` は `code -> text` の本体であり、`TM00` の token id を参照する。

各チャンクは Galuchat の共通 `Chunk` 構造に従う。

```text
Chunk
  name: 4 bytes
  size: MBUInt
  data: byte[size]
```

本仕様で説明する整数値は、特に明記しない限り MBUInt で格納する。

## 2. 入力と内部コード

入力データは次の形を想定する。

```text
id,text
1,一丁目
2,二丁目
3,三丁目
...
```

入力データセットの `id` は `WordBook` 内には格納しない。
外部に固定された id ではなく、ファイル内で一意な `code` を生成して使う。

```text
code = physical_row_index
page = first TT00.Page where cumulative page_record_count contains code
index_in_page = code - cumulative_record_count_before_page
```

`code` は record の物理配置そのものである。
生成時に record を圧縮効率優先で並べ替え、その並び順に `0..record_count-1` の `code` を割り当てる。
外部が文字列から `code` を得るための検索構造は、`WordBook` の必須要素には含めない。

## 3. WordBookHeaderChunk

`WordBookHeaderChunk` は WordBook 全体のメタ情報を定義する。
チャンク名は `"NM00"` とする。
構成は WGSMapHeaderChunk と同じく、16 byte 固定長の version と metadata を持つ。

```text
WordBookHeaderChunk.data
  VERSION: BYTE[16]
  metadata_len: MBUInt
  metadata: byte[metadata_len]
```

| 項目 | 内容 |
| --- | --- |
| `VERSION` | 固定文字列。初期値は `"WordBook/0"` |
| `metadata_len` | metadata の byte 数 |
| `metadata` | UTF-8 metadata。長さ 0 なら省略 |

`VERSION` は 16 byte 固定長の BStr として格納する。
`"WordBook/0"` より後ろの未使用 byte は 0 で埋める。
`metadata` は任意であり、Reader は解釈しなくてもよい。

`WordBook` の格納方式は固定とする。`flags` は持たない。

## 4. チャンク間の関係

`WordBookHeaderChunk` は WordBook 全体の version と metadata だけを保持する。
token の実体は `TM00`、文字列本体と page 構成は `TT00` に分離する。
`TM00` も token byte 長ごとの `TokenPage` を持ち、`global_token_id` から token byte 列を復元する。
`TT00` の palette packet 内の `global_token_id` bit 幅は `TT00.token_bits` で決まる。
`TT00.token_bits` は `TM00.token_count` を表現できる最小 bit 数を選択する。

```text
TT00.token_bits
  -> TT00 の palette packet 内 global_token_id 幅に使う

TT00.palette global_token_id
  -> TM00.TokenPage[] 内の token bytes を参照する
```

`record_count`, `page_size`, `page_count`, `token_bits` は `TT00` が保持する。
`NM00` には重複して持たない。

`TM00` と `TT00` の詳細は、それぞれ `TM00TokenMapChunk.md` と `TT00TextTableChunk.md` に定義する。

## 5. 読み出し手順

`code` から `text` を取り出す流れは次の通り。

```text
read NM00
read TM00
read TT00

for page in TT00.Page[]:
  if code < cumulative_record_count + page.page_record_count:
    index_in_page = code - cumulative_record_count
    read this page
    break
  skip page.RecordStream by page.record_stream_size
  cumulative_record_count += page.page_record_count

skip records before index_in_page
decode target record using TM00
```

オンメモリ Reader は、ファイル等から読み出した WordBook byte 列を保持し、チャンクヘッダだけを走査して `data_start` と `size` を記録する。
この用途では `Chunk.unpack(reader)` を使わない。
`Chunk.unpack(reader)` は `chunk.data` を `bytes` として切り出すため、チャンク単位のコピーが発生する。

```text
MappedChunk
  name
  data_start
  size
```

`TM00` と `TT00` の内部も同じ方針で、`TokenStream` と `RecordStream` は元 byte 列上の offset/size として保持する。
Reader は `read(code)` の時だけ `BytesBufferReader(src, offset=...)` を作り、対象 stream を読む。
Reader の入力は `bytes` とし、抽象的な stream reader は受け取らない。

`TT00` の page は record の構成 token 数ごとに分割する。
各構成 token 数 group の内部では、palette 更新回数を減らすために page 順序最適化を行ってよい。
`Page[]` は `record_token_count` 昇順に配置し、各 page は自身の `record_token_count` を保持する。
そのため `TokenCountGroupIndex` と `PageIndex` は持たない。

対象 page の探索は全 record 走査ではなく、page header の線形走査で行う。
対象外 page の `RecordStream` は `record_stream_size` で byte skip できる。

現行の `RecordStream` では、Page 内の skip は record terminator を数えて対象 record の開始位置を求める。
固定長 payload encoding を使う場合は、`record_token_count` から対象 record の開始位置を直接計算できる。

高速化が必要なら、`TT00` の `RecordStream` に record offset marker を追加する。
ただし offset 表はサイズが増えるため、初期フォーマットでは必須にしない。

`TM00` は token byte 長ごとの page を持つため、Reader は token table を `bytes[]` に展開せずに読める。
展開しない Reader は `TM00.data` と `TokenPage` の offset metadata だけを保持し、`TT00` が参照した `global_token_id` だけを `TokenStream` から切り出す。
頻出 token の再切り出しを避けるため、実装は小さな token LRU cache を持ってよい。

## 6. 未決定事項

- `WordBook` を単独ファイルとして扱うか、WGSMap 系コンテナ内の追加チャンク列として扱うか。
- 文字列から `code` を得るための検索構造を別チャンクとして持つか、外部で管理するか。
- `TT00` の page 内 skip を terminator scan だけで行うか、任意で offset marker を持つか。
