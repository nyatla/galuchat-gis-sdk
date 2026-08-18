# TT00 TextTable チャンク仕様

## 1. 概要

`TT00` は、内部コード `code` から文字列を復元する本体チャンクである。
`TT00` は page 列を持ち、各 page 内の `RecordStream` は `TM00` の token id を参照する。

```text
Chunk
  name: 4 bytes = "TT00"
  size: MBUInt
  data: byte[size]
```

本仕様で説明する整数値は、特に明記しない限り MBUInt で格納する。

## 2. データ構造

```text
TextTableChunk.data
  record_count: MBUInt
  page_size: MBUInt
  page_count: MBUInt
  token_bits: MBUInt
  Page[]
```

| 項目 | 内容 |
| --- | --- |
| `record_count` | record 数 |
| `page_size` | 1 page に入れる最大 record 数 |
| `page_count` | page 数 |
| `token_bits` | palette packet 内の `global_token_id` の bit 数 |

`record_count`, `page_size`, `page_count`, `token_bits` は `TT00` が保持する。
`NM00` には重複して持たない。
`token_bits` は `1..16` とする。
`token_bits` は、使用する `TM00.token_count` を表現できる最小 bit 数を選択する。
`TM00.token_count` は `2^token_bits` 以下でなければならない。

record は、まず構成 token 数ごとに分類する。
構成 token 数とは、record を復元するために必要な `TM00` token id の個数であり、record terminator `0` は含めない。
同じ構成 token 数の record 群を `TokenCountGroup` と呼ぶ。

`Page[]` は `TokenCountGroup` ごとに連続して配置する。
`TokenCountGroup` は構成 token 数 `0` から昇順に並べる。
各 `TokenCountGroup` 内では、palette 更新回数を減らすための page 順序最適化を行ってよい。
異なる構成 token 数の record を同じ page に混在させてはならない。

## 3. Page

`Page` は、一定件数分の record を保持する。
GI01 の page と同様に、先頭に 1 byte の `PageHeader` を置く。

```text
Page
  PageHeader: 1 byte
  record_token_count: MBUInt
  page_record_count: MBUInt
  record_stream_size: MBUInt
  RecordStream: byte[record_stream_size]
```

`record_token_count` は、この `Page` に含まれる record の構成 token 数である。
同一 page 内の record はすべて同じ `record_token_count` を持たなければならない。
`Page[]` は `record_token_count` 昇順に並べる。
同じ `record_token_count` の範囲内では、page 順序最適化によって任意の順序に並べてよい。
`page_record_count` は、この `Page` に含まれる record 数である。
通常は `TextTableChunk.data.page_size` と同じだが、各 `TokenCountGroup` の最後の page では小さくなる。

同じ `record_token_count` の page では、圧縮を行わない固定長 payload であれば、record の payload local code 数は常に `record_token_count + 1` になる。
この性質により、固定長 payload variant では `index_in_page` から対象 record の開始位置を直接計算できる。
現行の `RecordStream` は palette 更新 packet を含むため、固定長性を利用するには別 encoding または offset marker が必要である。

`RecordStream` の実体は bit stream である。
`record_stream_size` は、その bit stream を byte 境界まで 0 padding して格納した byte 数を表す。
byte alignment は page 単位で取る。
つまり各 `Page` の `RecordStream` は byte 境界から開始し、byte 境界で終了する。
bit cursor は page をまたいで継続しない。

## 4. PageHeader

`PageHeader` は page payload の格納方式を表す。

```text
bit7 bit6 | bit5 bit4 | bit3 bit2 bit1 bit0
  RSV     | Encoding  | RSV
```

| bit | 内容 |
| --- | --- |
| bit7-6 | 予約。0 |
| bit5-4 | `Encoding` |
| bit3-0 | 予約。0 |

`Encoding` は次の通り。

| Encoding | 意味 |
| --- | --- |
| `00` | RecordStream |
| `01` | Direct token stream。実験・比較用 |
| `10` | 予約 |
| `11` | 予約 |

初期仕様では `Encoding=00` を本線とする。

## 5. RecordStream

`Encoding=00` の `RecordStream` は、Header + Value 形式の packet 列である。
packet 列は byte 列ではなく連続した bit stream として読む。

```text
RecordStream
  packet_count: MBUInt
  packet[packet_count]

packet
  PacketHeader
  value: bit[value_bit_size]

PacketHeader
  packet_type: 2bit
  value_bit_size: MBUInt
```

packet は出現順に処理する。
palette 状態は同じ `RecordStream` 内で次 packet へ引き継ぐ。
page 境界では palette 状態を引き継がない。

`packet_type` は 2bit の値として `RecordStream` の bit cursor 上に直接配置する。
byte には packing しない。
`packet_type` の直後に `value_bit_size` を続ける。
`MBUInt` は通常の byte 符号を 8bit 単位で bit stream に流し込む。
packet 境界で byte alignment は要求しない。
最後の packet を読み終えた後、`record_stream_size` の byte 境界まで残る bit は padding であり、すべて 0 でなければならない。
この padding は `RecordStream` 末尾、すなわち page 末尾にのみ置く。

```text
bit1 bit0
packet_type
```

| packet_type | 名称 | 内容 |
| --- | --- | --- |
| `0` | `BasePalettePacket` | palette の基準状態を定義する |
| `1` | `UpdatePalettePacket` | palette slot を部分更新する |
| `2` | `TokenPayloadPacket` | 4bit local code stream を格納する |
| `3` | 予約 | 未使用 |

## 6. BasePalettePacket

`BasePalettePacket` は、palette の基準状態を定義する。
通常は `RecordStream` の先頭に 1 回置く。
`RecordStream` 開始時の palette は空である。

```text
BasePalettePacket.value
  entrySlots: 15bit
  entry[entry_count]

entry
  global_token_id: bit[token_bits]
```

`entrySlots` は 15bit の slot bitmask である。
bit0..bit14 が palette slot `1..15` に対応する。
record terminator の local code `0` は palette slot ではないため、`entrySlots` には含めない。
`entrySlots` は value 内で 15bit の bit field として格納する。

```text
slot = bit_index + 1
entry_count = popcount(entrySlots)
```

`entry` は、`entrySlots` で bit が立っている slot の昇順に並ぶ。
slot index は格納しない。
指定されない slot は空とする。
`entry_count` は最大 `15` である。
`global_token_id` は `TM00` の token id であり、`TextTableChunk.data.token_bits` bit で格納する。

## 7. UpdatePalettePacket

`UpdatePalettePacket` は、現在の palette の一部を更新する。
1 packet につき 1 slot を更新する。

```text
UpdatePalettePacket.value
  slot: 4bit
  global_token_id: bit[token_bits]
```

`slot` は local code と同じ 4bit 値であり、`1..15` を指定する。
`slot == 0` は record terminator と衝突するため不正とする。
`global_token_id` は `TM00` の token id である。
この value は合計 `4 + TextTableChunk.data.token_bits` bit であり、byte alignment 用の padding は持たない。

この packet は、直後に続く `TokenPayloadPacket` より前に適用する。
複数 slot を更新したい場合は、`UpdatePalettePacket` を複数個連続して置く。
連続する `UpdatePalettePacket` は、出現順にすべて適用する。

## 8. TokenPayloadPacket

`TokenPayloadPacket` は、4bit local code stream を格納する。

```text
TokenPayloadPacket.value
  local_code_stream: bit[value_bit_size]
```

`local_code_stream` は 4bit local code を上位 nibble から順に格納する。
`value_bit_size` から local code 数は一意に決まる。

```text
value_bit_size % 4 == 0
local_code_count = value_bit_size / 4
```

local code `0` は record terminator であり、終端記号を兼ねる。
`TokenPayloadPacket` は bit 長で終端位置を持つため、byte 境界合わせの padding は不要である。

```text
0    = record terminator
1-15 = palette slot
```

`local_code == 0` を読むと、現在の record を終了する。
`local_code != 0` の場合は、`palette[local_code]` で global token id を得て、`TM00` から byte 断片を復元する。
空 slot を参照する local code は不正である。
`RecordStream` 内で読んだ record terminator の数は、その `Page` の `page_record_count` と一致しなければならない。

`TokenPayloadPacket` は複数に分割してよい。
ただし分割位置は local code 境界、つまり 4bit 境界に置く。
packet の分割は復元結果に影響しない。

## 9. 復元手順

packet を順に読み、palette 状態を更新しながら `TokenPayloadPacket` の local code を復元する。

```text
palette = empty
record_index = 0

for packet in packet_stream:
  if packet.type == BasePalettePacket:
    palette = packet.palette
  if packet.type == UpdatePalettePacket:
    palette[packet.slot] = packet.global_token_id
  if packet.type == TokenPayloadPacket:
    for local_code in packet.local_code_stream:
      if local_code == 0:
        record_index += 1
      else:
        token = palette[local_code]
        emit TM00.TokenPage[] 内の token bytes
```

## 10. 格納例

```text
records:
  [一][丁目]
  [二][丁目]
  [嵯峨]

Page:
  record_token_count = 2
  page_record_count = 3

RecordStream:
  packet_count = 2

packet[0]: BasePalettePacket
  entrySlots = 0b000000000001111
  entry[0] -> token_id(一)    // slot 1
  entry[1] -> token_id(丁目)  // slot 2
  entry[2] -> token_id(二)    // slot 3
  entry[3] -> token_id(嵯峨)  // slot 4

packet[1]: TokenPayloadPacket
  local_code_stream = [1, 2, 0, 3, 2, 0, 4, 0]
```

## 11. 読み出し時の page 探索

`TT00` は `PageIndex` を持たない。
`code` から対象 page を探すときは、`Page[]` を先頭から読み、`page_record_count` を累積する。

```text
record_base = 0
for page in Page[]:
  if code < record_base + page.page_record_count:
    index_in_page = code - record_base
    decode page[index_in_page]
    break
  skip page.RecordStream by record_stream_size
  record_base += page.page_record_count
```

この走査は page 単位であり、全 record を走査するものではない。
各 page は `record_stream_size` を持つため、対象外 page の `RecordStream` は復号せずに読み飛ばせる。

## 12. 未決定事項

- `PageHeader.Encoding=01` の direct token stream を比較用に残すか。
- `PageHeader.Encoding=10` 以降の圧縮方式を使うか。
- Page 内 skip を terminator scan だけで行うか、任意で offset marker を持つか。
- `BasePalettePacket` を page 先頭に必須とするか、空 palette に対する `UpdatePalettePacket` 初期化を許可するか。
