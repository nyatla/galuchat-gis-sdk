# GI01 RleDataNode ShortValueEncoding仕様

## 1. 位置づけ

本書は、GI01 RLE DataNodeのラン長列を格納する`ShortValueEncoding`の仕様である。

本方式は、短いラン長値が連続する区間を固定bit幅でまとめて記録する。

## 2. 入力

入力はRLEラン長列である。

```
V[0], V[1], ... V[N-1]
```

各`V[i]`は正の整数であり、復号後の合計はノード画素数と一致しなければならない。

```
sum(V) == resolution * resolution
```

## 3. token構造

`ShortValueEncoding`は、先頭にラン長数`N`を置き、続いて`N-1`個のラン長値をtoken/P列で記録する。

```
[N: MBUInt]
[token/P列 for V[0] ... V[N-2]]
[TailP for V[N-1]]
```

末尾のラン長値`V[N-1]`は記録しない。
復号時は、既知のノード画素数から復元済みラン長値の合計を引いて求める。

```
V[N-1] = resolution * resolution - sum(V[0] ... V[N-2])
```

`N`は1以上でなければならない。
`N=1`の場合、token/P列は空であり、唯一のラン長値は`resolution * resolution`として復元する。

token/P列内のtokenは、次の2種類を混在させる。

| prefix | token | 消費するラン長数 |
|---|---|---:|
| `0` | MBUInt token | 1 |
| `1` | ShortValue token | 解像度別の対象連続長範囲 |

tokenはbit単位で連結する。各tokenはbyte境界に揃えない。

ストリーム末尾はbyte境界まで0でパディングする。

### 3.1 P配置

各tokenの直後には、そのtokenが生成した明示ラン長に対応する`P`を記録する。

```
[N: MBUInt]
[LenToken0][P0]
[LenToken1][P1]
...
[TailP]
```

`LenToken`は、MBUInt tokenまたはShortValue tokenである。
`P`は、直前の`LenToken`が生成したラン長数と、token開始時点のグローバルrun indexから必要bit数を決定する。

末尾ラン長`V[N-1]`は記録しないため、末尾ランに対応する`P`は`TailP`としてtoken/P列の末尾に記録する。

Palette Resolutionごとの`P`は、GI01 RLE DataNode構造仕様で定義する。
ShortValueEncodingでは次の規則で`P`の個数を決める。

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

### 3.2 MBUInt token混在時の配置例

次のラン長列とパレットインデックス列を例とする。

```
L = [3, 4, 2, 5, 7]
I = [0, 2, 1, 0, 2]
```

ここで、Palette Resolution=`01`、`InitialIndex=0`、DataEncoding=`01`とする。
ラン長数は`N=5`であり、末尾ラン長`L[4]`は記録しない。

token選択の結果が次であったとする。

```
Token0: MBUInt token     -> L[0] = 3
Token1: ShortValue token -> L[1], L[2] = 4, 2
Token2: MBUInt token     -> L[3] = 5
Tail : omitted          -> L[4] = 7
```

このとき、出力上の並びは次のようになる。

```
[N: MBUInt=5]
[Token0: 0 + MBUInt(3)]
  P: なし                  # run index 0 は InitialIndex
[Token1: 1 + run_code + values(4,2)]
  P: diff(I[1]), diff(I[2])
[Token2: 0 + MBUInt(5)]
  P: diff(I[3])
[TailP]
  P: diff(I[4])
```

Palette Resolution=`01`の差分は次である。

```
diff[n] = (I[n] - I[n-1] - 1) mod 3
```

概念的には次の順に並ぶ。

```
N
L0
L1 L2  P1 P2
L3     P3
TailP4
```

MBUInt tokenが混在しても、各tokenが生成したラン長数に対応する`P`を直後へ置く。
末尾ラン長は省略されるため、末尾ランに対応する`P`だけを`TailP`として最後に置く。

## 4. MBUInt token

MBUInt tokenは、token/P列内の1個のラン長をMBUIntでそのまま記録する。

```
[0: 1bit]
[V[i]: MBUInt]
```

このtokenは常に使用可能である。

## 5. ShortValue token

ShortValue tokenは、連続するラン長値を指定bit幅で記録する。

### 5.1 パラメータマトリクス

ShortValue tokenのパラメータは、次の5要素で定義する。

| パラメータ | 意味 |
|---|---|
| 対象連続長の基準格納bit数 | `run_code`を記録するbit幅の基準値。 |
| RunBitsAdd | 対象連続長の基準格納bit数に加算する値。 |
| 対象連続長の対象範囲の下限 | 1つのShortValue tokenに収容できるラン長値個数の下限 `run_min`。 |
| 基準bit幅 | 各ラン長値 `V[n] - 1` を記録するbit幅の基準値。 |
| VAddBits | 基準bit幅に加算する値。 |

対象連続長の格納bit数は、解像度ごとの対象連続長の基準格納bit数に、`RunBitsAdd`を加えて決定する。
V値bit幅は、解像度ごとの基準bit幅に、`VAddBits`を加えて決定する。
`RunBitsAdd`は0～1の整数である。
`VAddBits`は0～3の整数である。

```
run_bits = base_run_bits + RunBitsAdd
value_bits = base_value_bits + VAddBits
```

収容可能なV値範囲は`1～(2 ^ value_bits)`である。




パラメータは次の通りである。

| resolution | 対象連続長の基準格納bit数 | 対象連続長の対象範囲の下限 | 基準bit幅 | 対象連続長の範囲 | 収容可能なV値範囲 |
|---:|---:|---:|---:|---:|---:|
| 8 | 3 | 2 | 2 | `2～(2 + 2 ^ (3 + RunBitsAdd) - 1)` | `1～(2 ^ (2 + VAddBits))` |
| 16 | 3 | 2 | 2 | `2～(2 + 2 ^ (3 + RunBitsAdd) - 1)` | `1～(2 ^ (2 + VAddBits))` |
| 32 | 4 | 4 | 3 | `4～(4 + 2 ^ (4 + RunBitsAdd) - 1)` | `1～(2 ^ (3 + VAddBits))` |
| 64 | 4 | 4 | 4 | `4～(4 + 2 ^ (4 + RunBitsAdd) - 1)` | `1～(2 ^ (4 + VAddBits))` |
| 128 | 4 | 4 | 4 | `4～(4 + 2 ^ (4 + RunBitsAdd) - 1)` | `1～(2 ^ (4 + VAddBits))` |
| 256 | 5 | 4 | 4 | `4～(4 + 2 ^ (5 + RunBitsAdd) - 1)` | `1～(2 ^ (4 + VAddBits))` |

上記以外の解像度では、ShortValue tokenを使用しない。

### 5.2 使用条件

tokenに収容する全てのラン長値は、解像度別の収容可能範囲内でなければならない。

```
1 <= V[k] <= 2 ^ value_bits
```

`run`は解像度別の対象連続長範囲内でなければならない。

```
run_bits = base_run_bits + RunBitsAdd
run_min <= run <= run_min + 2 ^ run_bits - 1
run_code = run - run_min
```

### 5.3 符号化形式

```
[1: 1bit]
[run_code: run_bits]
[V[i] - 1: value_bits]
...
[V[i + run - 1] - 1: value_bits]
```

`run_code`は、解像度別の対象連続長の基準格納bit数に`RunBitsAdd`を加えたbit幅で記録する。

### 5.4 復号

`run_code`を解像度別の対象連続長格納bit数で読み、`run`を求める。

```
run = run_code + run_min
```

続いて`value_bits`幅の値を`run`個読み、それぞれに1を加えてラン長列へ追加する。

```
V = encoded_value + 1
```

## 6. token選択

符号化時は、末尾のラン長値`V[N-1]`を除外した`V[0] ... V[N-2]`を対象に、各位置から開始可能なtoken候補を生成し、総bit数が最小になるtoken列を選択する。

評価対象は次の候補である。

* MBUInt token
* ShortValue token

`M = N - 1`とし、`cost[i]`を`V[i] ... V[M-1]`を符号化する最小bit数とする。

```
cost[M] = 0
cost[i] = min(token_bits(i, j) + cost[j])
```

`j`はtoken消費後の次indexである。

### 6.1 L/P分離による符号化手順

出力は`LenToken`と`P`を交互に配置するが、符号化時のtoken選択はラン長列`L`だけを対象に行ってよい。

推奨する符号化手順は次の通りである。

1. 入力RLE列から、ラン長列`L`とパレットインデックス列`P`を一度分離する。
2. ラン長列`L`に対してShortValueEncodingのtoken選択を行う。
3. 選択された各`LenToken`について、そのtokenが消費するラン長数を求める。
4. 対応する`P`をパレット解像度ごとの規則で取り出し、`LenToken`直後へ配置する。
5. 末尾ラン長値を省略する場合は、末尾ランに対応する`P`を`TailP`として最後に配置する。

この手順により、token選択の評価は従来通りラン長列だけで行い、最終的なビットストリームのみ`LenToken/P`の順に並べ替えればよい。
`P`のbit数は同じラン数に対して一定であるため、`P`の配置をL/P化しても、ラン長token選択の最小化結果は変化しない。

## 7. 終端

bitストリーム内に終端tokenは置かない。

復号時は、先頭の`N`を読み、token/P列から`N-1`個のラン長値を復元する。
最後の1個は、復元済みラン長値の合計を`resolution * resolution`から引いて求める。

復号時は、各token直後の`P`を読みながら`N-1`個の明示ランを復元し、最後にPalette Resolutionごとの規則に従って必要なら`TailP`を読んで末尾ランのパレットインデックスを復元する。

後続データは、ShortValueEncodingストリームをbyte境界へパディングした次byteから開始する。

## 8. エラー条件

復号時は次をエラーとする。

* 復元したラン長値が0以下になる。
* 復元済みラン長値の合計が`resolution * resolution`以上になる。
* 復元した末尾ラン長値が0以下になる。
* 先頭の`N`が0である。
* 非対応解像度でShortValue tokenを読む。
* token/P列が`N-1`個を超えて値を復元する。
