# コートジボワール副県区域（RGPH 2021由来）

[English](ci-2021-anstat-ci-sprefectures-adm-rev1.md) | 日本語

[データセット目次に戻る](../../datasets/README.ja.md)

## 概要

原典SousPrefecture面が表すコートジボワールの範囲。 RGPH 2021に由来するSousPrefectureデータ。原典XMLの加工履歴はBaseRp2021、CI_SousPrefecture_2021、shp_2021を参照し、最終書出しは2025-10-17。2021は由来するデータの基準年度であり、取得年・書出し年ではない。

## 区域数

辞書コード単位で **510区域** を収録します。14 District、33 Région相当、111 Départementに属する510 Sous-préfecture。Région相当には31 Régionと2自治Districtを含む。 上位名称は辞書階層であり、独立した画素値ではありません。対象範囲と時点の詳細はZIP内の`data-spec.md`を参照してください。

## ダウンロード

[ci-2021-anstat-ci-sprefectures-adm-rev1.zipをダウンロード（1011.3 KiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/ci-2021-anstat-ci-sprefectures-adm-rev1.zip)

このリンクはv0.2.4の公開後に利用できます。ZIPはローカルの`release/`に作成済みです。

## 地図の解像度とサイズ

| unitInv | 南北方向の画素間隔の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 19.1 KiB |
| 1000（標準） | 約111 m | 129.2 KiB |
| 10000 | 約11 m | 919.0 KiB |

## 辞書

| GisWordBookの文字コード | サイズ |
| --- | ---: |
| UTF-8 | 5.3 KiB |
| UTF-16LE | 5.5 KiB |

同梱の`names.csv`で辞書コードと原典の識別子・名称を照合できます。地図と辞書は同じZIPから選んでください。

### GisWordBookの構造

各レコードは固定4スロットのStringSetです。

| 位置 | 意味 | 空値 |
| ---: | --- | --- |
| 1 | NomDistricによるDistrict名。 | 不可 |
| 2 | NomRegによるRégion相当名。自治Districtも含む。 | 不可 |
| 3 | NomDepによるDépartement名。 | 不可 |
| 4 | NomSpによるSous-préfecture名。 | 不可 |

実データ例（辞書コード`1`）：

```json
["COMOE","INDENIE-DJUABLIN","ABENGOUROU","ABENGOUROU"]
```

地図の非ゼロ値が辞書コードです。`0`は背景で、辞書レコードを指しません。空スロットがある場合も位置を詰めません。

## 描画例

<a href="../../docs/image/ci-2021-anstat-ci-sprefectures-adm-unit-inv-1000.png"><img src="../../docs/image/ci-2021-anstat-ci-sprefectures-adm-unit-inv-1000.png" alt="Abidjan付近のコートジボワール副県区域（RGPH 2021由来）" width="640"></a>

Abidjan付近を`unitInv=1000`で描画しました。青色は背景、その他の色は区域コードの区別を示し、色自体に別の意味はありません。

## ライセンスと利用条件

原典：[原典](https://geoportail.anstat.ci/)。

原典のライセンス・利用条件：**CC BY 4.0 and ANStat terms**（[規約 1](https://creativecommons.org/licenses/by/4.0/), [規約 2](https://www.anstat.ci/privacy)）。ZIP内の`NOTICE.md`に出典、適用条件、帰属表示および加工内容を記録しています。

### 商用利用・許諾申請（参考）

原典が示すCC BY 4.0は、条件に従う商用利用を認めています。確認した資料には、この範囲での個別許諾申請の指定はありません。用途に応じて現行の原典条件とZIP内のNOTICE.mdを確認してください。 これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。

### 出典・加工・承認表示

ZIP内の`NOTICE.md`に記載した出典・加工表示を維持してください。この加工データを原典提供者の公式・公認・推奨製品として表示しません。

## 利用上の注意

同じZIPから用途に合う地図1つとGisWordBook1つを選びます。サイズはZIP内ファイルの実サイズ、画素間隔は概算です。区域範囲、コード対応、制約はZIP内の原典文書を確認してください。
