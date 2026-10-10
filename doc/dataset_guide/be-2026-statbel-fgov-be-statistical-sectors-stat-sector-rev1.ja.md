# ベルギー統計区 Statistical sectors 2026

[English](be-2026-statbel-fgov-be-statistical-sectors-stat-sector-rev1.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

ベルギーの統計区をGaluchat用の区域図と名称辞書に加工したデータです。原典と加工内容の詳細はZIP内の`data-spec.md`を参照してください。地図の非ゼロ画素値は同梱GisWordBookのコードで、原典IDとの対応は`names.csv`に収録します。

## 区域数

区域数（辞書コード単位）は **20,781件** です。原典仕様：統計区20,781区域。上位名称には3地域、10県、43行政郡、565自治体を使用する。ブリュッセル首都地域には県の所属がない。 上位階層の名称は別個の地図画素値ではありません。

## ダウンロード

[ダウンロード be-2026-statbel-fgov-be-statistical-sectors-stat-sector-rev1.zip（4.90 MiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/be-2026-statbel-fgov-be-statistical-sectors-stat-sector-rev1.zip)

このリンクはv0.2.4公開後に有効になります。ZIPはローカルに準備済みです。

## 地図の解像度とサイズ

| unitInv | 1画素の目安（南北） | ファイル | サイズ |
| ---: | ---: | --- | ---: |
| 100 | 約1.1 km | `belgium_statbel_2026-grid-512-100.wgsmapset.glc` | 52.6 KiB |
| 1000（標準） | 約111 m | `belgium_statbel_2026-grid-4096-1000.wgsmapset.glc` | 464.5 KiB |
| 10000 | 約11 m | `belgium_statbel_2026-grid-8192-10000.wgsmapset.glc` | 3.12 MiB |

## 名称辞書とGisWordBookの構造

| 文字コード | ファイル | サイズ |
| --- | --- | ---: |
| UTF-8 | `belgium_statbel_2026.giswordbook` | 509.0 KiB |
| UTF-16LE | `belgium_statbel_2026.utf16.giswordbook` | 509.0 KiB |

各レコードは固定6スロットのStringSetです。

| スロット | 意味 |
| ---: | --- |
| 1 | 地域（Region）の名称。原典の`T_REGIO_NL`。 |
| 2 | 県（Province）の名称。原典の`T_PROVI_NL`。 |
| 3 | 行政郡（Arrondissement）の名称。原典の`T_ARRD_NL`。 |
| 4 | 自治体（Municipality）の名称。原典の`T_MUN_NL`。 |
| 5 | 統計区（Statistical sector）の名称。原典の`T_SEC_NL`。 |
| 6 | 原典統計区コード`CS01012026`。同名別区域を区別する識別属性。 |

実データの例（辞書コード`1`）：

```json
["Vlaams Gewest","Provincie Antwerpen","Arrondissement Antwerpen","Aartselaar","DE LEEUWERIK","11001A01-"]
```

地図と辞書は同じZIPから組み合わせてください。画素値`0`は背景で、水面専用値ではありません。原典IDは`names.csv`で確認できます。

## 表示例

<a href="../../docs/image/be-2026-statbel-fgov-be-statistical-sectors-stat-sector-unit-inv-1000.png"><img src="../../docs/image/be-2026-statbel-fgov-be-statistical-sectors-stat-sector-unit-inv-1000.png" alt="ベルギー統計区 Statistical sectors 2026の首都付近の表示例" width="640"></a>

`unitInv=1000`の地図から描画しています。色はコードの区別用であり、特別な意味はありません。

## ライセンスと利用条件

原典：[原典配布・説明ページ](https://statbel.fgov.be/fr/open-data/secteurs-statistiques-2026)。ZIP内の`NOTICE.md`に記録された原典の条件は **Statbel Licence open data** です。[原典の利用条件](https://statbel.fgov.be/sites/default/files/files/opendata/Licence%20open%20data_FR.pdf)を確認してください。 ZIPには原典のフランス語・オランダ語ライセンスPDFも同梱します。

### 商用利用・許諾申請（参考）

掲載した条件では商用再利用が認められ、通常の再利用について別途の許諾申請はNOTICEに記載されていません。これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。実際の用途に適用される現行の公式規約とZIP内の`NOTICE.md`を確認してください。

### 出典・加工・承認表示

加工製品の再配布時は、ZIP内の`NOTICE.md`に記載された出典・加工内容の表示を維持してください。原典提供者の公式製品や承認済み製品であるかのように表示しないでください。
