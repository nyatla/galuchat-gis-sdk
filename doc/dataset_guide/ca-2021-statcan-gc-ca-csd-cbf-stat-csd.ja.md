# カナダCensus Subdivision 2021年版

[English](ca-2021-statcan-gc-ca-csd-cbf-stat-csd.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

Statistics Canadaの2021年Census Subdivision（CSD）Cartographic Boundary File（英語版）から、カナダ全域のCSDを表す区域図と名称辞書を収録する。CSDは自治体、Indian reserve、unorganized territoryなど、自治体相当として扱う区域の総称である。区域図の非ゼロ画素値は同梱GisWordBookのコードであり、原典のCSD識別子との対応は`names.csv`で確認できる。

## 区域数

区域数（辞書コード単位）は **5,154件** です。これはGisWordBookの葉レコード数であり、上位区域数・ポリゴン数・各解像度で実際に画素化される区域数ではありません。

採用するCSDは5,161区域、辞書レコードは5,154件です。一部の原典区域は辞書コードを共有するため、原典区域数と辞書レコード数は一致しません。

## ダウンロード

[ダウンロード ca-2021-statcan-gc-ca-csd-cbf-stat-csd.zip (25.69 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/ca-2021-statcan-gc-ca-csd-cbf-stat-csd.zip)

## 地図の解像度とサイズ

| unitInv | 1画素の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 250.1 KiB |
| 1000（標準） | 約111 m | 2.55 MiB |
| 10000 | 約11 m | 24.29 MiB |

## 名称辞書

| GisWordBook文字コード | サイズ |
| --- | ---: |
| UTF-8 | 110.5 KiB |
| UTF-16LE | 110.6 KiB |

原典の区域識別子との対応は同梱の `names.csv` を参照してください。

### GisWordBookの構造

各レコードは3スロットの固定長StringSetです。下表の順に値が並びます。空欄は `""` として保持し、後続スロットを前へ詰めません。

| スロット | 意味 | 省略可否 |
| --- | --- | --- |
| 区域1 | `PRUID`に対応する英語の州・準州名。 | 不可 |
| 区域2 | 原典の英語`CSDNAME`。 | 不可 |
| 属性1 | 原典の`CSDTYPE`。 | 不可 |

共通の`Canada`ノードは含めない。`Census Division`も名称階層には含めない。同じ3スロットの組を持つ別CSDのうち、別コードを持つものは辞書コードで区別できる。コードを共有するものの個別識別には`names.csv`の`CSDUID`を用いる。

実データの例（辞書コード `2735`）：

```json
["Ontario","Toronto","C"]
```

地図の非ゼロ値が辞書コードです。この例は葉レコードの0始まりインデックス `2734` に対応します。コード `0` は未設定領域で、辞書レコードではありません。

## 表示例

<a href="../../docs/image/ca-admin-statcan-csd-2021-unit-inv-1000.png"><img src="../../docs/image/ca-admin-statcan-csd-2021-unit-inv-1000.png" alt="カナダCensus Subdivision 2021年版" width="640"></a>

トロント周辺を中心に、`unitInv=1000` の地図を描画しています。青色は未設定領域、その他の色は区域コードを表します。色自体に意味はありません。

## ライセンスと利用条件

原典：Statistics Canada [2021 Census Boundary Files](https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21)

原典ライセンス・利用条件：[Open Government Licence – Canada 2.0](https://open.canada.ca/en/open-government-licence-canada)

本パッケージは原典をGaluchat用に加工したものです。加工済みデータの利用条件は、上記の公式規約およびZIP内の `NOTICE.md` を参照してください。

### 商用利用・許諾申請（参考）

- 商用利用：Open Government Licence – Canadaは、条件に従う商用利用を認めています。 [公式説明](https://open.canada.ca/en/open-government-licence-canada)
- 許諾申請：ライセンスが許諾するデータ利用の範囲内では、個別の利用許諾申請は原則不要です。 [公式説明](https://open.canada.ca/en/open-government-licence-canada)

この説明は参考情報であり、正式な利用許諾や法的判断を示すものではありません。実際の利用方法に適用される条件・申請の要否は、利用者自身で公式規約とNOTICEを確認し、不明な場合は提供元へお問い合わせください。

### 出典・加工・承認表示

NOTICEに記載された出典・加工表示：

> Contains information licensed under the Open Government Licence – Canada.
>
> Derived and processed by the Galuchat project. This product is not endorsed by Statistics Canada or the Government of Canada.

## 利用にあたって

地図と辞書は必ず同じZIPの組み合わせを使用してください。通常は用途に合うWGSMapSetを1つとUTF-8辞書を選びます。画素値0は未設定領域です。サイズは実ファイルサイズであり、実行時のメモリ使用量ではありません。1画素の距離は緯度方向の概算です。

データの対象範囲、名称・属性、制約はZIP内の `data-spec.md`、出典、加工内容、帰属表示、利用条件は `NOTICE.md` を参照してください。
