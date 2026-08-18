# GI01 CellHeader仕様

## 1. 概要

CellHeaderは、GI01ノードの直前に配置される1バイトの構造識別子である。
上位2bitの`TYPE`でノード種別を識別し、残り6bitは`TYPE`ごとに異なる意味を持つ。

```
bit7 bit6 | bit5 bit4 bit3 bit2 bit1 bit0
 TYPE     | TYPE依存部
```

| TYPE | ノード種別 |
|------|------------|
| `00` | ContainerNode |
| `01` | Raw DataNode |
| `10` | RLE DataNode |
| `11` | 予約 |

復号側は、必ず最初に`TYPE`を判定し、その後に対応するビット構成で下位6bitを解釈する。

## 2. TYPE=`00`: ContainerNode

ContainerNodeのCellHeaderは、子要素の保持形式と、カスケードパレットSlot0～3の更新位置を表す。

| Bit位置 | 名称 | 意味 |
|---------|------|------|
| bit7–6 | TYPE | `00` = ContainerNode |
| bit5–4 | ContainerType | `00`=混載、`01`=値のみ、`10`=単一値、`11`=予約 |
| bit3–0 | UpdatePalletTable4 | Slot0～3の更新位置フラグ |

`UpdatePalletTable4`は、上位側からSlot0、Slot1、Slot2、Slot3に対応する。
1になっているビット数が後続するパレット更新値数である。

例:

| UpdatePalletTable4 | 更新対象 |
|--------------------|----------|
| `0000` | 更新なし |
| `1000` | Slot0 |
| `1010` | Slot0、Slot2 |
| `1111` | Slot0～3 |

ContainerTypeごとの制約は次の通りである。

| ContainerType | 用途 | `UpdatePalletTable4`の有効範囲 |
|---------------|------|--------------------------------|
| `00` | 混載 | Slot0～2のみ。bit0は0 |
| `01` | 値のみ | Slot0～3 |
| `10` | 単一値 | Slot0のみ。bit2～0は0 |
| `11` | 予約 | 使用不可 |

## 3. TYPE=`01`: Raw DataNode

Raw DataNodeのCellHeaderは、Raw形式であることと、Rawデータ部の格納方式を表す。

| Bit位置 | 名称 | 意味 |
|---------|------|------|
| bit7–6 | TYPE | `01` = Raw DataNode |
| bit5–4 | Palette Resolution | `00`=1bit Raw/P、`01`=2bit Raw/P、`10`=4bit Raw/P、`11`=Raw/N |
| bit3–0 | UpdatePalletTableLow4 | Raw/Pのパレット更新フラグ下位4bit。Raw/Nでは予約0 |

Palette Resolutionの意味は次の通りである。

| Palette Resolution | 形式 | 意味 |
|--------------------|------|------|
| `00` | Raw/P | 1bitインデックス。Slot0～1を参照 |
| `01` | Raw/P | 2bitインデックス。Slot0～3を参照 |
| `10` | Raw/P | 4bitインデックス。Slot0～15を参照 |
| `11` | Raw/N | カスケードパレットを使用しないMBUInt値列 |

Raw/Pの場合、CellHeaderの直後にRaw形式ごとのパレット更新制御が続く。
Raw/Nの場合、パレット更新制御は存在せず、Rawデータ部は画素値のMBUInt列である。

Raw/Pでは、Palette Resolutionごとに`UpdatePalletTableN`を使用する。

| Palette Resolution | 更新制御 | CellHeader bit3–0 | 後続更新制御 |
|--------------------|----------|-------------------|--------------|
| `00` | UpdatePalletTable2 | bit1–0に格納。bit3–2は予約0 | なし |
| `01` | UpdatePalletTable4 | bit3–0に格納 | なし |
| `10` | UpdatePalletTable16 | 下位4bitを格納 | 上位12bit |
| `11` | なし | 予約0 | なし |

Raw/P 4bitでは、CellHeader直後に`UpdatePalletTable16`の上位12bitを記録する。
Raw/Pの詳細は[GI01-RawDataNode構造仕様.md](GI01-RawDataNode構造仕様.md)を参照する。

## 4. TYPE=`10`: RLE DataNode

RLE DataNodeのCellHeaderは、RLE形式であること、ラン値インデックスの符号化方式、走査順を表す。

| Bit位置 | 名称 | 意味 |
|---------|------|------|
| bit7–6 | TYPE | `10` = RLE DataNode |
| bit5–4 | Palette Resolution | `00`=1～2値、`01`=3値、`10`=4～5値、`11`=6～16値 |
| bit3–2 | DataEncoding | `00`=MBUInt列、`01`=ShortValueEncoding、`10`=SingleEdgeRowEncoding、`11`=予約 |
| bit1–0 | ScanMode | RLE走査順 |

GI01のRLE DataNodeは常にカスケードパレットを参照する。
Palette Resolutionはパレットの有無ではなく、ラン値インデックス列の符号化方式を表す。

| Palette Resolution | 対象パレット数 | インデックス表現 |
|--------------------|----------------|------------------|
| `00` | 1～2値 | 初期インデックスと交互展開 |
| `01` | 3値 | 初期インデックスと1bit差分 |
| `10` | 4～5値 | 初期インデックスと2bit差分 |
| `11` | 6～16値 | 4bit即値インデックス |

DataEncodingはラン長列の格納方式を表す。

| DataEncoding | ラン長列の格納方式 |
|--------------|--------------------|
| `00` | MBUInt列 |
| `01` | ShortValueEncoding |
| `10` | SingleEdgeRowEncoding |
| `11` | 予約 |

DataEncoding=`01`および`10`では、ラン長列の先頭にラン長数を記録し、末尾ラン長値を省略する。
省略された末尾ラン長値は、既知のノード画素数から復元済みラン長値の合計を引いて求める。

ScanModeは次の通りである。

| ScanMode | 走査順 |
|----------|--------|
| `00` | Zigzag |
| `01` | MirrorH → Zigzag |
| `10` | Zigzag → Transpose |
| `11` | MirrorV → Zigzag → Transpose |

RLE DataNodeではCellHeaderの直後にPalletHeaderが続く。
PalletHeaderは、Palette Resolutionごとの初期インデックス、パレット更新制御、DataEncodingごとの追加パラメータを保持する。
Palette Resolution=`00`では7bit、`01`では9bit、`10`では12bit、`11`では20bitのPalletHeaderを使用する。
詳細は[GI01-RleDataNode構造仕様.md](GI01-RleDataNode構造仕様.md)を参照する。

## 5. TYPE=`11`: 予約

TYPE=`11`は予約領域である。
GI01の現行仕様では、ノードとして使用しない。

復号側はTYPE=`11`を読み取った場合、未定義形式として扱う。

## 6. バイナリ例

| 説明 | バイナリ | バイト値 |
|------|----------|----------|
| Container / 混載 / Slot0,2更新 | `00001010` | `0x0A` |
| Container / 値のみ / Slot0～3更新 | `00011111` | `0x1F` |
| Container / 単一値 / Slot0更新 | `00101000` | `0x28` |
| Raw/P / 2bit / Slot0～3更新 | `01011111` | `0x5F` |
| Raw/N | `01110000` | `0x70` |
| RLE / 4～5値 / MBUInt列 / Zigzag | `10100000` | `0xA0` |
| RLE / 4～5値 / ShortValueEncoding / Zigzag | `10100100` | `0xA4` |
| RLE / 4～5値 / SingleEdgeRowEncoding / Zigzag | `10101000` | `0xA8` |
| RLE / 6～16値 / MBUInt列 / MirrorV→Zigzag→Transpose | `10110011` | `0xB3` |

## 7. 注意事項

* `TYPE`によって下位6bitの意味は完全に変化する。
* 予約ビットは常に0として書き込み、復号時にも0であることを検証する。
* ContainerNodeの`UpdatePalletTable4`は、旧来のパレット数ではなく更新位置フラグである。
* RawのPalette Resolution=`11`はRaw/Nを表し、カスケードパレットを使用しない。
* RLEのPalette Resolutionはパレット有無ではなく、ラン値インデックス列の符号化方式を表す。
