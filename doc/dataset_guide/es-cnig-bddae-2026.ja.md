# スペイン行政区域 BDDAE 2026年版

[English](es-cnig-bddae-2026.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

IGN/CNIGのBase de Datos de Divisiones Administrativas de España（BDDAE）の2026-07-28更新版から、通常の市町村と共有管轄地等の特殊区域を収録した区域図です。GisWordBookには自治州相当・県相当・市町村または特殊区域の名称を収録し、原典コードとの対応は`names.csv`に保持します。原典のTerritorioも独立区域として含みます。

## 区域数

区域数（辞書コード単位）は **8,220件** です。採用した原典区域も8,220件で、本版では異なる区域の名称パスの集約はありません。ポリゴン片数や各解像度で画素化される区域数ではありません。

## ダウンロード

[ダウンロード es-2026-cnig-es-lilim-adm-rev1.zip（6.76 MiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/es-2026-cnig-es-lilim-adm-rev1.zip)

このリンクはv0.2.4公開後に有効になります。ZIPは現在、ローカルの`release/`に準備済みです。

## 地図の解像度とサイズ

| unitInv | 1画素の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 118.3 KiB |
| 1000（標準） | 約111 m | 871.0 KiB |
| 10000 | 約11 m | 5.88 MiB |

## 名称辞書

| GisWordBook文字コード | サイズ |
| --- | ---: |
| UTF-8 | 110.0 KiB |
| UTF-16LE | 110.1 KiB |

原典のNATCODE・INSPIREID、区画分類、辞書コードとの対応は同梱の`names.csv`を参照してください。

### GisWordBookの構造

各レコードは固定3スロットのStringSetです。存在しない上位階層は空文字列のまま保持します。

| スロット | 意味 | 省略可否 |
| --- | --- | --- |
| 区域1 | 自治州または自治都市の原典名称 | 可 |
| 区域2 | 県または自治都市相当の原典名称 | 可 |
| 区域3 | 市町村または特殊区域の原典名称 | 不可 |

実データの例（辞書コード`1`）：

```json
["Andalucía","Almería","Abla"]
```

地図の非ゼロ画素値は辞書コードです。コード`0`は背景であり、辞書レコードではありません。GibraltarなどのTerritorio収録は原典の区域集合を踏襲するもので、領有関係について本データが判断するものではありません。

## 表示例

<a href="../../docs/image/es-cnig-bddae-2026-unit-inv-1000.png"><img src="../../docs/image/es-cnig-bddae-2026-unit-inv-1000.png" alt="マドリード付近のスペイン行政区域" width="640"></a>

マドリード付近を`unitInv=1000`で描画。青は背景、その他の色は区域コードを表します。色自体に意味はありません。

## ライセンスと利用条件

原典：Instituto Geográfico Nacional de España（IGN）／Centro Nacional de Información Geográfica（CNIG）の[BDDAE・LILIM](https://centrodedescargas.cnig.es/CentroDescargas/catalogo.do?Serie=LILIM)。

原典の利用条件は[IGNの利用条件](https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf)および[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)を参照してください。帰属・ライセンスへのリンク・変更表示が必要です。

### 商用利用・許諾申請（参考）

CC BY 4.0は帰属等の条件に従う商用利用を認めています。ライセンスの範囲内の利用に個別の許諾申請は通常不要ですが、適用条件は利用者自身で公式規約とZIP内の`NOTICE.md`を確認してください。正式な法的判断ではありません。

### 出典・加工・承認表示

NOTICEに記載された表示：

> Obra derivada de BDLJE Continua CC-BY 4.0 [ign.es](https://www.ign.es/)
>
> IGN/CNIGの2026-07-28更新版をもとに、区域・名称の統合、階層の正規化、値の再割当およびGaluchat用の形式変換を行った。

## 利用にあたって

地図と辞書は必ず同じZIPの組み合わせを使用してください。通常は用途に合う地図とUTF-8辞書を選びます。サイズは実ファイルサイズ、1画素の距離は緯度方向の概算です。対象範囲・名称・制約はZIP内の`data-spec.md`、権利情報は`NOTICE.md`を参照してください。
