# 米国County境界 2025年版

[English](us-2025-census-gov-tl-county-adm2.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

米国国勢調査局の2025年版TIGER/Line® County and Equivalent Entitiesから、50州とDistrict of ColumbiaのCountyおよびCounty Equivalentの境界を採用した区域図と名称辞書を収録する。区域図の非ゼロ画素値は同梱GisWordBookのコードであり、原典のCounty識別子との対応は`names.csv`で確認できる。

## 区域数

区域数（辞書コード単位）は **3,144件** です。これはGisWordBookの葉レコード数であり、上位区域数・ポリゴン数・各解像度で実際に画素化される区域数ではありません。

採用するCounty・County Equivalentは3,144区域です。

## ダウンロード

[ダウンロード us-2025-census-gov-tl-county-adm2.zip (7.55 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/us-2025-census-gov-tl-county-adm2.zip)

## 地図の解像度とサイズ

| unitInv | 1画素の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 166.1 KiB |
| 1000（標準） | 約111 m | 978.5 KiB |
| 10000 | 約11 m | 7.11 MiB |

## 名称辞書

| GisWordBook文字コード | サイズ |
| --- | ---: |
| UTF-8 | 21.8 KiB |
| UTF-16LE | 21.8 KiB |

原典の区域識別子との対応は同梱の `names.csv` を参照してください。

### GisWordBookの構造

各レコードは2スロットの固定長StringSetです。下表の順に値が並びます。空欄は `""` として保持し、後続スロットを前へ詰めません。

| スロット | 意味 | 省略可否 |
| --- | --- | --- |
| 区域1 | `STATEFP`に対応する英語の州・州相当区域名。 | 不可 |
| 区域2 | 原典の`NAMELSAD`による英語のCounty・County Equivalent名。 | 不可 |

共通の`United States`ノードは含めない。同じ`NAMELSAD`が異なる州で使われても、区域1と区域2の組で名称パスを区別する。

実データの例（辞書コード `1861`）：

```json
["New York","New York County"]
```

地図の非ゼロ値が辞書コードです。この例は葉レコードの0始まりインデックス `1860` に対応します。コード `0` は未設定領域で、辞書レコードではありません。

## 表示例

<a href="../../docs/image/us-admin-census-county-2025-unit-inv-1000.png"><img src="../../docs/image/us-admin-census-county-2025-unit-inv-1000.png" alt="米国County境界 2025年版" width="640"></a>

ニューヨーク周辺を中心に、`unitInv=1000` の地図を描画しています。青色は未設定領域、その他の色は区域コードを表します。色自体に意味はありません。

## ライセンスと利用条件

原典：U.S. Census Bureau [2025 TIGER/Line Shapefiles（county）](https://www.census.gov/geographies/mapping-files/2025/geo/tiger-line-file.html)

原典ライセンス・利用条件：[米国政府著作物（17 U.S.C. §105）・TIGER/Line利用上の注意](https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2025/TGRSHP2025_TechDoc_Ch1.pdf)

本パッケージは原典をGaluchat用に加工したものです。加工済みデータの利用条件は、上記の公式規約およびZIP内の `NOTICE.md` を参照してください。

### 商用利用・許諾申請（参考）

- 商用利用：米国政府著作物のデータは、商用製品を含め再利用できます。TIGER/Lineの商標等はデータとは別に扱われます。 [公式説明](https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2025/TGRSHP2025_TechDoc_Ch1.pdf)
- 許諾申請：原典データの著作権利用について、米国法上の個別許諾申請は原則不要です。商標など別の権利に関する利用は公式の注意事項を確認してください。 [公式説明](https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2025/TGRSHP2025_TechDoc_Ch1.pdf)

この説明は参考情報であり、正式な利用許諾や法的判断を示すものではありません。実際の利用方法に適用される条件・申請の要否は、利用者自身で公式規約とNOTICEを確認し、不明な場合は提供元へお問い合わせください。

### 出典・加工・承認表示

NOTICEに記載された出典・加工表示：

> Source: U.S. Census Bureau, 2025 TIGER/Line® Shapefiles, County and Equivalent Entities.
>
> Derived and processed by the Galuchat project. This product is not endorsed by the U.S. Census Bureau.

## 利用にあたって

地図と辞書は必ず同じZIPの組み合わせを使用してください。通常は用途に合うWGSMapSetを1つとUTF-8辞書を選びます。画素値0は未設定領域です。サイズは実ファイルサイズであり、実行時のメモリ使用量ではありません。1画素の距離は緯度方向の概算です。

データの対象範囲、名称・属性、制約はZIP内の `data-spec.md`、出典、加工内容、帰属表示、利用条件は `NOTICE.md` を参照してください。
