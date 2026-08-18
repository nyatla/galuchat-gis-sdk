# 1. 概要

`ContainerNode`は、2x2のグリッドを再帰的に構成するコンテナ型ノードである。4つの子要素は、値または子ノードを保持する。

値は最大16スロットのカスケードパレットを参照し、ContainerNodeは先頭4スロットまで更新できる。

---

# 2. CellHeader構造（TYPE = 00）

`CellHeader`はContainerNodeの先頭に配置する1バイトのヘッダである。

| Bit位置 | 名称 | 説明 |
|---|---|---|
| 7–6 | TYPE | `00` = ContainerNode |
| 5–4 | ContainerType | `00` = 混載、`01` = 値のみ、`10` = 単一値、`11` = 予約 |
| 3–0 | UpdatePalletTable4 | カスケードパレット更新フラグ |

`UpdatePalletTable4`は、ContainerNodeが参照するカスケードパレットのSlot0～3に対応する4bitの更新フラグである。
ビットは上位からSlot0、Slot1、Slot2、Slot3に対応する。
`1`のビット数が後続するMBUInt値の数を示し、値列はビットが`1`のスロットに上位側から順に反映する。
`UpdatePalletTable4=0000`の場合、カスケードパレットは更新しない。

---

# 3. 共通データ要素

## 3.1 カスケードパレット

カスケードパレットはノードのシリアライズ順で共有する。ContainerNodeはIndex 0～3を参照する。

## 3.2 PalletMask

`ContainerType=00`と`01`で使用する1バイトのマスクである。左上→右上→左下→右下の順に、4つの子要素を2bitずつ保持する。

```
| b7-b6 | b5-b4 | b3-b2 | b1-b0 |
| 子0   | 子1   | 子2   | 子3   |
```

---

# 4. ContainerType別構造

## 4.1 ContainerType=00：混載

1個以上の子ノードを持つ場合に使用する。

```
CellHeader
PalletMask
パレット更新値列（MBUInt × popcount(UpdatePalletTable4)）
子ノード列
```

PalletMaskの`00`～`10`はカスケードパレットのIndex 0～2、`11`は子ノードを示す。N種類の値を使用する場合、Indexは`0`～`N-1`を使用する。Nは1～3である。
ContainerType=00では、PalletMaskの`11`を子ノード指定に使用するため、値として参照できるのはIndex 0～2である。
したがって、UpdatePalletTable4のSlot3に対応する末尾ビットは常に`0`である。

子ノード列には、PalletMaskの`11`に対応するノードが子0から子3の順に出現する。

## 4.2 ContainerType=01：値のみ

子ノードを持たず、かつ複数の値を持つ場合に使用する。

```
CellHeader
PalletMask
パレット更新値列（MBUInt × popcount(UpdatePalletTable4)）
```

PalletMaskの`00`～`11`はカスケードパレットのIndex 0～3を示す。N種類の値を使用する場合、Indexは`0`～`N-1`を使用する。Nは1～4である。

## 4.3 ContainerType=10：単一値

4つの子要素がすべて同値の場合に使用する。

```
CellHeader
パレット更新値列（MBUInt × popcount(UpdatePalletTable4)）
```

値はカスケードパレットのIndex 0を参照し、PalletMaskは持たない。
ContainerType=10ではIndex 0のみを参照するため、UpdatePalletTable4のSlot1～3に対応する下位3bitは常に`0`である。

---

# 5. バイナリ例

以下の例では、値が1バイトで表現できるMBUIntであるものとする。

## 5.1 ContainerType=00：混載

子0～2が値`1`、`3`、`5`、子3が単一値`7`のContainerNodeである。

```
[0x0E]                         CellHeader
                               TYPE=00, ContainerType=00, UpdatePalletTable4=1110
[0x1B]                         PalletMask = 00 01 10 11
[0x01][0x03][0x05]             パレット更新値列
[0x28][0x07]                   子3のContainerType=10ノード
```

全体のバイト列は次のとおり。

```
0E 1B 01 03 05 28 07
```

## 5.2 ContainerType=01：値のみ

子0～3が値`1`、`3`、`5`、`9`のContainerNodeである。

```
[0x1F]                         CellHeader
                               TYPE=00, ContainerType=01, UpdatePalletTable4=1111
[0x1B]                         PalletMask = 00 01 10 11
[0x01][0x03][0x05][0x09]       パレット更新値列
```

全体のバイト列は次のとおり。

```
1F 1B 01 03 05 09
```

## 5.3 ContainerType=10：単一値

4つの子要素がすべて値`7`のContainerNodeである。

```
[0x28]                         CellHeader
                               TYPE=00, ContainerType=10, UpdatePalletTable4=1000
[0x07]                         パレット更新値
```

全体のバイト列は次のとおり。

```
28 07
```

## 5.4 パレット更新の省略

カスケードパレットのIndex 0がすでに`7`の場合、同じ単一値ContainerNodeは更新値を持たない。

```
[0x20]                         CellHeader
                               TYPE=00, ContainerType=10, UpdatePalletTable4=0000
```

全体のバイト列は次の1バイトとなる。

```
20
```

---
