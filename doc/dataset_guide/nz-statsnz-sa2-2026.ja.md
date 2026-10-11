# ニュージーランド Statistical Area 2 2026年版

[English](nz-statsnz-sa2-2026.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

Stats NZのStatistical Area 2（SA2）2026年版を区域図として収録します。Meshblock Higher Geographies 2026の対応でTerritorial Authority（TA）名を付け、`[TA名, SA2名]`の名称辞書と原典コード対応表を同梱します。Regional Councilは名称階層に含めません。

## 区域数

区域数（辞書コード単位）は **2,396件** です。原典のSA2も2,396区域ですが、形状を持つ2,380区域だけが地図の描画対象です。形状なし16区域は辞書と`names.csv`には残ります。これは各解像度で実際に画素化される区域数ではありません。

## ダウンロード

[ダウンロード nz-2026-stats-govt-nz-sa2-stat-sa2-rev1.zip（2.46 MiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/nz-2026-stats-govt-nz-sa2-stat-sa2-rev1.zip)

このリンクはv0.2.4公開後に有効になります。ZIPは現在、ローカルの`release/`に準備済みです。

## 地図の解像度とサイズ

| unitInv | 1画素の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 33.2 KiB |
| 1000（標準） | 約111 m | 273.5 KiB |
| 10000 | 約11 m | 2.19 MiB |

## 名称辞書

| GisWordBook文字コード | サイズ |
| --- | ---: |
| UTF-8 | 40.7 KiB |
| UTF-16LE | 40.7 KiB |

原典SA2コードとTAコード、形状の有無は同梱の`names.csv`を参照してください。

### GisWordBookの構造

各レコードは固定2スロットのStringSetです。

| スロット | 意味 | 省略可否 |
| --- | --- | --- |
| 区域1 | Territorial Authority名。所属外は空文字列 | 可 |
| 区域2 | SA2名 | 不可 |

実データの例（辞書コード`1`）：

```json
["Far North District","North Cape"]
```

TA所属外42区域の上位名は空文字列です。所属外は水域と同義ではありません。地図の非ゼロ画素値は辞書コード、`0`は背景です。

## 表示例

<a href="../../docs/image/nz-statsnz-sa2-2026-unit-inv-1000.png"><img src="../../docs/image/nz-statsnz-sa2-2026-unit-inv-1000.png" alt="ウェリントン付近のSA2区域" width="640"></a>

ウェリントン付近を`unitInv=1000`で描画。青は背景、その他の色は区域コードを表します。水域にもSA2コードがあるため、背景色だけで水面を判定できません。

## ライセンスと利用条件

原典：[Stats NZ Statistical Area 2 2026](https://datafinder.stats.govt.nz/layer/123515-statistical-area-2-2026/)と[Meshblock Higher Geographies 2026](https://services2.arcgis.com/vKb0s8tBIA3bdocZ/ArcGIS/rest/services/Meshblock_Higher_Geographies_2026/FeatureServer/0)。

原典の利用条件は[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)および[Stats NZの著作権・帰属表示案内](https://www.stats.govt.nz/about-us/copyright/)を参照してください。

### 商用利用・許諾申請（参考）

CC BY 4.0は帰属等の条件に従う商用利用を認めています。ライセンスの範囲内の利用に個別の許諾申請は通常不要ですが、適用条件は利用者自身で公式規約とZIP内の`NOTICE.md`を確認してください。正式な法的判断ではありません。

### 出典・加工・承認表示

NOTICEに記載された表示：

> This work is based on/includes Stats NZ’s data which are licensed by Stats NZ for reuse under the Creative Commons Attribution 4.0 International licence.
>
> Stats NZのSA2形状・名称および2026年版TA対応を基に、座標変換、TA・SA2の名称階層化、コードの対応付け、区域図・辞書への形式変換を行った。Stats NZは本加工物を承認・推奨していない。

## 利用にあたって

地図と辞書は必ず同じZIPの組み合わせを使用してください。通常は用途に合う地図とUTF-8辞書を選びます。サイズは実ファイルサイズ、1画素の距離は緯度方向の概算です。対象範囲・制約はZIP内の`data-spec.md`、権利情報は`NOTICE.md`を参照してください。
