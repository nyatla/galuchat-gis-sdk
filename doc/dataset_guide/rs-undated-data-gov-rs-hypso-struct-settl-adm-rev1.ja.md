# セルビアGeoanalitičari集落区域（境界基準年不詳）

[English](rs-undated-data-gov-rs-hypso-struct-settl-adm-rev1.md) | 日本語

[データセット目次に戻る](../../datasets/README.ja.md)

## 概要

GeoanalitičariのHypso_Struct_Settl配布物を基にした集落区域です。配布物の公開日は2021-06-18ですが、境界自体の基準年は確認できません。`undated`は基準年不詳を示し、現行の境界という意味ではありません。原典はコソボを収録していません。これは原典の対象範囲の説明であり、政治的地位の判断ではありません。

## 区域数

辞書コード単位で **4,721集落** を収録します。自治体名は辞書の親階層であり、別の画素値ではありません。`names.csv`は辞書コードと原典の集落ID `MatBrNas`、自治体ID `MatBrO`を対応付けます。

## ダウンロード

[rs-undated-data-gov-rs-hypso-struct-settl-adm-rev1.zipをダウンロード（2.47 MiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/rs-undated-data-gov-rs-hypso-struct-settl-adm-rev1.zip)

このリンクはv0.2.4の公開後に利用できます。ZIPはローカルの`release/`に作成済みです。

## 地図の解像度とサイズ

| unitInv | 南北方向の画素間隔の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 43.1 KiB |
| 1000（標準） | 約111 m | 300.5 KiB |
| 10000 | 約11 m | 2.08 MiB |

## 辞書

| GisWordBookの文字コード | サイズ |
| --- | ---: |
| UTF-8 | 33.5 KiB |
| UTF-16LE | 33.5 KiB |

### GisWordBookの構造

各レコードは原典のキリル文字名称を使用する固定2スロットのStringSetです。

| 位置 | 意味 | 空値 |
| ---: | --- | --- |
| 区域1 | 自治体名（`ImeOpsCir`） | 不可 |
| 区域2 | 集落名（`ImeNasCir`） | 不可 |

実データ例（辞書コード`1`）：

```json
["АЛЕКСАНДРОВАЦ","АЛЕКСАНДРОВАЦ"]
```

地図の非ゼロ値が辞書コードです。`0`は背景で、水域専用の値ではありません。地図と辞書は同じZIPから選んでください。

## 描画例

<a href="../../docs/image/rs-undated-data-gov-rs-hypso-struct-settl-adm-unit-inv-1000.png"><img src="../../docs/image/rs-undated-data-gov-rs-hypso-struct-settl-adm-unit-inv-1000.png" alt="ベオグラード中心部付近の集落区域" width="640"></a>

ベオグラード中心部付近を`unitInv=1000`で描画しました。青色は背景、その他の色は区域コードの区別を示し、色自体に別の意味はありません。

## ライセンスと利用条件

原典：[セルビア政府オープンデータポータル](https://data.gov.rs/sr/datasets/khipsometrijska-struktura-visinske-zone-opshtina-i-naselja/)、[Geoanalitičariの配布物](https://geoanaliticari.github.io/depopulacija/data/Indicator_6/Hypso_Struct_Settl.zip)。

原典ライセンス：[Serbian Open Data License 1.0（SODL）](https://data.gov.rs/sr/terms/)。ZIP内の`NOTICE.md`に出典の経緯、帰属表示、取得日と加工内容を記録しています。

### 商用利用・許諾申請（参考）

原典が示すSODLは、条件に従う商用利用を認めています。確認した規約には、その許諾範囲での個別申請の指定はありません。これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。利用時は現行の公式規約とZIP内の`NOTICE.md`を確認してください。

### 出典・加工・承認表示

`NOTICE.md`に記載した提供者、取得元URL、取得日、加工内容を維持してください。同文書は配布者の説明に従ってGeoSrbija/RGZを境界の由来として記載しますが、RGZから直接配布されたものや提供者の承認を受けたものとは表示しません。

## 利用上の注意

ZIPには地図3解像度、UTF-8・UTF-16LEのGisWordBook、`names.csv`、`data-spec.md`、`NOTICE.md`を収録します。上記サイズはZIP内ファイルの実サイズです。標高統計は収録せず、この区域図は法的な境界を確定するものではありません。
