# GI01 Raw DataNode構造仕様

## 1. 概要

Raw DataNodeは、画素列をラン長圧縮せずに記録する終端ノードである。
画素はブロック内の通常走査順で並び、Rawデータ部にそのまま格納される。

Raw形式は、値の格納方法によって次の2形式に分かれる。

* **Raw/P**: カスケードパレットを参照し、各画素をパレットインデックスとして記録する。
* **Raw/N**: カスケードパレットを使用せず、各画素値をMBUIntで直接記録する。

CellHeader.TYPEは常に`0b01`である。
CellHeaderのPalette Resolutionは、Raw/Pではインデックスのビット幅を示し、Raw/Nでは直接値列であることを示す。

| Palette Resolution | 形式 | 意味 |
|--------------------|------|------|
| `00` | Raw/P | 1bitインデックス。Slot0～1を参照 |
| `01` | Raw/P | 2bitインデックス。Slot0～3を参照 |
| `10` | Raw/P | 4bitインデックス。Slot0～15を参照 |
| `11` | Raw/N | パレット未使用。MBUInt値列 |

## 2. 構成要素

Raw DataNodeの構成要素は次の通りである。

* CellHeader（1バイト）
* 追加パレット更新制御（Raw/P 4bitの場合のみ、12bit）
* パレット更新値列（Raw/Pで更新がある場合のみ）
* Rawデータ部

Raw/Pで使用されるパレットは、ノードブロック内で共有されるカスケードパレットである。
Raw/Pは、必要に応じてカスケードパレットを更新し、更新後のスロットをインデックス列から参照する。

Raw/Nはカスケードパレットを使用しない。
Raw/Nを読み書きしても、カスケードパレットの状態は変化しない。

## 3. CellHeader構造

Raw形式におけるCellHeader（1バイト）の構造は次の通りである。

| ビット位置 | フィールド名 | 説明 |
|------------|--------------|------|
| 7–6 | TYPE | `01` = Raw形式 |
| 5–4 | Palette Resolution | `00`=1bit、`01`=2bit、`10`=4bit、`11`=Raw/N |
| 3–0 | UpdatePalletTableLow4 | Raw/Pのパレット更新フラグ下位4bit。Raw/Nでは予約0 |

Raw/Pでは、パレット更新制御をPalette Resolutionごとの`UpdatePalletTableN`として扱う。
`UpdatePalletTableN`のbitは上位側からSlot0、Slot1、...、SlotN-1に対応する。

| Palette Resolution | 更新制御 | CellHeader bit3–0 | 後続更新制御 |
|--------------------|----------|-------------------|--------------|
| `00` | UpdatePalletTable2 | bit1–0に格納。bit3–2は予約0 | なし |
| `01` | UpdatePalletTable4 | bit3–0に格納 | なし |
| `10` | UpdatePalletTable16 | 下位4bitを格納 | 上位12bit |
| `11` | なし | 予約0 | なし |

Raw/P 4bitでは、CellHeader直後に`UpdatePalletTable16High12`を12bitで記録する。

```
UpdatePalletTable16 = (UpdatePalletTable16High12 << 4) | UpdatePalletTableLow4
```

## 4. Raw/P

Raw/Pは、各画素をカスケードパレットのインデックスとして記録する形式である。
Palette Resolutionにより、インデックスのビット幅とパレット更新制御が決まる。

### 4.1 共通構造

```
[CellHeader (1バイト)]
[追加パレット更新制御 (Raw/P 4bitのみ12bit)]
[パレット更新値列 (MBUInt × 更新値数)]
[インデックス列（ビットパック）]
```

インデックス列は画素数分のインデックスを固定ビット幅で連続して並べる。
ビット列はバイトの上位ビットから左詰めで格納し、末尾が8bitに満たない場合は下位ビットを0で埋める。
読出し時、パディングビットは破棄する。

### 4.2 Palette Resolution=`00` 1bit Raw/P

1bit Raw/Pは、カスケードパレットのSlot0～1を参照する。

```
[CellHeader]
[パレット更新値列 (MBUInt × UpdatePalletTable2の1ビット数)]
[1bitインデックス列]
```

`UpdatePalletTable2`はCellHeader bit1–0に記録する。
CellHeader bit3–2は予約として0にする。
`UpdatePalletTable2`は上位側からSlot0、Slot1に対応する。

例:

| UpdatePalletTable2 | 更新対象 |
|--------------------|----------|
| `00` | 更新なし |
| `10` | Slot0 |
| `01` | Slot1 |
| `11` | Slot0、Slot1 |

### 4.3 Palette Resolution=`01` 2bit Raw/P

2bit Raw/Pは、カスケードパレットのSlot0～3を参照する。

```
[CellHeader]
[パレット更新値列 (MBUInt × UpdatePalletTable4の1ビット数)]
[2bitインデックス列]
```

`UpdatePalletTable4`はCellHeader bit3–0に記録する。
`UpdatePalletTable4`は上位側からSlot0、Slot1、Slot2、Slot3に対応する。

例:

| UpdatePalletTable4 | 更新対象 |
|--------------------|----------|
| `0000` | 更新なし |
| `1000` | Slot0 |
| `1010` | Slot0、Slot2 |
| `1111` | Slot0～3 |

### 4.4 Palette Resolution=`10` 4bit Raw/P

4bit Raw/Pは、カスケードパレットのSlot0～15を参照する。

```
[CellHeader]
[UpdatePalletTable16High12 (12bit)]
[パレット更新値列 (MBUInt × UpdatePalletTable16の1ビット数)]
[4bitインデックス列]
```

`UpdatePalletTable16`は16bitの更新位置フラグである。
下位4bitはCellHeader bit3–0に、上位12bitはCellHeader直後に記録する。

```
UpdatePalletTable16 = (UpdatePalletTable16High12 << 4) | CellHeader.bit3_0
```

`UpdatePalletTable16`は上位側からSlot0、Slot1、...、Slot15に対応する。
パレット更新値列は、更新フラグが立ったSlotの昇順で並べる。
`UpdatePalletTable16`が0の場合、カスケードパレットは変更されない。

## 5. Raw/N

Raw/Nは、カスケードパレットを使用せず、各画素値をMBUIntで直接記録する形式である。

### 5.1 バイナリ構造

```
[CellHeader]
[値列 (MBUInt × 画素数)]
```

CellHeaderのPalette Resolutionは`11`である。
Raw/Nにはパレット更新制御もパレット更新値列も存在しない。

## 6. パレット更新値列

Raw/Pのパレット更新値列は、更新制御で指定されたスロット順に並ぶ。

`UpdatePalletTable`を使用する場合、1になっているビットに対応するスロットだけを、Slot0から順に更新する。

例:

```
更新前: [10, 20, 30, 40, ...]
UpdatePalletTable4: 1010
更新値列: [1, 5]
更新後: [1, 20, 5, 40, ...]
```

4bit Raw/Pでも、`UpdatePalletTable16`の1になっているビットに対応するスロットだけを、Slot0から順に更新する。

例:

```
更新前: [10, 20, 30, 40, ...]
UpdatePalletTable16: 1010_0000_0000_0001
更新値列: [1, 5, 9]
更新後: [1, 20, 5, 40, ..., 9]
```

## 7. バイナリ例

### 7.1 Raw/P 2bit

* 解像度: 4×4（画素数16）
* CellHeader: `0b01011111`（TYPE=`01`、Palette Resolution=`01`、UpdatePalletTable4=`1111`） → `0x5F`
* パレット更新値列: `[1, 3, 5, 9]`（Slot0～3）
* インデックス列: `[0, 1, 2, 3, 0, 1, 2, 3, 3, 2, 1, 0, 3, 2, 1, 0]`
* 2bitパック: `00 01 10 11 00 01 10 11 11 10 01 00 11 10 01 00` → `[0x1B, 0x1B, 0xE4, 0xE4]`

```
[0x5F]                            ← CellHeader
[0x01][0x03][0x05][0x09]          ← パレット更新値列
[0x1B][0x1B][0xE4][0xE4]          ← 2bitインデックス列
```

### 7.2 Raw/N

* 解像度: 4×4（画素数16）
* CellHeader: `0b01110000`（TYPE=`01`、Palette Resolution=`11`） → `0x70`
* 値列: `[1, 2, 3, ..., 16]`

```
[0x70]                      ← CellHeader
[0x01][0x02][0x03][0x04]    ← 画素値1～4
[0x05][0x06][0x07][0x08]    ← 画素値5～8
[0x09][0x0A][0x0B][0x0C]    ← 画素値9～12
[0x0D][0x0E][0x0F][0x10]    ← 画素値13～16
```
