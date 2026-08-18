# GisWordBook 包括格納仕様

## 1. 概要

`GisWordBook` は、順序付き階層地名リストを格納するための形式である。
`WordBook` の文字列辞書である `TT00`/`TM00` に、階層 index である `TI00` を追加する。

`GisWordBook` は、index 番号から次の値を復元できなければならない。

```text
index -> code_set
index -> string_set
```

`code_set` は、階層 component ごとの `WordBook.code` 配列である。
`string_set` は、`code_set` の各 code を `TT00`/`TM00` で復元した文字列配列である。

`index` は入力データの leaf 出現順に対応する。
地図画像や属性テーブルがこの `index` を参照する場合があるため、`GisWordBook` の生成処理は leaf の順序を変更してはならない。

## 2. 入力

入力は、`TI00` が対象とする順序付き階層地名リストである。
代表的な入力は `AddressComponentTree` コンテナである。

```json
{
  "type": "AddressComponents:1",
  "level": "ADM4",
  "depth": 4,
  "data": [
    [
      "都道府県",
      [
        [
          "市区町村",
          [
            [
              "地区名",
              [
                ["丁目番地"]
              ]
            ]
          ]
        ]
      ]
    ]
  ]
}
```

入力 tree の sibling 順序と leaf 出現順は、意味を持つデータとして扱う。
圧縮効率のために sibling や leaf を並べ替えてはならない。

## 3. 出力ファイル

`GisWordBook` は Galuchat の共通 `Chunk` 構造に従うチャンク列である。

```text
Chunk
  name: 4 bytes
  size: MBUInt
  data: byte[size]
```

必須チャンクは次の通りである。

```text
GisWordBook
  GisWordBookHeaderChunk: "GW00"
  TokenMapChunk:         "TM00"
  TextTableChunk:        "TT00"
  HierarchicalIndexChunk:"TI00"
```

`TM00` は token id から復元 byte 断片を得る辞書である。
`TT00` は `code -> text` の文字列テーブルであり、`TM00` の token id を参照する。
`TI00` は `index -> code_set` の階層 index であり、`TT00` の code を参照する。

チャンクは上記順序で格納する。
Reader は未知チャンクを無視してよいが、`TM00`、`TT00`、`TI00` がすべて存在しなければならない。

## 4. GisWordBookHeaderChunk

`GisWordBookHeaderChunk` は `GisWordBook` 全体のメタ情報を定義する。
チャンク名は `"GW00"` とする。
構成は WGSMapHeaderChunk と同じく、16 byte 固定長の version と metadata を持つ。

```text
GisWordBookHeaderChunk.data
  VERSION: BYTE[16]
  metadata_len: MBUInt
  metadata: byte[metadata_len]
```

| 項目 | 内容 |
| --- | --- |
| `VERSION` | 固定文字列。初期値は `"GisWordBook/0"` |
| `metadata_len` | metadata の byte 数 |
| `metadata` | UTF-8 metadata。長さ 0 なら省略 |

`VERSION` は 16 byte 固定長の BStr として格納する。
`"GisWordBook/0"` より後ろの未使用 byte は 0 で埋める。
`metadata` は任意であり、Reader は解釈しなくてもよい。

## 5. 生成手順

`GisWordBook` の生成は次の手順で行う。

1. 入力 tree を左から右へ走査し、全階層の component 文字列を収集する。
2. 収集した component 文字列から `TT00`/`TM00` を構築する。
3. 各 component 文字列を `TT00` の `code` に置換する。
4. 入力 tree の順序を維持したまま `TI00` の `IndexStream` を構築する。
5. `"GW00"`、`"TM00"`、`"TT00"`、`"TI00"` の順にチャンク列を書き出す。

`TT00`/`TM00` の内部では、文字列辞書の圧縮最適化を行ってよい。
ただし、`TI00` が参照する `code` と `TT00` record の対応は、出力時点で一貫していなければならない。

`TI00` の `IndexStream` は入力 leaf の出現順を保持しなければならない。
この制約により、`TI00` 生成時に leaf 順序を変えるブロック最適化やクラスタリングを行ってはならない。

## 6. チャンク間の参照

`TI00` は `TT00` の `code` だけを参照する。
`TI00` は文字列 byte 列も token id も直接持たない。

```text
TI00.code
  -> TT00.code
  -> TT00.RecordStream token id
  -> TM00.TokenPage token bytes
  -> UTF-8 text
```

`TI00.code_bits` は、`TT00.record_count` の全 code を表現できる bit 数でなければならない。

```text
TT00.record_count <= 2^TI00.code_bits
```

`TT00.token_bits` は、`TM00.token_count` の全 token id を表現できる bit 数でなければならない。

```text
TM00.token_count <= 2^TT00.token_bits
```

## 7. DOM

`GisWordBook` の DOM は、ビルド・変換・検証用の完全な中間表現である。
DOM は一時オブジェクトの生成を許容する。

```text
GisWordBookDom
  header: GisWordBookHeaderChunk
  token_map: TM00TokenMapChunk
  text_table: TT00TextTableChunk
  index: TI00HierarchicalIndexChunk
```

DOM は次の責務を持つ。

- 入力 tree から component 文字列集合を作る。
- `TT00`/`TM00` の構築と最適化を行う。
- 入力 tree を code tree へ変換する。
- `TI00` を構築する。
- チャンク列として serialize する。
- `TT00`、`TM00`、`TI00` の参照整合性を検証する。

DOM は Reader の実装要件ではない。
組込用途の Reader は DOM を復元してはならない。

## 8. Reader

`GisWordBookReader` は組込用途を想定し、入力は `bytes` のみとする。
抽象 stream reader や `Chunk.unpack()` によるチャンク data コピーを必須にしてはならない。

Reader は、初期化時に元 `bytes` を保持し、チャンクヘッダを走査して各チャンクの `data_start` と `size` を記録する。

```text
MappedChunk
  name
  data_start
  size
```

Reader は `TM00`、`TT00`、`TI00` の page/header metadata だけを保持してよい。
token、text、code_set、string_set を全件展開してはならない。

```text
GisWordBookReader
  src: bytes
  tm_reader: TM00ChunkReader
  tt_reader: TT00ChunkReader
  ti_reader: TI00ChunkReader
```

各 chunk reader は、元 `bytes` と chunk data 範囲を参照する。
読み出し時は `BytesBufferReader(src, offset=...)` を使い、必要な stream 範囲だけを読む。

## 9. Reader API

Reader は、少なくとも次の操作を提供する。

```text
recordCount() -> int
depth() -> int
readCodeSet(index: int, out: list[int] | None = None) -> list[int]
readStringSet(index: int, out: list[str] | None = None) -> list[str]
readComponent(code: int) -> str
```

組込用途では、呼び出し側が `out` を渡せる API を提供する。
`out` が渡された場合、Reader は既存配列を再利用し、新しい配列を作らない。

より低レベルな API として、文字列を直接返さず、呼び出し側の sink に UTF-8 byte 断片を流し込む操作を提供してよい。

```text
readComponentBytes(code: int, sink) -> None
readStringSetBytes(index: int, sink) -> None
```

この場合、Reader は component 文字列の中間 `bytes` オブジェクトを作らず、`TM00.TokenStream` の slice 範囲を順に sink へ渡す。

## 10. 一時オブジェクト抑制

Reader は次の方針で一時オブジェクトを抑制する。

- `Chunk.unpack()` を使わず、チャンク data を元 `bytes` 上の offset/size として扱う。
- `TM00` token table を `bytes[]` へ展開しない。
- `TT00` text table を `str[]` へ展開しない。
- `TI00` code_set table を `list[list[int]]` へ展開しない。
- `BytesBufferReader` は chunk reader 内で再利用可能な作業 reader として保持してよい。
- `readCodeSet(index, out)` は `out` を上書きして返す。
- `readStringSet(index, out)` は必要な component だけを復元する。

ただし、Python 実装では `str` を返す API は文字列オブジェクトを生成する。
完全に一時オブジェクトを避けたい場合は、byte sink API を使う。

## 11. ランダムアクセス

`TI00` は `leaf_count` により、対象 index が container/block 内に含まれるかを判定する。

`PrefixContainer.payload_bits > 0` の場合、対象外 container の `ChildPayload` は `skipBits(payload_bits)` で飛ばせる。
`payload_bits == 0` の場合、Reader は `leaf_count` 個の leaf record が復元されるまで子要素を線形走査する。

`TT00` は page 単位で `RecordStream` を持つ。
対象外 page は `record_stream_size` で byte skip できる。

`TM00` は token byte 長ごとの `TokenPage` を持つ。
対象 token page が決まった後は、page 内 token を走査せず、乗算で byte offset を計算する。

## 12. 制約

- `GW00`、`TM00`、`TT00`、`TI00` はすべて存在しなければならない。
- `TI00.record_count` は `GisWordBookReader.recordCount()` の値である。
- `TI00.max_depth` は `GisWordBookReader.depth()` の値である。
- `TI00.code` は `0 <= code < TT00.record_count` を満たさなければならない。
- `TT00` が参照する token id は `0 <= token_id < TM00.token_count` を満たさなければならない。
- 入力 tree の leaf 出現順と `TI00` の index 順は一致しなければならない。
- Reader は、読み出しのために DOM を構築してはならない。

## 13. 未決定事項

- `GW00` を必須ヘッダとして維持するか、`TM00`/`TT00`/`TI00` だけの最小チャンク列を許容するか。
- `TI00.payload_bits` を常に書くか、サイズ削減のために一部 `0` を許容するかの生成ポリシー。
- `readStringSetBytes` の sink インターフェイスを Python/JavaScript/Java でどう揃えるか。
