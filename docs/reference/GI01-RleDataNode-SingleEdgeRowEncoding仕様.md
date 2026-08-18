# GI01 RleDataNode SingleEdgeRowEncoding仕様

## 1. 位置づけ

本書は、GI01 RLE DataNodeのラン長列を格納する`SingleEdgeRowEncoding`の仕様である。

本方式は、縦方向に2色で分断された`resolution`四方の領域について、左上から開始されるジグザグスキャンで発生する1本境界のラン長列を記録する。

## 2. 入力

入力はRLEラン長列である。

```
V[0], V[1], ... V[N-1]
```

各`V[i]`は正の整数であり、復号後の合計はノード画素数と一致しなければならない。

```
sum(V) == resolution * resolution
```

## 3. 基本モデル

`resolution`を`L`とする。

縦方向に2色で分断された領域をジグザグスキャンした場合、同一行内の1本境界に由来する隣接ラン長は、理想的には次の関係を持つ。

```
V[i] == 2 * L - V[i - 1]
```

この関係からの偏差を`d[i]`として定義する。

```
d[i] = V[i] - (2 * L - V[i - 1])
     = V[i] + V[i - 1] - 2 * L
```

符号化では、初期値`V[start]`を直接記録し、以降のラン長を`d`で復元する。

```
V[i] = 2 * L - V[i - 1] + d[i]
```

`d[i]`は、現行のLinePairにおける`a`と同じ値である。
本方式は、LinePairで記録していた境界位置差分`db`を持たず、前ラン長と偏差`d`だけで次ラン長を復元する。

## 4. token構造

`SingleEdgeRowEncoding`は、次の2種類のtokenを混在させる。

| prefix | token | 消費するラン長数 |
|---|---|---:|
| `0` | MBUInt token | 1 |
| `1` | SingleEdgeRow token | 2以上 |

SingleEdgeRowEncodingでは、ラン長数`N`をMBUIntで先に記録し、末尾値`V[N-1]`を除くラン長列をprefix付きtoken/P列として記録する。
末尾値は、既知の画素数から復元済みラン長の合計を差し引いて復元する。

```
[N: MBUInt]
[token/P列 for V[0] ... V[N-2]]
[TailP for V[N-1]]
```

`MBUIntReduceBits`が指定された場合、ラン長数に続いて先頭値をMBUIntで記録し、末尾値を除く中間ラン長列をprefix付きtoken/P列として記録する。
末尾値は、既知の画素数から復元済みラン長の合計を差し引いて復元する。
この場合のprefix `0` は、中間ラン長列のShort MBUInt tokenを表す。
prefix `1` はSingleEdgeRow tokenを表し、SingleEdgeRow tokenの構造は変わらない。

tokenはbit単位で連結する。各tokenはbyte境界に揃えない。

ストリーム末尾はbyte境界まで0でパディングする。

### 4.1 通常形式のP配置

`MBUIntReduceBits`が指定されない通常形式では、各tokenの直後に、そのtokenが生成した明示ラン長に対応する`P`を記録する。

```
[N: MBUInt]
[LenToken0][P0]
[LenToken1][P1]
...
[TailP]
```

`LenToken`は、MBUInt tokenまたはSingleEdgeRow tokenである。
`P`は、直前の`LenToken`が生成したラン長数と、token開始時点のグローバルrun indexから必要bit数を決定する。

末尾ラン長`V[N-1]`は記録しないため、末尾ランに対応する`P`は`TailP`としてtoken/P列の末尾に記録する。

Palette Resolutionごとの`P`は、GI01 RLE DataNode構造仕様で定義する。
通常形式では次の規則で`P`の個数を決める。

| Palette Resolution | token直後の`P` | `TailP` |
|---|---|---|
| `00` | なし | なし |
| `01` | token内の各runについて、run index 0を除き1bit差分を記録 | `N>=2`の場合のみ1bit差分 |
| `10` | token内の各runについて、run index 0を除き2bit差分を記録 | `N>=2`の場合のみ2bit差分 |
| `11` | token内の各runについて4bit即値indexを記録 | 4bit即値index |

Palette Resolution=`01`および`10`では、run index 0のパレットインデックスはPalletHeaderの`InitialIndex`から復元するため、run index 0に対応する`P`は記録しない。
run index 1以降は、直前runのパレットインデックスとの差分を記録する。
したがって、tokenがrun index 0を含む場合、そのtoken直後に記録する`P`の個数は`token_run_count - 1`である。
tokenがrun index 0を含まない場合、そのtoken直後に記録する`P`の個数は`token_run_count`である。
末尾ランがrun index 0である場合、`TailP`は記録しない。
末尾ランがrun index 1以降である場合、`TailP`を記録する。

Palette Resolution=`11`ではPalletHeaderに`InitialIndex`が存在しないため、run index 0を含む全runについて4bit即値indexを記録する。

### 4.2 MBUInt token混在時の配置例

次のラン長列とパレットインデックス列を例とする。

```
L = [5, 6, 7, 9, 4]
I = [0, 2, 1, 0, 2]
```

ここで、Palette Resolution=`01`、`InitialIndex=0`、DataEncoding=`10`、通常形式とする。
ラン長数は`N=5`であり、末尾ラン長`L[4]`は記録しない。

token選択の結果が次であったとする。

```
Token0: MBUInt token        -> L[0] = 5
Token1: SingleEdgeRow token -> L[1], L[2] = 6, 7
Token2: MBUInt token        -> L[3] = 9
Tail : omitted             -> L[4] = 4
```

このとき、出力上の並びは次のようになる。

```
[N: MBUInt=5]
[Token0: 0 + MBUInt(5)]
  P: なし                  # run index 0 は InitialIndex
[Token1: 1 + run_count(2) + MBUInt(6) + d(7)]
  P: diff(I[1]), diff(I[2])
[Token2: 0 + MBUInt(9)]
  P: diff(I[3])
[TailP]
  P: diff(I[4])
```

P3の差分は次式で計算する。

```
diff[n] = (I[n] - I[n-1] - 1) mod 3
```

上記の例では、差分列は次の通りである。

```
diff[1] = (2 - 0 - 1) mod 3 = 1
diff[2] = (1 - 2 - 1) mod 3 = 1
diff[3] = (0 - 1 - 1) mod 3 = 1
diff[4] = (2 - 0 - 1) mod 3 = 1
```

したがって、概念上の配置は次のようになる。

```
N
L0
L1 L2  P1 P2
L3     P3
TailP4
```

MBUInt tokenが混在しても、各tokenが生成したラン長数に対応する`P`を直後へ置く。
末尾ラン長は省略されるため、末尾ランに対応する`P`だけを`TailP`として最後に置く。

## 5. MBUInt token

MBUInt tokenは、1個のラン長をMBUIntでそのまま記録する。

`MBUIntReduceBits`が指定されない場合、prefix `0` は常に次の形式で1個のラン長を生成する。

```
[0: 1bit]
[V[i]: MBUInt]
```

このtokenは`MBUIntReduceBits`が指定されない場合に使用可能である。

## 6. SingleEdgeRow token

SingleEdgeRow tokenは、開始ラン長を直接記録し、続くラン長を偏差`d`の列で記録する。

```
[1: 1bit]
[run_count - 2: 5bit]
[V[start]: MBUInt]
[d[start + 1] - d_min: d値bit幅]
...
[d[start + run_count - 1] - d_min: d値bit幅]
```

`run_count`は、このtokenが消費するラン長値の個数である。
`run_count`は2以上33以下でなければならない。

```
2 <= run_count <= 33
```

`run_count - 2`を5bitで記録する。

### 6.1 初期値

開始ラン長`V[start]`は、正の整数でなければならない。

```
1 <= V[start]
```

開始ラン長はMBUIntで記録する。

### 6.2 対応解像度

| resolution | 備考 |
|---:|---|
| 8 | 対応 |
| 16 | 対応 |
| 32 | 対応 |
| 64 | 対応 |
| 128 | 対応 |
| 256 | 対応 |

上記以外の解像度では、SingleEdgeRow tokenを使用しない。

## 7. d値記録モード

`d`の記録範囲は、外部から与えられる`DValueFormat`で選択する。

`DValueFormat`は、`d`の記録bit幅を2, 3, 4の3モードから選択する。

| DValueFormat | d値bit幅 | dの記録値 | 収容可能なd |
|---|---:|---|---:|
| `00` | 2 | `d + 1` | -1～2 |
| `01` | 3 | `d + 3` | -3～4 |
| `10` | 4 | `d + 7` | -7～8 |
| `11` | 予約 | - | - |

符号化時は、token内の全`d`が収容可能な最小の`DValueFormat`を選択できる。
どの`DValueFormat`にも収まらない場合は、SingleEdgeRow tokenを使用しない。

## 8. 使用条件

SingleEdgeRow tokenに含まれる全ラン長は、正の整数でなければならない。

```
1 <= V[i]
```

2個目以降のラン長について、偏差`d[i]`は選択した`DValueFormat`の収容範囲内でなければならない。

```
d[i] = V[i] - (2 * resolution - V[i - 1])
```

また、連続記録する隣接ラン長は、同一行内の1本境界モデルに属していなければならない。
符号化時は、累積画素位置から行を判定し、行を飛び越える隣接関係をSingleEdgeRow tokenに含めてはならない。

```
pos_before(i) = sum(V[0:i])
pos_after(i)  = sum(V[0:i + 1])
row_before(i) = pos_before(i) // resolution
row_after(i)  = (pos_after(i) - 1) // resolution
```

SingleEdgeRow token内の各`V[i]`は、1行内または隣接する行境界上の1本境界モデルとして復元できる範囲に収まらなければならない。

## 9. 復号

復号時は、まず開始ラン長をMBUIntとして復元する。

```
V[start] = MBUInt
```

続いて、`d`を順に読み、直前のラン長から次のラン長を復元する。

```
d[i] = encoded_d + d_min
V[i] = 2 * resolution - V[i - 1] + d[i]
```

復元したラン長は、使用条件を満たさなければならない。

## 10. token選択

符号化時は、各位置から開始可能なtoken候補を生成し、総bit数が最小になるtoken列を選択する。

評価対象は次の候補である。

* MBUInt token
* SingleEdgeRow token

通常形式では、ラン長数`N`をtoken選択の外側でMBUIntとして記録する。
token選択の対象は`V[0] ... V[N-2]`であり、末尾値は記録しない。

`MBUIntReduceBits`が指定された場合、ラン長数と先頭値はtoken選択の外側でMBUIntとして記録する。
末尾値は記録せず、復号時に既知の画素数から復元する。
token選択の対象は中間ラン長列であり、評価対象はShort MBUInt tokenとSingleEdgeRow tokenである。

`cost[i]`を`V[i:]`を符号化する最小bit数とする。

```
cost[N] = 0
cost[i] = min(token_bits(i, j) + cost[j])
```

`j`はtoken消費後の次indexである。

### 10.1 L/P分離による符号化手順

通常形式の出力は`LenToken`と`P`を交互に配置するが、符号化時のtoken選択はラン長列`L`だけを対象に行ってよい。

推奨する符号化手順は次の通りである。

1. 入力RLE列から、ラン長列`L`とパレットインデックス列`P`を一度分離する。
2. ラン長列`L`に対してSingleEdgeRowEncodingのtoken選択を行う。
3. 選択された各`LenToken`について、そのtokenが消費するラン長数を求める。
4. 対応する`P`をパレット解像度ごとの規則で取り出し、`LenToken`直後へ配置する。
5. 末尾ラン長値を省略する場合は、末尾ランに対応する`P`を`TailP`として最後に配置する。

この手順により、token選択の評価は従来通りラン長列だけで行い、最終的なビットストリームのみ`LenToken/P`の順に並べ替えればよい。
`P`のbit数は同じラン数に対して一定であるため、通常形式では`P`の配置をL/P化しても、ラン長token選択の最小化結果は変化しない。

## 11. 終端

bitストリーム内に終端tokenは置かない。

復号時は、先頭のラン長数`N`を読み、末尾値を除く`N-1`個のラン長値を復元するまでtokenを読み続ける。
最後に、既知の画素数から復元済みラン長値の合計を差し引いて末尾値を復元する。

通常形式では、各token直後の`P`を読みながら`N-1`個の明示ランを復元し、最後にPalette Resolutionごとの規則に従って必要なら`TailP`を読んで末尾ランのパレットインデックスを復元する。

SingleEdgeRowEncodingデータ部はbyte境界まで0でパディングし、後続データは次byteから開始する。

## 12. MBUInt Reduce

`MBUIntReduceBits`が指定された場合、ラン長数とラン長列の先頭値をMBUIntで先に記録し、末尾値を除く中間ラン長列をtoken/P列として記録する。
`MBUIntReduceBits`はShort MBUInt tokenの値記録bit幅であり、2～5bitを使用できる。

入力ラン長列を次のように表す。

```
V[0], V[1], ... V[N-2], V[N-1]
```

短縮表記では、ラン長数`N`と先頭値`V[0]`をMBUIntで記録する。
その後、中間ラン長列`V[1] ... V[N-2]`をprefix付きtoken/P列として記録する。
末尾値`V[N-1]`は記録しない。

```
[N: MBUInt]
[V[0]: MBUInt]
[P for V[0]]
[middle token/P列]
[TailP]
```

`N`および`V[0]`にはprefixを置かない。
`V[0]`に対応する`P`は、Palette Resolutionごとの規則に従って`V[0]`の直後に記録する。
末尾ラン長`V[N-1]`は記録しないため、末尾ランに対応する`P`は`TailP`としてtoken/P列の末尾に記録する。

Palette Resolution=`01`および`10`では、run index 0のパレットインデックスはPalletHeaderの`InitialIndex`から復元するため、`V[0]`に対応する`P`は記録しない。
中間token列および`TailP`では、run index 1以降のランについて、直前runのパレットインデックスとの差分を記録する。

Palette Resolution=`11`ではPalletHeaderに`InitialIndex`が存在しないため、`V[0]`を含む全runについて4bit即値indexを記録する。

Palette Resolution=`00`では`P`を記録しない。

### 12.1 中間token列

中間token列は、次の2種類のtokenを混在させる。

| prefix | token | 消費する中間ラン長数 |
|---|---|---:|
| `0` | Short MBUInt token | 1 |
| `1` | SingleEdgeRow token | 2以上 |

prefix `1` のSingleEdgeRow tokenは、通常のSingleEdgeRow tokenと同じ構造である。
ただし、対象は中間ラン長列上の現在位置から始まる部分列である。

各中間tokenの直後には、そのtokenが生成した中間ラン長に対応する`P`を記録する。
Palette Resolution=`01`および`10`では、中間token列はrun index 1以降だけを対象とするため、各中間token直後の`P`の個数は`token_run_count`である。
Palette Resolution=`11`でも、各中間token直後の`P`の個数は`token_run_count`である。

### 12.2 Short MBUInt token

Short MBUInt tokenは、中間ラン長値を`MBUIntReduceBits`固定幅で1個記録する。

```
[0: 1bit]
[V[i] - 1: MBUIntReduceBits]
```

Short MBUInt tokenで記録する値は、1以上`2^MBUIntReduceBits`以下でなければならない。

```
1 <= V[i] <= 2^MBUIntReduceBits
```

### 12.3 中間値の通常MBUInt表記

`MBUIntReduceBits`が指定された場合、中間ラン長列に通常のMBUInt tokenを置かない。

中間ラン長値がShort MBUInt tokenで記録できない場合は、SingleEdgeRow tokenで記録しなければならない。
Short MBUInt tokenにもSingleEdgeRow tokenにもできない中間ラン長値を含むラン長列は、指定された`MBUIntReduceBits`では表現できない。

### 12.4 復号

復号時は、まずラン長数と先頭値を読む。

```
N = MBUInt
V[0] = MBUInt
```

続いて、中間token/P列を読み、末尾値を除く`N-1`個のラン長値を復元する。

```
while len(values) < N - 1:
    read middle token
    read P for generated runs if needed
```

中間token/P列を読み終えた後、Palette Resolutionごとの規則に従って必要なら末尾ランに対応する`TailP`を読む。
最後に、既知の画素数から復元済みラン長値の合計を差し引いて末尾値を復元する。

```
last = resolution * resolution - sum(values)
if last <= 0:
    error
output(last)
```

中間token列に終端tokenは置かない。

### 12.5 符号化条件

`MBUIntReduceBits`が指定された場合、ラン長列は2個以上の値を持たなければならない。

```
N >= 2
```

中間ラン長列は空でもよい。
中間ラン長列が空の場合、記録される値は`V[0]`と`V[N-1]`のみである。

## 13. エラー条件

復号時は次をエラーとする。

* 復元したラン長値が0以下になる。
* 復元したラン長値の合計が`resolution * resolution`を超える。
* 非対応解像度でSingleEdgeRow tokenを読む。
* `DValueFormat=11`である。
* `MBUIntReduceBits`が指定されていて、ラン長列が2個未満である。
* `MBUIntReduceBits`が指定されていて、Short MBUInt tokenの値が`1～2^MBUIntReduceBits`に収まらない。
* `MBUIntReduceBits`が指定されていて、中間ラン長値をShort MBUInt tokenまたはSingleEdgeRow tokenのいずれでも復元できない。
* SingleEdgeRow tokenが要求ラン長数または画素数を超えて値を復元する。
* 復元したラン長値が0以下になる。
* 復元したラン長列が同一行内の1本境界モデルを満たさない。
