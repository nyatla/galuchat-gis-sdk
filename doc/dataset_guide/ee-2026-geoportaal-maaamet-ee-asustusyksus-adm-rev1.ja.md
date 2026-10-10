# Maa- ja Ruumiamet Asustusüksused（2026-09-02）

[English](ee-2026-geoportaal-maaamet-ee-asustusyksus-adm-rev1.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

エストニアの集落区域をGaluchat用の区域図と名称辞書に加工したデータです。原典と加工内容の詳細はZIP内の`data-spec.md`を参照してください。地図の非ゼロ画素値は同梱GisWordBookのコードで、原典IDとの対応は`names.csv`に収録します。

## 区域数

区域数（辞書コード単位）は **4,715件** です。原典仕様：原典4,717図形からなる4,715の集落区域。 上位階層の名称は別個の地図画素値ではありません。

## ダウンロード

[ダウンロード ee-2026-geoportaal-maaamet-ee-asustusyksus-adm-rev1.zip（2.19 MiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.2/ee-2026-geoportaal-maaamet-ee-asustusyksus-adm-rev1.zip)

このリンクはv0.2.2公開後に有効になります。ZIPはローカルに準備済みです。

## 地図の解像度とサイズ

| unitInv | 1画素の目安（南北） | ファイル | サイズ |
| ---: | ---: | --- | ---: |
| 100 | 約1.1 km | `estonia_asustusyksus_2026-grid-512-100.wgsmapset.glc` | 44.3 KiB |
| 1000（標準） | 約111 m | `estonia_asustusyksus_2026-grid-4096-1000.wgsmapset.glc` | 284.6 KiB |
| 10000 | 約11 m | `estonia_asustusyksus_2026-grid-8192-10000.wgsmapset.glc` | 1.82 MiB |

## 名称辞書とGisWordBookの構造

| 文字コード | ファイル | サイズ |
| --- | --- | ---: |
| UTF-8 | `estonia_asustusyksus_2026.giswordbook` | 88.1 KiB |
| UTF-16LE | `estonia_asustusyksus_2026.utf16.giswordbook` | 88.2 KiB |

各レコードは固定4スロットのStringSetです。

| スロット | 意味 |
| ---: | --- |
| 1 | 原典`MNIMI`によるMaakond名。 |
| 2 | 原典`ONIMI`によるOmavalitsus名。 |
| 3 | 原典`ANIMI`によるAsustusüksus名。 |
| 4 | 原典`TYYP`の区域種別コード。 |

実データの例（辞書コード`1`）：

```json
["Harju maakond","Tallinn","Haabersti linnaosa","6"]
```

地図と辞書は同じZIPから組み合わせてください。画素値`0`は背景で、水面専用値ではありません。原典IDは`names.csv`で確認できます。

## 表示例

<a href="../../docs/image/ee-2026-geoportaal-maaamet-ee-asustusyksus-adm-unit-inv-1000.png"><img src="../../docs/image/ee-2026-geoportaal-maaamet-ee-asustusyksus-adm-unit-inv-1000.png" alt="Maa- ja Ruumiamet Asustusüksused（2026-09-02）の首都付近の表示例" width="640"></a>

`unitInv=1000`の地図から描画しています。色はコードの区別用であり、特別な意味はありません。

## ライセンスと利用条件

原典：[原典配布・説明ページ](https://geoportaal.maaamet.ee/est/ruumiandmed/haldus-ja-asustusjaotus-p119.html)。ZIP内の`NOTICE.md`に記録された原典の条件は **Provider's open-data terms** です。[原典の利用条件](https://kataster.ee/sites/default/files/documents/2024-03/MTP_andmeteenuste_kasutustingimused.pdf)を確認してください。

### 商用利用・許諾申請（参考）

原典はオープンデータとして公開されていますが、商用利用と申請要否は用途に照らして公式規約を確認してください。これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。実際の用途に適用される現行の公式規約とZIP内の`NOTICE.md`を確認してください。

### 出典・加工・承認表示

加工製品の再配布時は、ZIP内の`NOTICE.md`に記載された出典・加工内容の表示を維持してください。原典提供者の公式製品や承認済み製品であるかのように表示しないでください。
