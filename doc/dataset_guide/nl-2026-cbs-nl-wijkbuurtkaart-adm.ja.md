# オランダ自治体区域 2026年版

[English](nl-2026-cbs-nl-wijkbuurtkaart-adm.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

CBSのWijk- en Buurtkaart 2026 versie 0を基に、オランダのProvincie（州）とGemeente（自治体）を名称辞書コードで参照する区域図を収録する。同じ自治体でも原典の陸地面と水域面を区別し、WATER属性を持つ別の辞書レコードとして保持する。地図の非ゼロ画素値は同梱GisWordBookのコードであり、原典コードとの対応はnames.csvに保持する。

## 区域数

区域数（辞書コード単位）は **423件** です。これはGisWordBookの葉レコード数であり、上位区域数・ポリゴン数・各解像度で実際に画素化される区域数ではありません。

自治体は342（`GEM_CODE`の異なり数）、陸地・水域を分けた採用面は423件です。423面が423辞書レコードに対応します。

## ダウンロード

[ダウンロード nl-2026-cbs-nl-wijkbuurtkaart-adm.zip (636.5 KiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/nl-2026-cbs-nl-wijkbuurtkaart-adm.zip)

## 地図の解像度とサイズ

| unitInv | 1画素の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 8.8 KiB |
| 1000（標準） | 約111 m | 68.7 KiB |
| 10000 | 約11 m | 566.8 KiB |

## 名称辞書

| GisWordBook文字コード | サイズ |
| --- | ---: |
| UTF-8 | 6.7 KiB |
| UTF-16LE | 6.7 KiB |

原典の区域識別子との対応は同梱の `names.csv` を参照してください。

### GisWordBookの構造

各レコードは3スロットの固定長StringSetです。下表の順に値が並びます。空欄は `""` として保持し、後続スロットを前へ詰めません。

| スロット | 意味 | 省略可否 |
| --- | --- | --- |
| 区域1 | Provincieの名称。 | 不可 |
| 区域2 | Gemeenteの原典名称。 | 不可 |
| 属性1 | 原典のWATER。`NEE`は陸地区分、`JA`は水域区分。 | 不可 |

スロットは`[PROV_NAME, GEM_NAME, WATER]`の順で3個を保持する。WATERは区域階層ではなく、末尾の面属性である。国名`Nederland`と原典コードはStringSetに含めない。

同じ州・自治体名でも、WATERが異なる面は別辞書コードとする。名称は原典表記を保持し、アクセント記号等をASCII化せず、原典コードや独自の識別接尾辞を付加しない。

実データの例（辞書コード `128`）：

```json
["Noord-Holland","Amsterdam","NEE"]
```

地図の非ゼロ値が辞書コードです。この例は葉レコードの0始まりインデックス `127` に対応します。コード `0` は未設定領域で、辞書レコードではありません。

## 表示例

<a href="../../docs/image/nl-admin-municipality-2026-unit-inv-1000.png"><img src="../../docs/image/nl-admin-municipality-2026-unit-inv-1000.png" alt="オランダ自治体区域 2026年版" width="640"></a>

アムステルダム周辺を中心に、`unitInv=1000` の地図を描画しています。青色は未設定領域、その他の色は区域コードを表します。色自体に意味はありません。

## ライセンスと利用条件

原典：CBS・Kadaster [Wijk- en Buurtkaart 2026](https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2026)、CBS [自治体・州対応表](https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/overig/gemeentelijke-indelingen-per-jaar/indeling-per-jaar/gemeentelijke-indeling-op-1-januari-2026)

原典ライセンス・利用条件：[CBS著作権方針（原則CC BY 4.0）](https://www.cbs.nl/en-gb/about-us/website/copyright)、[Wijk- en Buurtkaartの出典表示条件](https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2026)

本パッケージは原典をGaluchat用に加工したものです。加工済みデータの利用条件は、上記の公式規約およびZIP内の `NOTICE.md` を参照してください。

### 商用利用・許諾申請（参考）

- 商用利用：CBSの一般方針によるCC BY 4.0の適用範囲では、条件に従う商用利用が認められます。地理データの配布ページにはCBS・Kadasterの出典表示条件もあります。 [公式説明](https://www.cbs.nl/en-gb/about-us/website/copyright)
- 許諾申請：CC BY 4.0の適用範囲内では個別の著作権利用許諾申請は不要です。個別の条件がある情報については、配布ページを確認してください。 [公式説明](https://creativecommons.org/licenses/by/4.0/)

この説明は参考情報であり、正式な利用許諾や法的判断を示すものではありません。実際の利用方法に適用される条件・申請の要否は、利用者自身で公式規約とNOTICEを確認し、不明な場合は提供元へお問い合わせください。

### 出典・加工・承認表示

NOTICEに記載された出典・加工表示：

> Source: CBS and Kadaster, Wijk- en Buurtkaart 2026 versie 0.
>
> Derived and processed by Galuchat. Not endorsed by CBS or Kadaster.
>
> Source: CBS, Gemeentelijke indeling op 1 januari 2026.
>
> Derived and processed by Galuchat. Not endorsed by CBS.

## 利用にあたって

地図と辞書は必ず同じZIPの組み合わせを使用してください。通常は用途に合うWGSMapSetを1つとUTF-8辞書を選びます。画素値0は未設定領域です。サイズは実ファイルサイズであり、実行時のメモリ使用量ではありません。1画素の距離は緯度方向の概算です。

データの対象範囲、名称・属性、制約はZIP内の `data-spec.md`、出典、加工内容、帰属表示、利用条件は `NOTICE.md` を参照してください。
