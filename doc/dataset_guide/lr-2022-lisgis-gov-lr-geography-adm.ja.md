# リベリア行政区域（LISGIS 2022）

[English](lr-2022-lisgis-gov-lr-geography-adm.md) | 日本語

[データセット目次に戻る](../../datasets/README.ja.md)

## 概要

LISGISの詳細Clan面が表すリベリアの範囲。原典に含まれる沿岸・島状部分を保持する。 LISGIS 2022 Population and Housing Census由来の行政GIS、非simplified版、各データセットの版2022。

## 区域数

辞書コード単位で **902区域** を収録します。15 County、160 Districtに属する902 Clan。 上位名称は辞書階層であり、独立した画素値ではありません。対象範囲と時点の詳細はZIP内の`data-spec.md`を参照してください。

## ダウンロード

[lr-2022-lisgis-gov-lr-geography-adm-rev1.zipをダウンロード（695.2 KiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/lr-2022-lisgis-gov-lr-geography-adm-rev1.zip)

このリンクはv0.2.4の公開後に利用できます。ZIPはローカルの`release/`に作成済みです。

## 地図の解像度とサイズ

| unitInv | 南北方向の画素間隔の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 13.6 KiB |
| 1000（標準） | 約111 m | 90.1 KiB |
| 10000 | 約11 m | 588.9 KiB |

## 辞書

| GisWordBookの文字コード | サイズ |
| --- | ---: |
| UTF-8 | 13.8 KiB |
| UTF-16LE | 13.8 KiB |

同梱の`names.csv`で辞書コードと原典の識別子・名称を照合できます。地図と辞書は同じZIPから選んでください。

### GisWordBookの構造

各レコードは固定3スロットのStringSetです。

| 位置 | 意味 | 空値 |
| ---: | --- | --- |
| 1 | 親Districtが属するCountyの原典name。 | 不可 |
| 2 | Clanのparent_codeが指すDistrictの原典name。 | 不可 |
| 3 | Clanの原典name。 | 不可 |

実データ例（辞書コード`1`）：

```json
["Bomi","Klay","Gorblah"]
```

地図の非ゼロ値が辞書コードです。`0`は背景で、辞書レコードを指しません。空スロットがある場合も位置を詰めません。

## 描画例

<a href="../../docs/image/lr-2022-lisgis-gov-lr-geography-adm-unit-inv-1000.png"><img src="../../docs/image/lr-2022-lisgis-gov-lr-geography-adm-unit-inv-1000.png" alt="Monrovia付近のリベリア行政区域（LISGIS 2022）" width="640"></a>

Monrovia付近を`unitInv=1000`で描画しました。青色は背景、その他の色は区域コードの区別を示し、色自体に別の意味はありません。

## ライセンスと利用条件

原典：[原典 1](https://lisgis.gov.lr/data), [原典 2](https://lisgis.gov.lr/api/datasets), [原典 3](https://lisgis.gov.lr/data/api)。

原典のライセンス・利用条件：**CC BY 4.0 / LISGIS Open Data License**（[規約 1](https://creativecommons.org/licenses/by/4.0/), [規約 2](https://lisgis.gov.lr/open-data-license)）。ZIP内の`NOTICE.md`に出典、適用条件、帰属表示および加工内容を記録しています。

### 商用利用・許諾申請（参考）

原典が示すCC BY 4.0は、条件に従う商用利用を認めています。確認した資料には、この範囲での個別許諾申請の指定はありません。用途に応じて現行の原典条件とZIP内のNOTICE.mdを確認してください。 これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。

### 出典・加工・承認表示

ZIP内の`NOTICE.md`に記載した出典・加工表示を維持してください。この加工データを原典提供者の公式・公認・推奨製品として表示しません。

## 利用上の注意

同じZIPから用途に合う地図1つとGisWordBook1つを選びます。サイズはZIP内ファイルの実サイズ、画素間隔は概算です。区域範囲、コード対応、制約はZIP内の原典文書を確認してください。
