# チリ国勢調査District（APC2023）

[English](cl-2023-ine-gob-cl-apc-stat-distrito-censal-rev1.md) | 日本語

[データセット目次に戻る](../../datasets/README.ja.md)

## 概要

取得済み16地域のDistritalが表すチリの範囲。原典にある太平洋島嶼を含み、南極大陸の区域は含まない。 Actualización Precensal 2023（APC2023）。Censo 2024の準備用地図であり、2017年版として扱わない。

## 区域数

辞書コード単位で **2,768区域** を収録します。16 Region、56 Provincia、345 Comunaの所属を持つ2,768 Distrito censal。 上位名称は辞書階層であり、独立した画素値ではありません。対象範囲と時点の詳細はZIP内の`data-spec.md`を参照してください。

## ダウンロード

[cl-2023-ine-gob-cl-apc-stat-distrito-censal-rev1.zipをダウンロード（7.74 MiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.3/cl-2023-ine-gob-cl-apc-stat-distrito-censal-rev1.zip)

このリンクはv0.2.3の公開後に利用できます。ZIPはローカルの`release/`に作成済みです。

## 地図の解像度とサイズ

| unitInv | 南北方向の画素間隔の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 69.7 KiB |
| 1000（標準） | 約111 m | 782.4 KiB |
| 10000 | 約11 m | 7.23 MiB |

## 辞書

| GisWordBookの文字コード | サイズ |
| --- | ---: |
| UTF-8 | 35.4 KiB |
| UTF-16LE | 35.4 KiB |

同梱の`names.csv`で辞書コードと原典の識別子・名称を照合できます。地図と辞書は同じZIPから選んでください。

### GisWordBookの構造

各レコードは固定5スロットのStringSetです。

| 位置 | 意味 | 空値 |
| ---: | --- | --- |
| 1 | N_REGIONによるRegion名。 | 不可 |
| 2 | N_PROVINCIによるProvincia名。 | 不可 |
| 3 | N_COMUNAによるComuna名。 | 不可 |
| 4 | N_DISTRITOによるDistrito censal名。 | 不可 |
| 5（属性） | TIPO_DISTRによる末端Districtの都市・農村分類。 | 不可 |

実データ例（辞書コード`1`）：

```json
["TARAPACÁ","IQUIQUE","IQUIQUE","PUERTO","URBANO"]
```

地図の非ゼロ値が辞書コードです。`0`は背景で、辞書レコードを指しません。空スロットがある場合も位置を詰めません。

## 描画例

<a href="../../docs/image/cl-2023-ine-gob-cl-apc-stat-distrito-censal-unit-inv-1000.png"><img src="../../docs/image/cl-2023-ine-gob-cl-apc-stat-distrito-censal-unit-inv-1000.png" alt="Santiago付近のチリ国勢調査District（APC2023）" width="640"></a>

Santiago付近を`unitInv=1000`で描画しました。青色は背景、その他の色は区域コードの区別を示し、色自体に別の意味はありません。

## ライセンスと利用条件

原典：[原典](https://www.ine.gob.cl/herramientas/portal-de-mapas/geodatos-abiertos)。

原典のライセンス・利用条件：**CC BY-SA 4.0 and INE terms**（[規約 1](https://creativecommons.org/licenses/by-sa/4.0/), [規約 2](https://www.ine.gob.cl/terminos-de-uso-y-licencia-de-datos-abiertos)）。ZIP内の`NOTICE.md`に出典、適用条件、帰属表示および加工内容を記録しています。

### 商用利用・許諾申請（参考）

原典が示すCC BY-SA 4.0は条件に従う商用利用を認め、加工物には継承条件があります。ライセンスが認める利用について個別申請の指定は確認していません。現行のINE条件とNOTICE.mdを確認してください。 これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。

### 出典・加工・承認表示

ZIP内の`NOTICE.md`に記載した出典・加工表示を維持してください。この加工データを原典提供者の公式・公認・推奨製品として表示しません。

## 利用上の注意

同じZIPから用途に合う地図1つとGisWordBook1つを選びます。サイズはZIP内ファイルの実サイズ、画素間隔は概算です。区域範囲、コード対応、制約はZIP内の原典文書を確認してください。
