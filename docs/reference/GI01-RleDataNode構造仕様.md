# GI01 RLE DataNode構造仕様

## 1. 概要

RLE DataNodeは、走査順に並べた画素列をラン長で圧縮する終端ノードである。
連続する同値画素をラン長列とパレットインデックス列へ変換して記録する。

GI01 RLE DataNodeは、最大16値のパレットを使用するRLE/P形式のみを扱う。
16値を超える値集合は、RLE DataNodeへ直接格納せず、上位の分割または別形式で処理する。

RLE DataNodeは次の要素で構成する。

```
[CellHeader (1 byte)]
[PalletHeader]
[パレット更新値列]
[RLEデータ部]
```

ラン長列の格納方式は、CellHeader内の`DataEncoding`で選択する。
GI01では次の3方式を定義する。

| DataEncoding | 方式 | 概要 |
|---|---|---|
| `00` | MBUInt列 | ラン長列をMBUInt列としてそのまま記録する。 |
| `01` | ShortValueEncoding | 短いラン長値の連続を固定bit幅で圧縮する。 |
| `10` | SingleEdgeRowEncoding | 行方向の単一境界をラン長列として圧縮する。 |
| `11` | 予約 | 使用しない。 |

`ShortValueEncoding`の詳細は[GI01-RleDataNode-ShortValueEncoding仕様.md](GI01-RleDataNode-ShortValueEncoding仕様.md)を参照する。

`SingleEdgeRowEncoding`の詳細は[GI01-RleDataNode-SingleEdgeRowEncoding仕様.md](GI01-RleDataNode-SingleEdgeRowEncoding仕様.md)を参照する。

`PairValueEncoding`はGI01 RLE DataNodeの`DataEncoding`割当から廃止した。

## 2. CellHeader

RLE DataNodeのCellHeaderは1byteである。

| bit | フィールド | 内容 |
|---:|---|---|
| 7-6 | TYPE | `10`: RLE DataNode |
| 5-4 | Palette Resolution | パレットインデックス列の格納方式 |
| 3-2 | DataEncoding | ラン長列の格納方式 |
| 1-0 | ScanMode | IndexMapの走査順 |

### 2.1 Palette Resolution

Palette Resolutionは、パレット数とインデックス列の格納方式を指定する。

| 値 | 対象パレット数 | インデックス列の格納方式 |
|---|---:|---|
| `00` | 1～2 | 初期インデックスのみをPalletHeaderへ記録し、後続は交互に復元する。 |
| `01` | 3 | 初期インデックスと1bit差分列で記録する。 |
| `10` | 4～5 | 初期インデックスと2bit差分列で記録する。 |
| `11` | 6～16 | 4bit即値インデックス列で記録する。 |

### 2.2 DataEncoding

DataEncodingは、ラン長列の格納方式を指定する。

| 値 | 方式 | ラン長情報`L`の表現 |
|---|---|---|
| `00` | MBUInt | 各ラン長値`V[i]`をMBUIntとして記録する。 |
| `01` | ShortValueEncoding | ラン長数を先頭に置き、末尾ランを除くラン長列をMBUInt tokenとShortValue tokenで記録する。 |
| `10` | SingleEdgeRowEncoding | ラン長数を先頭に置き、末尾ランを除くラン長列をMBUInt tokenとSingleEdgeRow tokenで記録する。 |
| `11` | 予約 | 読み取り時はエラーとする。 |

DataEncodingが`01`または`10`の場合、ラン長情報`L`はbit streamである。
bit stream内に終端tokenは置かず、末尾ランは既知のノード画素数から復元する。
`P`の配置と対応関係は、各DataEncoding仕様で定義する。

DataEncodingが`00`の場合、ラン長情報`L`はMBUInt値である。
ただし、Palette Resolution=`01`、`10`、`11`ではRLEデータ部が`L P`順のビットストリームになるため、RLEデータ部全体の末尾はbyte境界まで0でパディングする。

### 2.3 ScanMode

ScanModeは、RLE化前に画素を走査するIndexMapを指定する。

| 値 | IndexMap | 構成 |
|---|---|---|
| `00` | Zigzag | Zigzag |
| `01` | Zigzag + MirrorH | Mirror(x) → Zigzag |
| `10` | Zigzag + Transpose | Zigzag → Transpose |
| `11` | Zigzag + Transpose + MirrorV | Mirror(y) → Zigzag → Transpose |

IndexMap構造の詳細は[v1/Galuchat-IndexMap構造仕様.md](v1/Galuchat-IndexMap構造仕様.md)を参照する。

## 3. PalletHeaderとパレット更新値列

RLE DataNodeでは、CellHeaderの直後にPalletHeaderを置く。
PalletHeaderはPalette Resolutionごとにビット幅が異なり、byte境界へパディングしない。
後続のパレット更新値列は、PalletHeaderの直後のbit位置から連続して記録する。

パレット更新値列は、PalletHeaderで指定された更新がある場合のみ出現する。
更新値は、GI01のカスケードパレットへ反映される。

パレット更新値列の値は、ノードブロックのパレット格納方式に従い、絶対値または差分値として記録する。
カスケードパレットの扱いは[GI01-カスケードパレット.md](GI01-カスケードパレット.md)を参照する。

PalletHeaderには、DataEncodingごとの追加パラメータを保持する`EncodingParams`フィールドを置く。
`EncodingParams`の割り当てはDataEncodingごとに定義する。
使用しないDataEncodingでは0にする。

### 3.1 EncodingParams

`EncodingParams`は、ラン長列の符号化方式が必要とする追加パラメータを保持する4bitフィールドである。

| DataEncoding | 方式 | EncodingParamsの割り当て |
|---|---|---|
| `00` | MBUInt列 | 予約。0にする。 |
| `01` | ShortValueEncoding | bit2を`RunBitsAdd`、bit1-0を`VAddBits`として使用する。 |
| `10` | SingleEdgeRowEncoding | `DValueFormat * 5 + MBUIntReduceCode`として使用する。 |
| `11` | 予約 | 0にする。 |

ShortValueEncodingでは、`EncodingParams` bit2をShortValueEncoding仕様の`RunBitsAdd`、bit1-0を`VAddBits`として渡す。
対象連続長の格納bit数は、ShortValueEncoding仕様で定義する解像度ごとの基準bit数に`RunBitsAdd`を加えて決定する。
V値bit幅は、ShortValueEncoding仕様で定義する解像度ごとの基準bit幅に`VAddBits`を加えて決定する。
```
RunBitsAdd = (EncodingParams >> 2) & 0b1
VAddBits = EncodingParams & 0b011
run_bits = base_run_bits + RunBitsAdd
value_bits = base_value_bits + VAddBits
```

SingleEdgeRowEncodingでは、`EncodingParams`をSingleEdgeRowEncoding仕様の`DValueFormat`と`MBUIntReduceCode`に展開して渡す。

```
DValueFormat = EncodingParams // 5
MBUIntReduceCode = EncodingParams % 5
MBUIntReduceBits = None if MBUIntReduceCode == 0 else MBUIntReduceCode + 1
```

`EncodingParams=15`は予約値である。

### 3.2 Palette Resolution=`00`

1値または2値のパレットを扱う。
PalletHeaderは7bitである。

| bit | フィールド | 内容 |
|---:|---|---|
| 6 | InitialIndex | 初期インデックス。0～1。 |
| 5-4 | UpdatePalletTable2 | Slot0～1の更新位置フラグ |
| 3-0 | EncodingParams | DataEncodingごとの追加パラメータ。 |

`UpdatePalletTable2`は上位bitからSlot0、Slot1に対応する。
更新値列は、更新フラグが立ったslotの昇順で並べる。

ランごとのインデックスは次式で復元する。

```
index[n] = (InitialIndex + n) mod 2
```

1値ノードでは、参照しないSlotの更新bitは0にする。

### 3.3 Palette Resolution=`01`

3値のパレットを扱う。
PalletHeaderは9bitである。

| bit | フィールド | 内容 |
|---:|---|---|
| 8-7 | InitialIndex | 初期インデックス。0～2。 |
| 6-4 | UpdatePalletTable3 | Slot0～2の更新位置フラグ |
| 3-0 | EncodingParams | DataEncodingごとの追加パラメータ。 |

`UpdatePalletTable3`は上位bitからSlot0、Slot1、Slot2に対応する。

インデックス列は、先頭を`InitialIndex`とし、2個目以降を1bit差分列で記録する。

```
diff[n] = (index[n] - index[n-1] - 1) mod 3
index[n] = (index[n-1] + diff[n] + 1) mod 3
```

差分列のbyte数は次の式で求める。

```
ceil((N - 1) * 1 / 8)
```

### 3.4 Palette Resolution=`10`

4値または5値のパレットを扱う。
PalletHeaderは12bitである。

| bit | フィールド | 内容 |
|---:|---|---|
| 11-9 | InitialIndex | 初期インデックス。0～4。 |
| 8-4 | UpdatePalletTable5 | Slot0～4の更新位置フラグ |
| 3-0 | EncodingParams | DataEncodingごとの追加パラメータ。 |

`UpdatePalletTable5`は上位bitからSlot0、Slot1、Slot2、Slot3、Slot4に対応する。
4値ノードでは、参照しないSlot4の更新bitは0にする。

インデックス列は、先頭を`InitialIndex`とし、2個目以降を2bit差分列で記録する。

```
diff[n] = (index[n] - index[n-1] - 1) mod 5
index[n] = (index[n-1] + diff[n] + 1) mod 5
```

差分列のbyte数は次の式で求める。

```
ceil((N - 1) * 2 / 8)
```

### 3.5 Palette Resolution=`11`

6～16値のパレットを扱う。
PalletHeaderは20bitである。

| bit | フィールド | 内容 |
|---:|---|---|
| 19-4 | UpdatePalletTable16 | Slot0～15の更新位置フラグ |
| 3-0 | EncodingParams | DataEncodingごとの追加パラメータ。 |

`UpdatePalletTable16`は上位bitからSlot0、Slot1、...、Slot15に対応する。
更新値列は、更新フラグが立ったslotの昇順で並べる。

インデックス列は、各ランのパレットインデックスを4bit即値で記録する。

インデックス列のbyte数は次の式で求める。

```
ceil(N * 4 / 8)
```

## 4. ラン長列

ラン長列は、走査順に並べたRLEランの長さである。

```
V[0], V[1], ... V[N-1]
```

各`V[i]`は正の整数であり、合計はノード画素数と一致しなければならない。

```
sum(V) == resolution * resolution
```

ラン長列自体には終端tokenを置かない。
復号時の終端判定はDataEncodingごとに異なる。

* DataEncoding=`00`では、復元したラン長値の合計が`resolution * resolution`に達するまでMBUIntを読み出す。
* DataEncoding=`01`または`10`では、先頭のラン長数`N`を読み、`N-1`個のラン長値を復元した後、末尾ラン長値を`resolution * resolution - sum(V[0] ... V[N-2])`で求める。

### 4.1 DataEncoding=`00`

ラン長列をMBUInt列として記録する。

```
[V[0]: MBUInt]
[V[1]: MBUInt]
...
[V[N-1]: MBUInt]
```

MBUInt形式は[v1/Galuchat-MBIntエンコード仕様.md](v1/Galuchat-MBIntエンコード仕様.md)を参照する。

### 4.2 DataEncoding=`01`

ラン長列をShortValueEncodingで記録する。
先頭にラン長数`N`をMBUIntで記録し、末尾ラン長値`V[N-1]`を除く`N-1`個のラン長値をbit streamで記録する。
末尾ラン長値は復号時にノード画素数から復元する。

詳細は[GI01-RleDataNode-ShortValueEncoding仕様.md](GI01-RleDataNode-ShortValueEncoding仕様.md)を参照する。

### 4.3 DataEncoding=`10`

ラン長列をSingleEdgeRowEncodingで記録する。
先頭にラン長数`N`をMBUIntで記録し、末尾ラン長値`V[N-1]`を除く`N-1`個のラン長値をbit streamで記録する。
`MBUIntReduce`を使用する場合は、ラン長数に続けて先頭ラン長値をMBUIntで記録し、中間ラン長列をbit streamで記録する。
いずれの場合も、末尾ラン長値は復号時にノード画素数から復元する。

詳細は[GI01-RleDataNode-SingleEdgeRowEncoding仕様.md](GI01-RleDataNode-SingleEdgeRowEncoding仕様.md)を参照する。

## 5. RLEデータ部

RLEデータ部は、ラン長情報`L`とパレットインデックス情報`P`で構成する。

Palette Resolution=`00`では、パレットインデックスは`InitialIndex`から計算で復元できるため、RLEデータ部にはラン長情報のみを記録する。

Palette Resolution=`01`、`10`、`11`では、`P`はPalette Resolutionごとのパレットインデックス差分または即値インデックスを表す。
DataEncoding=`00`では、RLEデータ部は`L`と`P`をラン単位で交互に配置するビットストリームとする。

```
L P L P ...
```

DataEncoding=`01`または`10`では、`L`は各DataEncodingで定義されるtoken形式に従う。
その場合、`P`の配置、`L`が生成したラン長との対応、末尾ランに対応する`P`の扱いは、各DataEncoding仕様で定義する。
本章では、`P`として記録する値の意味だけをPalette Resolutionごとに定義する。

### 5.1 Palette Resolution=`00`

```
[L列]
```

パレットインデックス列は記録しない。
インデックスは`InitialIndex`から交互に復元する。

### 5.2 Palette Resolution=`01`

`P`は1bit差分である。
各差分は直前のランのパレットインデックスから次のランのパレットインデックスを復元する。

### 5.3 Palette Resolution=`10`

`P`は2bit差分である。
各差分は直前のランのパレットインデックスから次のランのパレットインデックスを復元する。

### 5.4 Palette Resolution=`11`

`P`は4bit即値インデックスである。
各ランに対応するパレットインデックスを直接記録する。

## 6. シリアライズ全体

RLE DataNode全体は次の順序で記録する。

```
[CellHeader]
[PalletHeader]
[パレット更新値列]
[RLEデータ部]
```

`Palette Resolution=00`では、RLEデータ部に`P`は存在しない。
`Palette Resolution=01`、`10`、`11`では、DataEncoding=`00`の場合にRLEデータ部内で`L`と`P`を交互に読み出す。
DataEncoding=`01`または`10`の場合、RLEデータ部の詳細な配置は各DataEncoding仕様に従う。
RLEデータ部はbyte境界まで0でパディングし、後続データは次byteから開始する。

## 7. バイナリ例

### 7.1 DataEncoding=`00`

条件:

* 解像度: 4×4
* Palette Resolution: `10`
* DataEncoding: `00`
* ScanMode: `00`
* パレット更新: Slot0～3 = `[10, 20, 30, 40]`
* ラン長列: `[5, 6, 5]`
* インデックス列: `[3, 0, 2]`

CellHeader:

```
TYPE=10, PaletteResolution=10, DataEncoding=00, ScanMode=00
0b10100000 = 0xA0
```

PalletHeader:

```
InitialIndex=3, UpdatePalletTable5=11110, EncodingParams=0000
12bit列: 011 11110 0000
```

インデックス差分:

```
(0 - 3 - 1) mod 5 = 1
(2 - 0 - 1) mod 5 = 1
2bit列: 01 01 + padding 0000 = 0x50
```

記録順:

```
[CellHeader: 0xA0]
[PalletHeader: 12bit 011111100000]
[パレット更新値列: MBUInt 0x0A, 0x14, 0x1E, 0x28]
[ラン長列: MBUInt 0x05, 0x06, 0x05]
[インデックス差分列: 2bit列 01 01 + padding 0000]
```

### 7.2 DataEncoding=`01`

DataEncoding=`01`では、ラン長列をShortValueEncodingで記録する。
ShortValueEncodingのbit列は、ラン長列の内容とShortValueEncoding仕様に従って決まる。

CellHeaderのDataEncoding bitは`01`である。

```
TYPE=10, PaletteResolution=10, DataEncoding=01, ScanMode=00
0b10100100 = 0xA4
```

以降のPalletHeader、パレット更新値列、パレットインデックス差分列の構造はDataEncoding=`00`と同じである。
ただし、`EncodingParams` bit2はShortValueEncodingの`RunBitsAdd`、bit1-0は`VAddBits`として扱う。
ShortValueEncodingでは`EncodingParams` bit3は0にする。

### 7.3 DataEncoding=`10`

DataEncoding=`10`では、ラン長列をSingleEdgeRowEncodingで記録する。
SingleEdgeRowEncodingのbit列は、ラン長列の内容とSingleEdgeRowEncoding仕様に従って決まる。

CellHeaderのDataEncoding bitは`10`である。

```
TYPE=10, PaletteResolution=10, DataEncoding=10, ScanMode=00
0b10101000 = 0xA8
```

以降のPalletHeader、パレット更新値列、パレットインデックス差分列の構造はDataEncoding=`00`と同じである。
ただし、`EncodingParams`は`DValueFormat * 5 + MBUIntReduceCode`として扱う。

## 8. エラー条件

復号時は次をエラーとする。

* CellHeader.TYPEが`10`ではない。
* DataEncodingが`11`である。
* ラン長値が0以下である。
* 復元したラン長合計が`resolution * resolution`と一致しない。
* パレット更新指定がPalette Resolutionの容量を超える。
* 復元したパレットインデックスが対象Palette Resolutionの範囲を超える。
* PalletHeaderの予約値を使用している。
* ShortValueEncodingで、`EncodingParams` bit3が0ではない。
* SingleEdgeRowEncodingで、`EncodingParams=15`である。
* ラン長bit streamの後続データがbyte境界から開始しない。
