# スロバキアZBGIS自治体区域（2026年版）

[English](sk-2026-skgeodesy-sk-zbgis-adm-rev1.md) | 日本語

[データセット目次に戻る](../../datasets/README.ja.md)

## 概要

原典のobec_0面が表すスロバキア全域。軍事区域、島状部分、飛地および原典区域に含まれる水面を含む。 ZBGIS行政界の基本レベルah_shp_0.zip。原則2026-06-30、8郡は2024-12-31時点。例外郡は第5章に記載する。

## 区域数

辞書コード単位で **2,927区域** を収録します。Obecレベルの2,927区域。上位名称は8のKrajと79のOkres。 上位名称は辞書階層であり、独立した画素値ではありません。対象範囲と時点の詳細はZIP内の`data-spec.md`を参照してください。

## ダウンロード

[sk-2026-skgeodesy-sk-zbgis-adm-rev1.zipをダウンロード（1.61 MiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/sk-2026-skgeodesy-sk-zbgis-adm-rev1.zip)

このリンクはv0.2.4の公開後に利用できます。ZIPはローカルの`release/`に作成済みです。

## 地図の解像度とサイズ

| unitInv | 南北方向の画素間隔の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 28.4 KiB |
| 1000（標準） | 約111 m | 199.8 KiB |
| 10000 | 約11 m | 1.34 MiB |

## 辞書

| GisWordBookの文字コード | サイズ |
| --- | ---: |
| UTF-8 | 42.6 KiB |
| UTF-16LE | 42.7 KiB |

同梱の`names.csv`で辞書コードと原典の識別子・名称を照合できます。地図と辞書は同じZIPから選んでください。

### GisWordBookの構造

各レコードは固定3スロットのStringSetです。

| 位置 | 意味 | 空値 |
| ---: | --- | --- |
| 1 | Kraj（地域）の名称NM2。 | 不可 |
| 2 | Okres（郡）の名称NM3。 | 不可 |
| 3 | Obecレベルの区域の名称NM4。都市内区域・軍事区域を含む。 | 不可 |

実データ例（辞書コード`1`）：

```json
["Nitriansky","Nitra","Nitra"]
```

地図の非ゼロ値が辞書コードです。`0`は背景で、辞書レコードを指しません。空スロットがある場合も位置を詰めません。

## 描画例

<a href="../../docs/image/sk-2026-skgeodesy-sk-zbgis-adm-unit-inv-1000.png"><img src="../../docs/image/sk-2026-skgeodesy-sk-zbgis-adm-unit-inv-1000.png" alt="Bratislava付近のスロバキアZBGIS自治体区域（2026年版）" width="640"></a>

Bratislava付近を`unitInv=1000`で描画しました。青色は背景、その他の色は区域コードの区別を示し、色自体に別の意味はありません。

## ライセンスと利用条件

原典：[原典](https://www.gku.sk/gku/produkty-sluzby/na-stiahnutie/zbgis.html)。

原典のライセンス・利用条件：**CC BY 4.0 and provider terms**（[規約 1](https://creativecommons.org/licenses/by/4.0/), [規約 2](https://www.gku.sk/gku/produkty-sluzby/na-stiahnutie/zbgis.html)）。ZIP内の`NOTICE.md`に出典、適用条件、帰属表示および加工内容を記録しています。

### 商用利用・許諾申請（参考）

原典が示すCC BY 4.0は、条件に従う商用利用を認めています。確認した資料には、この範囲での個別許諾申請の指定はありません。用途に応じて現行の原典条件とZIP内のNOTICE.mdを確認してください。 これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。

### 出典・加工・承認表示

ZIP内の`NOTICE.md`に記載した出典・加工表示を維持してください。この加工データを原典提供者の公式・公認・推奨製品として表示しません。

## 利用上の注意

同じZIPから用途に合う地図1つとGisWordBook1つを選びます。サイズはZIP内ファイルの実サイズ、画素間隔は概算です。区域範囲、コード対応、制約はZIP内の原典文書を確認してください。
