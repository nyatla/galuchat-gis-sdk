# DAGI V4 Kommuneinddeling（Current_217抽出版）

[English](dk-2026-datafordeler-dk-dagi-adm-rev1.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

デンマークの自治体・ChristiansøをGaluchat用の区域図と名称辞書に加工したデータです。原典と加工内容の詳細はZIP内の`data-spec.md`を参照してください。地図の非ゼロ画素値は同梱GisWordBookのコードで、原典IDとの対応は`names.csv`に収録します。

## 区域数

区域数（辞書コード単位）は **99件** です。原典仕様：通常の自治体98区域と、自治体区分外のChristiansø 1区域。 上位階層の名称は別個の地図画素値ではありません。

## ダウンロード

[ダウンロード dk-2026-datafordeler-dk-dagi-adm-rev1.zip（557.2 KiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/dk-2026-datafordeler-dk-dagi-adm-rev1.zip)

このリンクはv0.2.4公開後に有効になります。ZIPはローカルに準備済みです。

## 地図の解像度とサイズ

| unitInv | 1画素の目安（南北） | ファイル | サイズ |
| ---: | ---: | --- | ---: |
| 100 | 約1.1 km | `denmark_dagi_2026-grid-512-100.wgsmapset.glc` | 5.7 KiB |
| 1000（標準） | 約111 m | `denmark_dagi_2026-grid-4096-1000.wgsmapset.glc` | 54.2 KiB |
| 10000 | 約11 m | `denmark_dagi_2026-grid-8192-10000.wgsmapset.glc` | 511.4 KiB |

## 名称辞書とGisWordBookの構造

| 文字コード | ファイル | サイズ |
| --- | --- | ---: |
| UTF-8 | `denmark_dagi_2026.giswordbook` | 2.2 KiB |
| UTF-16LE | `denmark_dagi_2026.utf16.giswordbook` | 2.2 KiB |

各レコードは固定3スロットのStringSetです。

| スロット | 意味 |
| ---: | --- |
| 1 | Regionの原典名称。 |
| 2 | Kommuneinddelingの原典名称。 |
| 3 | `udenforkommuneinddeling`の値。`0`は通常自治体、`1`は自治体区分外。 |

実データの例（辞書コード`1`）：

```json
["Region Hovedstaden","Frederiksberg","0"]
```

地図と辞書は同じZIPから組み合わせてください。画素値`0`は背景で、水面専用値ではありません。原典IDは`names.csv`で確認できます。

## 表示例

<a href="../../docs/image/dk-2026-datafordeler-dk-dagi-adm-unit-inv-1000.png"><img src="../../docs/image/dk-2026-datafordeler-dk-dagi-adm-unit-inv-1000.png" alt="DAGI V4 Kommuneinddeling（Current_217抽出版）の首都付近の表示例" width="640"></a>

`unitInv=1000`の地図から描画しています。色はコードの区別用であり、特別な意味はありません。

## ライセンスと利用条件

原典：[原典配布・説明ページ](https://datafordeler.dk/dataoversigt/danmarks-administrative-geografiske-inddeling-dagi/dagi-fildownload/)。ZIP内の`NOTICE.md`に記録された原典の条件は **CC BY 4.0** です。[原典の利用条件](https://datafordeler.dk/vejledning/brugervilkaar/kds-geografiske-data/)を確認してください。

### 商用利用・許諾申請（参考）

掲載した条件では商用再利用が認められ、通常の再利用について別途の許諾申請はNOTICEに記載されていません。これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。実際の用途に適用される現行の公式規約とZIP内の`NOTICE.md`を確認してください。

### 出典・加工・承認表示

加工製品の再配布時は、ZIP内の`NOTICE.md`に記載された出典・加工内容の表示を維持してください。原典提供者の公式製品や承認済み製品であるかのように表示しないでください。
