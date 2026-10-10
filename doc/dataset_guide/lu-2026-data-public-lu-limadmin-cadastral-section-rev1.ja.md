# ルクセンブルク地籍区域（2026-10-05更新版）

[English](lu-2026-data-public-lu-limadmin-cadastral-section-rev1.md) | 日本語

[データセット目次に戻る](../../datasets/README.ja.md)

## 概要

ルクセンブルクの原典地籍区域および原典Condominium面が表すドイツとの共同管理区域。 PCN由来のlimadmin原典、2026-10-05更新版。地籍Communeは歴史的な地籍単位であり、現行行政Communeと同一視しない。

## 区域数

辞書コード単位で **521区域** を収録します。519の地籍Sectionと2つの共同管理面、計521末端区域。通常区域の所属には12 Canton、100行政Commune、130地籍Communeを使用する。 上位名称は辞書階層であり、独立した画素値ではありません。対象範囲と時点の詳細はZIP内の`data-spec.md`を参照してください。

## ダウンロード

[lu-2026-data-public-lu-limadmin-cadastral-section-rev1.zipをダウンロード（220.6 KiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/lu-2026-data-public-lu-limadmin-cadastral-section-rev1.zip)

このリンクはv0.2.4の公開後に利用できます。ZIPはローカルの`release/`に作成済みです。

## 地図の解像度とサイズ

| unitInv | 南北方向の画素間隔の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 3.2 KiB |
| 1000（標準） | 約111 m | 23.7 KiB |
| 10000 | 約11 m | 169.1 KiB |

## 辞書

| GisWordBookの文字コード | サイズ |
| --- | ---: |
| UTF-8 | 7.3 KiB |
| UTF-16LE | 7.4 KiB |

同梱の`names.csv`で辞書コードと原典の識別子・名称を照合できます。地図と辞書は同じZIPから選んでください。

### GisWordBookの構造

各レコードは固定4スロットのStringSetです。

| 位置 | 意味 | 空値 |
| ---: | --- | --- |
| 1 | CANTONによるCanton名。 | 空文字可。共同管理面では空文字列。 |
| 2 | COMMUNE_ADによる行政Commune名。 | 空文字可。共同管理面では空文字列。 |
| 3 | COMMUNE_CAによる地籍Commune名。 | 空文字可。共同管理面では空文字列。 |
| 4 | SECTIONによる地籍Section名、またはCondominium。 | 不可 |

実データ例（辞書コード`1`）：

```json
["Redange","Rambrouch","Arsdorf","Arsdorf"]
```

地図の非ゼロ値が辞書コードです。`0`は背景で、辞書レコードを指しません。空スロットがある場合も位置を詰めません。

## 描画例

<a href="../../docs/image/lu-2026-data-public-lu-limadmin-cadastral-section-unit-inv-1000.png"><img src="../../docs/image/lu-2026-data-public-lu-limadmin-cadastral-section-unit-inv-1000.png" alt="Luxembourg City付近のルクセンブルク地籍区域（2026-10-05更新版）" width="640"></a>

Luxembourg City付近を`unitInv=1000`で描画しました。青色は背景、その他の色は区域コードの区別を示し、色自体に別の意味はありません。

## ライセンスと利用条件

原典：[原典 1](https://data.public.lu/fr/datasets/limites-administratives-du-grand-duche-de-luxembourg/), [原典 2](https://download.data.public.lu/resources/limites-administratives-du-grand-duche-de-luxembourg/20261005-031853/limadmin-shp.zip), [原典 3](https://wms.inspire.geoportail.lu/geoserver/ogc/features/v1/collections/au:AU_Condominium/items?f=application%2Fjson)。

原典のライセンス・利用条件：**CC0 1.0**（[規約](https://creativecommons.org/publicdomain/zero/1.0/)）。ZIP内の`NOTICE.md`に出典、適用条件、帰属表示および加工内容を記録しています。

### 商用利用・許諾申請（参考）

原典はCC0 1.0を示しており、その対象権利について商用利用や個別許諾申請の要件は示されていません。CC0の対象外となる権利も含め、NOTICE.mdと原典を確認してください。 これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。

### 出典・加工・承認表示

ZIP内の`NOTICE.md`に記載した出典・加工表示を維持してください。この加工データを原典提供者の公式・公認・推奨製品として表示しません。

## 利用上の注意

同じZIPから用途に合う地図1つとGisWordBook1つを選びます。サイズはZIP内ファイルの実サイズ、画素間隔は概算です。区域範囲、コード対応、制約はZIP内の原典文書を確認してください。
