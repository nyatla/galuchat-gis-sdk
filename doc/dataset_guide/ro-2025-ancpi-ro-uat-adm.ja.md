# ルーマニアANCPI地方行政区域（2025-03-26）

[English](ro-2025-ancpi-ro-uat-adm.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

ルーマニアのUAT・ブカレストのセクターをGaluchat用の区域図と名称辞書に加工したデータです。原典と加工内容の詳細はZIP内の`data-spec.md`を参照してください。地図の非ゼロ画素値は同梱GisWordBookのコードで、原典IDとの対応は`names.csv`に収録します。

## 区域数

区域数（辞書コード単位）は **3,186件** です。原典仕様：UAT・ブカレストのセクター、計3,186区域。上位名称は41県とブカレストの42区域。 上位階層の名称は別個の地図画素値ではありません。

## ダウンロード

[ダウンロード ro-2025-ancpi-ro-uat-adm-rev1.zip（3.49 MiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/ro-2025-ancpi-ro-uat-adm-rev1.zip)

このリンクはv0.2.4公開後に有効になります。ZIPはローカルに準備済みです。

## 地図の解像度とサイズ

| unitInv | 1画素の目安（南北） | ファイル | サイズ |
| ---: | ---: | --- | ---: |
| 100 | 約1.1 km | `romania_uat_2025-grid-512-100.wgsmapset.glc` | 57.6 KiB |
| 1000（標準） | 約111 m | `romania_uat_2025-grid-4096-1000.wgsmapset.glc` | 438.0 KiB |
| 10000 | 約11 m | `romania_uat_2025-grid-8192-10000.wgsmapset.glc` | 3.09 MiB |

## 名称辞書とGisWordBookの構造

| 文字コード | ファイル | サイズ |
| --- | --- | ---: |
| UTF-8 | `romania_uat_2025.giswordbook` | 37.3 KiB |
| UTF-16LE | `romania_uat_2025.utf16.giswordbook` | 37.4 KiB |

各レコードは固定3スロットのStringSetです。

| スロット | 意味 |
| ---: | --- |
| 1 | Județ（県）または同格のブカレストの名称。県原典のname。 |
| 2 | UATまたはブカレストのセクターの名称。UAT原典のname。 |
| 3 | 末端区域の種類。UAT原典のnatLevName。 |

実データの例（辞書コード`1`）：

```json
["ALBA","CIUGUD","Comuna"]
```

地図と辞書は同じZIPから組み合わせてください。画素値`0`は背景で、水面専用値ではありません。原典IDは`names.csv`で確認できます。

## 表示例

<a href="../../docs/image/ro-2025-ancpi-ro-uat-adm-unit-inv-1000.png"><img src="../../docs/image/ro-2025-ancpi-ro-uat-adm-unit-inv-1000.png" alt="ルーマニアANCPI地方行政区域（2025-03-26）の首都付近の表示例" width="640"></a>

`unitInv=1000`の地図から描画しています。色はコードの区別用であり、特別な意味はありません。

## ライセンスと利用条件

原典：[原典配布・説明ページ](https://geoportal.ancpi.ro/portal/apps/webappviewer/index.html?id=faeba2d173374445b1f13512bd477bb2)。ZIP内の`NOTICE.md`に記録された原典の条件は **OGL ROU 1.0 / ANCPI open-information licence** です。[原典の利用条件](https://geoportal.ancpi.ro/portal/sharing/rest/content/items/8077dd16e957477d9cc9b457f5f17cac/data)を確認してください。

### 商用利用・許諾申請（参考）

掲載した条件では商用再利用が認められ、通常の再利用について別途の許諾申請はNOTICEに記載されていません。これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。実際の用途に適用される現行の公式規約とZIP内の`NOTICE.md`を確認してください。

### 出典・加工・承認表示

加工製品の再配布時は、ZIP内の`NOTICE.md`に記載された出典・加工内容の表示を維持してください。原典提供者の公式製品や承認済み製品であるかのように表示しないでください。
