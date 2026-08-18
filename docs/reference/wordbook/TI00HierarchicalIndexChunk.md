# TI00 HierarchicalIndex チャンク仕様

## 1. 概要

`TI00` は、固定深度の階層地名 index を prefix 圧縮して格納するチャンクである。

`TI00` は、index 番号から次の値を復元できなければならない。

```text
index -> code_set
index -> string_set
```

`code_set` は、階層 component ごとの `WordBook.code` 配列である。
`string_set` は、`code_set` の各 code を `TT00`/`TM00` で復元した文字列配列である。

`TI00` は文字列そのものを持たない。
全 component 文字列は、同じ `WordBook` 内の `TT00`/`TM00` に格納する。

対象入力は、`AddressComponentTree` のような階層化済み構造化データである。

```json
{
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

変換手順は次の通りである。

1. `data` tree の全 node name から、全階層の component 文字列を統合した `WordBook` を作成する。
2. 各 node name を `WordBook.code` に置換する。
3. `data` tree を左から右へ DFS preorder で走査し、共通 prefix を `PrefixContainer`、末端列を `LeafBlock` として格納する。

`TI00` 生成時に、`data` tree の兄弟 node の出現順序を変更してはならない。
復元される index 番号は、`data` tree を左から右へ DFS preorder で走査した時の leaf 出現順と一致しなければならない。

```text
Chunk
  name: 4 bytes = "TI00"
  size: MBUInt
  data: byte[size]
```

## 2. データ構造

```text
HierarchicalIndexChunk.data
  max_depth: MBUInt
  record_count: MBUInt
  code_bits: MBUInt
  root_count: MBUInt
  stream_size: MBUInt
  IndexStream: byte[stream_size]
```

| 項目 | 内容 |
| --- | --- |
| `max_depth` | `code_set` の固定要素数 |
| `record_count` | index 数 |
| `code_bits` | `WordBook.code` の固定 bit 幅 |
| `root_count` | root 階層の要素数 |
| `stream_size` | `IndexStream` の byte 数 |
| `IndexStream` | `PrefixContainer` と `LeafBlock` の階層列 |

`max_depth` は `1` 以上でなければならない。
`record_count` は、`IndexStream` の走査で生成される record 数と一致しなければならない。
`code_bits` は `1` 以上で、参照対象 `TT00.record_count` の全 code を表現できなければならない。

```text
TT00.record_count <= 2^code_bits
```

## 3. IndexStream

`IndexStream` は bit stream である。
`PrefixContainer` と `LeafBlock` は byte 境界から開始する必要はない。
`IndexStream` 全体は、`HierarchicalIndexChunk.data` に byte 列として格納するため、末尾だけを 0 bit で padding して byte 境界で終了する。

`IndexStream` 内の `MBUInt` は、現在の bit 位置から論理 8bit 単位で読み書きする。
このため、`MBUInt` 自体も byte 境界から開始する必要はない。

`IndexStream` に container type と depth は持たない。
Reader は現在の `depth` から次に読む要素型を決定する。

```text
if max_depth == 1:
  LeafBlock
else if depth < max_depth - 1:
  PrefixContainer
else:
  LeafBlock
```

通常、`max_depth > 1` の場合、root 要素は `PrefixContainer` である。
`max_depth == 1` の場合、root 要素は `LeafBlock` である。

## 4. PrefixContainer

`PrefixContainer` は、現在 depth の component code と、その prefix 配下の child 要素列を表す。

```text
PrefixContainer
  code: bit[code_bits]
  leaf_count: MBUInt
  payload_bits: MBUInt
  ChildPayload: bit[payload_bits] if payload_bits > 0
              variable-length child stream if payload_bits == 0
```

| 項目 | 内容 |
| --- | --- |
| `code` | 現在 depth の component の `WordBook.code` |
| `leaf_count` | この prefix 配下から復元される record 数 |
| `payload_bits` | `ChildPayload` の bit 数。`0` の場合は不明 |
| `ChildPayload` | 次 depth の `PrefixContainer` 又は `LeafBlock` の連結 bit 列 |

`code` は `code_bits` bit で格納する。
`leaf_count` と `payload_bits` は、`code` の直後の bit 位置から MBUInt で格納する。

`leaf_count` は `1` 以上でなければならない。
`payload_bits` は `0` 以上でなければならない。

`depth < max_depth - 2` の場合、`ChildPayload` は `PrefixContainer` 列である。
`depth == max_depth - 2` の場合、`ChildPayload` は `LeafBlock` 列である。
`payload_bits > 0` の場合、Reader は `payload_bits` から `ChildPayload` の終端 bit 位置を計算し、終端まで child 要素を読み続ける。
対象 index がこの container の範囲外であれば、`payload_bits` bit を読み飛ばして次の兄弟要素へ進むことができる。

`payload_bits == 0` の場合、`ChildPayload` の bit 数は記録されない。
Reader は `leaf_count` 個の leaf record が復元されるまで `ChildPayload` を線形に走査しなければならない。
この場合、対象 index が container の範囲外であっても、`ChildPayload` 全体を定数時間で skip することはできない。

## 5. LeafBlock

`LeafBlock` は、末端 depth の component code 列をまとめて格納する。

```text
LeafBlock
  leaf_count: MBUInt
  codes: bit[leaf_count * code_bits]
```

| 項目 | 内容 |
| --- | --- |
| `leaf_count` | この block に含まれる leaf record 数 |
| `codes` | 末端 component の `WordBook.code` 列 |

`codes` は `code_bits` bit 幅で連続して格納する。
`LeafBlock` の直後に兄弟要素が続く場合、次の要素は `codes` の直後の bit 位置から始まる。

`LeafBlock.leaf_count` は `1` 以上でなければならない。

## 6. 状態機械

`TI00` の Reader は、`IndexStream` を先頭から読み、index 番号順に record を返す iterator として振る舞う。

状態機械は次の変数を持つ。

```text
emitted: int = 0
slot: code[max_depth]
```

`slot` は現在の path の `WordBook.code` を保持する。

### PrefixContainer 処理

```text
read PrefixContainer at depth
slot[depth] = container.code

for child in container.ChildPayload:
  read child at depth + 1
```

`PrefixContainer.leaf_count` は、`ChildPayload` を走査して生成される leaf record 数と一致しなければならない。

### LeafBlock 処理

```text
read LeafBlock at depth = max_depth - 1

for code in LeafBlock.codes:
  slot[max_depth - 1] = code
  emit code_set(emitted, slot[0..max_depth-1])
  emitted += 1
```

`LeafBlock` の各 code は、入力 tree の leaf 出現順に並ばなければならない。

## 7. index からの復元

index `k` の `code_set` を得るには、`IndexStream` を先頭から走査し、`emitted <= k < emitted + leaf_count` を満たす container/block だけを辿る。

`LeafBlock` では、block 内 offset を計算して対象 code だけを読む。

```text
offset = k - emitted
leaf_code = LeafBlock.codes[offset]
return slot[0..max_depth-2] + [leaf_code]
```

`string_set` は、得られた `code_set` の各 code を `WordBook` で復元して得る。

```text
code_set = TI00.readCodeSet(index)
string_set = [WordBook.read(code) for code in code_set]
```

この仕様は、`leaf_count` による簡易な計算で対象 index が container/block 内に含まれるかを判定できることを必須とする。
対象外の `PrefixContainer` は、`payload_bits > 0` の場合に限り `ChildPayload` 全体を bit skip できる。
`payload_bits == 0` の場合は、`leaf_count` に基づいて子要素を線形走査して読み飛ばす。

## 8. 復元例

次の component 階層を考える。

```text
北海道
  札幌市中央区
    宮の森一条
      一丁目
      二丁目
    円山
      ""
```

`max_depth = 4` の `IndexStream` は次の構造になる。

```text
PrefixContainer(code=北海道, leaf_count=3, payload_bits=...)
  PrefixContainer(code=札幌市中央区, leaf_count=3, payload_bits=...)
    PrefixContainer(code=宮の森一条, leaf_count=2, payload_bits=...)
      LeafBlock(leaf_count=2, codes=[一丁目, 二丁目])
    PrefixContainer(code=円山, leaf_count=1, payload_bits=...)
      LeafBlock(leaf_count=1, codes=[""])
```

Reader は順に次の `code_set` を返す。

```text
0 -> [北海道, 札幌市中央区, 宮の森一条, 一丁目]
1 -> [北海道, 札幌市中央区, 宮の森一条, 二丁目]
2 -> [北海道, 札幌市中央区, 円山, ""]
```

実際の `IndexStream` には文字列ではなく `WordBook.code` が格納される。

## 9. 圧縮効果

深さ `N` の path を単純に record ごとに格納すると、必要な code 数は次の通りである。

```text
N * record_count
```

`TI00` では、上位階層の共通 prefix は `PrefixContainer` として 1 回だけ格納し、末端階層は `LeafBlock` の code 列としてまとめる。
そのため、地名が行政階層に沿って強く共有される場合、格納 code 数を削減できる。

## 10. 制約

* `code` は `0 <= code < TT00.record_count` を満たさなければならない。
* `PrefixContainer.leaf_count` は `1` 以上でなければならない。
* `PrefixContainer.payload_bits` は `0` 以上でなければならない。
* `LeafBlock.leaf_count` は `1` 以上でなければならない。
* `LeafBlock` の leaf 数合計は `HierarchicalIndexChunk.data.record_count` と一致しなければならない。
* `IndexStream` を最後まで読んだ時、`emitted == record_count` でなければならない。
* `max_depth == 1` の場合、`IndexStream` は `LeafBlock` だけで構成される。
