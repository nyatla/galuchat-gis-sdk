# WordBook Bitstream 設計メモ

## 0. 現在の位置づけ

この文書は、`WordBook` の token 化と圧縮方式を検討した過程のメモである。
現行の格納仕様は次の文書に分割する。

```text
WordBookStorageFormat.md
TM00TokenMapChunk.md
TT00TextTableChunk.md
```

現行仕様では、`TransitionTable` を廃止し、`TM00` の token 辞書と `TT00` の palette 付き `RecordStream` で復元する。

```text
text -> token_id[]
token_id -> TM00.TokenPage[] 内の token bytes
TT00.RecordStream -> local palette -> token_id
```

以降の遷移 token / direct token stream / 局所遷移に関する記述は、圧縮方式を検討した過程のメモとして扱う。

## 1. 対象

対象は、全角文字列 `text` と、それを復元するための内部コード `code` の対応表である。

```text
source_id,text
1,一丁目
2,二丁目
3,三丁目
...
```

現在の実験対象は次の JSON とする。

```text
src/galuchat/wordbook/data/x_estat_shp_codes.sections.json
```

この JSON では `section_name` を `text` として扱う。`section_id` は入力元の識別子であり、`WordBook` 内には格納しない。

## 2. 目的

`code -> text` の検索システムを作る。

`code` はファイル生成時に割り当てる内部識別値であり、外部に対して固定する必要はない。
外部が文字列から `code` を得るための検索は遅くてもよく、`WordBook` 本体の必須機能には含めない。
主な課題は、`code -> text` のランダムアクセス性を保ちながら `text` 側の情報量を削減することである。

## 3. token 化方針

文字列を、先頭文字 token と文字遷移 token の列として表現する。

```text
text = [先頭文字トークン][遷移トークン]...
```

例:

```text
一丁目
  先頭文字 token: 一
  遷移 token: 一->丁, 丁->目

グリーンヒル団地
  先頭文字 token: グ
  遷移 token: グ->リ, リ->ー, ー->ン, ン->ヒ, ヒ->ル, ル->団, 団->地
```

デコード時は、先頭文字 token で最初の文字を得る。以降は直前の文字と遷移 token から次の文字を得る。

```text
head = decode_head_token()
text = head
prev = head
while not end:
  next = decode_transition_token(prev, token)
  text += next
  prev = next
```

## 4. token 集計

token 辞書は次の手順で作る。

1. 全 `text` に出現する全角文字の種類を集計する。
2. 全 `text` の先頭文字を集計し、先頭文字 token とする。
3. 全 `text` の隣接 2 文字を集計し、遷移 token とする。
4. 各 `text` を `[先頭文字 token][遷移 token]...` に変換する。

この段階では、bigram を 1 語句として置換するのではなく、文字間の遷移そのものを token として扱う。

## 5. 現在データでの token 数

`src/galuchat/wordbook/data/x_estat_shp_codes.sections.json` の実測値は次の通り。

| 項目 | 値 |
| --- | ---: |
| rows | 30,831 |
| empty text | 0 |
| 出現文字種類数 | 2,033 |
| 先頭文字 token 数 | 1,549 |
| 遷移 token 数 | 27,486 |
| 総文字数 | 108,035 |
| 総遷移数 | 77,204 |

先頭文字 token は最大でも出現文字種類数以下になる。遷移 token は `前文字 -> 次文字` の組なので、文字種類数より大きくなる。

## 6. 格納イメージ

`code` は record の物理位置を表す。
record の格納順は、圧縮効率を優先して並べ替えられる。

```text
code = physical_row_index
page_id = code // page_size
index_in_page = code % page_size
```

文字列本体は固定件数のブロックに分ける。

```text
header
token table
page index
page[0]
page[1]
...
```

各ブロックは、文字列ごとの token 数と token 列を持つ。

```text
text_count
token_count_per_text[]
token_stream
```

1 件取得時は `code` からブロックを引き、ブロック内の対象文字列だけを復元する。

## 7. 評価する値

まず知りたい値は token 数である。

- `head_token_count`
- `transition_token_count`
- `token_count_per_text`
- `bits_per_head_token`
- `bits_per_transition_token`
- `encoded_bits_per_text`

次に、辞書とブロックを含めた格納スコアを測る。

```text
storage_score =
  head_token_table_bits
  + transition_token_table_bits
  + page_index_bits
  + token_count_bits
  + token_stream_bits
```

## 8. 次に確認すること

1. 先頭文字 token と遷移 token を頻度順に並べる。
2. 固定 bit 幅で token を格納した場合のサイズを出す。
3. 頻度順の可変長 token にした場合のサイズを出す。
4. 遷移 token を `前文字ごとの局所 token` に分けると小さくなるか確認する。
5. ブロックサイズを変え、ランダムアクセス時の読み量と格納サイズを比較する。

## 9. 文字列表現 token を短くする戦略

最初に狙うべき短縮は、遷移 token を全体共通の token 空間で持たず、`前文字ごとの局所 token` として持つことである。

全体共通の遷移 token では、現在のデータで 27,486 種類あるため、固定長なら 15bit が必要になる。

```text
transition_token = token_id_of(prev_char -> next_char)
```

しかしデコード時には直前の文字 `prev_char` が必ず分かっている。したがって token は `prev_char` ごとの候補だけを区別できればよい。

```text
transition_token = local_token_id_of(next_char in transitions[prev_char])
```

例:

```text
prev = 丁
  token 0 -> 目

prev = 一
  token 0 -> 丁
  token 1 -> 区
  token 2 -> 号
  ...
```

この方式では、同じ `token 0` でも `prev_char` によって意味が変わる。遷移 token 単体では復元できないが、文字列復元時には常に `prev_char` があるため問題ない。

## 10. 固定長 token の概算

現在データでの概算は次の通り。

| 方式 | 概算 |
| --- | ---: |
| 先頭文字 token 固定幅 | 16 bit |
| 全体遷移 token 固定幅 | 15 bit |
| 全体遷移 token stream | 187,151 byte |
| 局所遷移 token stream | 105,587 byte |
| 局所遷移による削減 | 81,563 byte |

局所遷移 token の固定幅は、`prev_char` ごとの遷移先種類数で決まる。

```text
width(prev_char) = ceil(log2(len(transitions[prev_char])))
```

遷移先が 1 種類しかない文字は、遷移 token を 0bit にできる。これは `prev_char` が決まった時点で次文字も一意に決まるためである。

## 11. 頻度順 token

固定長の次は、頻度順 token を検討する。

先頭文字は出現頻度に偏りがある。

```text
字, 上, 下, 西, 大, 中, 東, 小, 北, 南, ...
```

遷移も頻度に偏りがある。

```text
丁目, 田町, 屋敷, 団地, 一丁, 屋町, 久保, 小字, ...
```

ただし遷移 token は全体頻度で短くするより、`prev_char` ごとの局所頻度で短くする方が筋がよい。

```text
transitions[丁]:
  目 -> short code

transitions[一]:
  丁 -> short code
  区 -> next code
  号 -> next code
```

理論上の目安では、全体遷移のエントロピーは約 13.5bit/遷移、局所遷移のエントロピーは約 5.0bit/遷移である。まず局所 token 化を優先し、その後に局所頻度順の可変長 token を試す。

## 12. 採用順序

実装と評価は次の順序で進める。

1. 先頭文字 token は 16bit 固定幅にする。
2. 遷移 token は `prev_char` ごとの局所辞書で固定幅にする。
3. 遷移先が 1 種類の `prev_char` は token を省略する。
4. 局所辞書を頻度順に並べ、短い code を高頻度遷移へ割り当てる。
5. 先頭文字 token も頻度順の可変長 code にする。

この順序なら、デコーダは常に次の状態だけを持てばよい。

```text
prev_char
current_page
token_reader
```

複雑な文脈モデルはまだ入れない。まず `prev_char -> next_char` の 1 次遷移だけで、どこまで格納スコアが下がるかを見る。

## 13. token マージ戦略

文字 token と遷移 token は独立に最適化するのではなく、相互にマージして総 token 数を下げる。

ここでは、文字 token を次の 3 種に分ける。

| 種類 | 意味 |
| --- | --- |
| 単独文字 token | 1 文字を復元する基本 token |
| 復号文字 token | 遷移先が 1 種類の文字列をまとめた token |
| 複合文字 token | 頻出する複数文字列をまとめた token |

### 13.1 復号文字 token

遷移先が 1 種類しかない文字は、次文字が確定している。

```text
嵯 -> 峨
諏 -> 訪
菖 -> 蒲
```

このような文字は、単独文字 token としてではなく、復号文字 token としてまとめる。

```text
嵯 token = 嵯峨
諏 token = 諏訪
菖 token = 菖蒲
```

このとき、`嵯->峨` の遷移 token は不要になる。さらに `峨` が他の場所で単独利用されないなら、`峨` の単独文字 token も削除できる。

採用条件:

```text
gain =
  removed_transition_bits
  + removed_unused_char_token_bits
  - added_decode_char_token_bits
```

`gain > 0` なら採用する。

### 13.2 複合文字 token

使用頻度が高い遷移は、2 文字以上を 1 つの複合文字 token にする。

例:

```text
丁 + 目 -> 丁目
団 + 地 -> 団地
田 + 町 -> 田町
```

複合文字 token を追加すると、該当する遷移 token の出現回数が減る。一方で、複合文字 token の定義が増える。

採用条件:

```text
gain =
  removed_transition_bits
  + removed_unused_char_token_bits
  - added_compound_char_token_bits
```

`gain > 0` なら採用する。

ここで `removed_unused_char_token_bits` は、複合 token 化の結果として単独文字 token が使われなくなった場合だけ加算する。

### 13.3 マージ後の再集計

token をマージすると、遷移グラフが変わる。

```text
一 丁 目
```

`丁目` を複合文字 token にすると、表現は次のようになる。

```text
一 丁目
```

この結果、遷移は `一->丁` と `丁->目` ではなく、`一->丁目` になる。したがって、1 回のマージで終わらせず、マージ後に次を再集計する。

1. 使用される文字 token の集合
2. token 間の遷移集合
3. 各 token の出現回数
4. 各 token の遷移先種類数

再集計後に、さらに `一 + 丁目 -> 一丁目` が有利なら複合文字 token として採用する。

### 13.4 探索順序

初期実装では、次の貪欲法でよい。

1. 遷移先が 1 種類の文字を復号文字 token 候補にする。
2. 頻出遷移を複合文字 token 候補にする。
3. 各候補の `gain` を計算する。
4. `gain` が最大の候補を 1 つ採用する。
5. token 列と遷移表を再集計する。
6. `gain > 0` の候補がなくなるまで繰り返す。

一度に大量採用すると、候補同士が同じ遷移を取り合って効果を二重計上しやすい。まずは 1 件ずつ採用して再集計する。

### 13.5 注意点

複合文字 token を増やしすぎると、辞書が大きくなり、ランダムアクセス時に必要な token table も重くなる。

そのため採用判定では、必ず次を含める。

- 複合 token 定義の保存コスト
- token id 幅の増加コスト
- 遷移 token の削減量
- 未使用になった単独文字 token の削除量

定義による増加分を、遷移 token の減少量が上回る場合だけ採用する。
