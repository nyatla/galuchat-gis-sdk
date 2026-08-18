# TM00 TokenMap チャンク仕様

## 1. 概要

`TM00` は、token id から復元 byte 断片を得るための辞書チャンクである。
`TT00` の palette packet は、この `TM00` の token id を参照する。

```text
Chunk
  name: 4 bytes = "TM00"
  size: MBUInt
  data: byte[size]
```

本仕様で説明する整数値は、特に明記しない限り MBUInt で格納する。

## 2. データ構造

```text
TokenMapChunk.data
  token_count: MBUInt
  token_page_count: MBUInt
  TokenPage[token_page_count]

TokenPage
  PageHeader: 1 byte
  token_byte_size: MBUInt
  page_token_count: MBUInt
  token_stream_size: MBUInt
  TokenStream: byte[token_stream_size]
```

token id は `TokenPage[]` 内の token 出現順で決まる。
`TokenPage[]` は `token_byte_size` 昇順に並べる。
同一 `TokenPage` には同じ `token_byte_size` の token だけを格納する。
`token_stream_size` は `token_byte_size * page_token_count` と一致しなければならない。

`PageHeader` は初期仕様では `0` 固定とする。
将来の token stream encoding 切り替え用に予約する。

`token_byte_size` は復元時にコピーする byte 数であり、文字数は持たない。
`TokenStream` は token bytes を固定長で連結した byte 列である。

```text
0 -> 一
1 -> 二
2 -> 丁目
3 -> 嵯峨
4 -> 団地
```

`TT00` の palette packet 内の `global_token_id` は、`TT00.token_bits` bit で参照する。
`TT00.token_bits` は、この `token_count` を表現できる最小 bit 数とする。
そのため `token_count` は `2^TT00.token_bits` 以下でなければならない。

## 3. Token の意味

token には次の種類がある。
ただし種類そのものは格納しない。
Reader はすべて「復元 byte 断片」として扱えばよい。

| 種類 | 例 | 内容 |
| --- | --- | --- |
| 単独文字 token | `一` | 1 文字を復元する |
| 復号文字 token | `嵯峨` | 一意に連続しやすい文字列をまとめる |
| 複合文字 token | `丁目` | 頻出する文字列をまとめる |

## 4. 復元規則

`TT00` から得た `global_token_id` を `TokenPage[]` 内の通算 token index として使う。

```text
token_base = 0
for page in TokenPage[]:
  if global_token_id < token_base + page.page_token_count:
    index_in_page = global_token_id - token_base
    offset = index_in_page * page.token_byte_size
    emit page.TokenStream[offset : offset + page.token_byte_size]
    break
  token_base += page.page_token_count
```

`emit` は token の `bytes` を出力 byte 列へ連結する。
文字列として解釈する場合は、呼び出し側が復元後の byte 列を UTF-8 として decode する。

`global_token_id >= token_count` は不正である。

この構造により、対象 `TokenPage` が決まった後は page 内 token entry を走査せず、乗算で byte offset を計算できる。

## 5. 展開レス Reader

Reader は `TM00` を必ずしも `token_id -> bytes` の配列へ展開しなくてよい。
展開しない場合は、`TokenPage[]` の header だけを読み、次の情報を保持する。

```text
MappedTokenPage
  token_base
  token_byte_size
  page_token_count
  token_stream_start
  token_stream_size
```

`token_stream_start` は `TM00.data` 先頭から見た `TokenStream` の byte offset である。
`global_token_id` から token を読む時は、対象 page を選び、次の式で byte 範囲を切り出す。

```text
index_in_page = global_token_id - token_base
offset = token_stream_start + index_in_page * token_byte_size
token = TM00.data[offset : offset + token_byte_size]
```

この読み方では token table 全体の個別 `bytes` オブジェクトを作らない。
ただし同じ token は `TT00` の palette から繰り返し参照されるため、実装は任意で小さな LRU cache を持ってよい。
