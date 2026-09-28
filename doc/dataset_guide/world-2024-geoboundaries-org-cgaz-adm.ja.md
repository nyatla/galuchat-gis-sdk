# 世界行政境界

[English](world-2024-geoboundaries-org-cgaz-adm.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

本データセットは、geoBoundariesのComprehensive Global Administrative Zones（CGAZ）を、Galuchatのオフライン逆ジオコーディング用に加工したリリースパッケージである。各shapeGroupについて利用できる最も詳細な行政区域を選び、WGSMapSet/3の区域地図とGisWordBook/0の名称辞書として提供する。

## 区域数

区域数（辞書コード単位）は **49,349件** です。これはGisWordBookの葉レコード数であり、上位区域数・ポリゴン数・各解像度で実際に画素化される区域数ではありません。

この値は辞書収録項目の数として示しており、原典の区域数とは区別します。

## ダウンロード

[ダウンロード world-2024-geoboundaries-org-cgaz-adm.zip (22.93 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/world-2024-geoboundaries-org-cgaz-adm.zip)

## 地図の解像度とサイズ

| unitInv | 1画素の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 2.81 MiB |
| 1000（標準） | 約111 m | 20.45 MiB |

## 名称辞書

| GisWordBook文字コード | サイズ |
| --- | ---: |
| UTF-8 | 561.2 KiB |
| UTF-16LE | 561.4 KiB |

### GisWordBookの構造

各レコードは3スロットの固定長StringSetです。下表の順に値が並びます。空欄は `""` として保持し、後続スロットを前へ詰めません。

GisWordBookの各レコードは次の3スロットを持つ。`shapeName`が空の場合は、区域を識別できるように`shapeID`を使用する。

| スロット | 意味 | 省略可否 |
| --- | --- | --- |
| 区域1 | `shapeGroup`。原典の区域グループ識別子。 | 不可 |
| 属性1 | `shapeType`。採用した`ADM2`、`ADM1`、`ADM0`または`DISP`。 | 不可 |
| 区域2 | `shapeName`。空の場合は`shapeID`。 | 不可 |

世界各地の名称を収録するため、GisWordBookはUTF-8版とUTF-16LE版を提供する。CP932で表現できない名称があるため、Shift_JIS版は提供しない。

実データの例（辞書コード `20675`）：

```json
["JPN","ADM2","Chiyoda"]
```

地図の非ゼロ値が辞書コードです。この例は葉レコードの0始まりインデックス `20674` に対応します。コード `0` は未設定領域で、辞書レコードではありません。

## 表示例

<a href="../../docs/image/world-geoboundaries-cgaz-unit-inv-1000.png"><img src="../../docs/image/world-geoboundaries-cgaz-unit-inv-1000.png" alt="世界行政境界" width="640"></a>

習志野市周辺を中心に、`unitInv=1000` の地図を描画しています。青色は未設定領域、その他の色は区域コードを表します。色自体に意味はありません。

## ライセンスと利用条件

原典：William & Mary geoLab・geoBoundaries community [CGAZ](https://www.geoboundaries.org/globalDownloads.html)

原典ライセンス・利用条件：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)、[geoBoundariesライセンス表示](https://github.com/wmgeolab/geoBoundaries/blob/main/LICENSE)

本パッケージは原典をGaluchat用に加工したものです。加工済みデータの利用条件は、上記の公式規約およびZIP内の `NOTICE.md` を参照してください。

### 商用利用・許諾申請（参考）

- 商用利用：CC BY 4.0は、ライセンス条件に従う商用利用を認めています。 [公式説明](https://creativecommons.org/licenses/by/4.0/)
- 許諾申請：CC BY 4.0の許諾範囲内では、著作権者への個別申請は不要です。 [公式説明](https://creativecommons.org/licenses/by/4.0/)

この説明は参考情報であり、正式な利用許諾や法的判断を示すものではありません。実際の利用方法に適用される条件・申請の要否は、利用者自身で公式規約とNOTICEを確認し、不明な場合は提供元へお問い合わせください。

### 出典・加工・承認表示

NOTICEに記載された出典・加工表示：

> Contains information from geoBoundaries, produced by the William & Mary geoLab and the geoBoundaries community, licensed under CC BY 4.0. Adapted for Galuchat.

## 利用にあたって

地図と辞書は必ず同じZIPの組み合わせを使用してください。通常は用途に合うWGSMapSetを1つとUTF-8辞書を選びます。画素値0は未設定領域です。サイズは実ファイルサイズであり、実行時のメモリ使用量ではありません。1画素の距離は緯度方向の概算です。

データの対象範囲、名称・属性、制約はZIP内の `data-spec.md`、出典、加工内容、帰属表示、利用条件は `NOTICE.md` を参照してください。
