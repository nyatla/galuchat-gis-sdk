# ドイツ行政区域 VG250 2026年版

[English](de-2026-gdz-bkg-bund-de-vg250-adm.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

BKGのVG250（2026-01-01版）を基に、ドイツのGemeindeおよび自治体非所属区域をGisWordBookコードで参照する区域図と名称辞書として収録する。名称は原典のまま保持し、自治体非所属区域を同名の自治体へ統合しない。区域図の非ゼロ画素値は同梱辞書のコードであり、原典AGSとの対応はnames.csvで確認できる。

## 区域数

区域数（辞書コード単位）は **10,939件** です。これはGisWordBookの葉レコード数であり、上位区域数・ポリゴン数・各解像度で実際に画素化される区域数ではありません。

採用するGemeinde・Gemeindefreies Gebietは10,939区域です。

## ダウンロード

[ダウンロード de-2026-gdz-bkg-bund-de-vg250-adm.zip (7.96 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/de-2026-gdz-bkg-bund-de-vg250-adm.zip)

## 地図の解像度とサイズ

| unitInv | 1画素の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 124.7 KiB |
| 1000（標準） | 約111 m | 1015.5 KiB |
| 10000 | 約11 m | 6.92 MiB |

## 名称辞書

| GisWordBook文字コード | サイズ |
| --- | ---: |
| UTF-8 | 193.7 KiB |
| UTF-16LE | 193.6 KiB |

原典の区域識別子との対応は同梱の `names.csv` を参照してください。

### GisWordBookの構造

各レコードは6スロットの固定長StringSetです。下表の順に値が並びます。空欄は `""` として保持し、後続スロットを前へ詰めません。

| スロット | 意味 | 省略可否 |
| --- | --- | --- |
| 区域1 | Landの原典名称。 | 不可 |
| 区域2 | Regierungsbezirkの原典名称。原典に対応する階層がなければ空文字列。 | 可 |
| 区域3 | KreisまたはKreisfreie Stadtの原典名称。 | 不可 |
| 区域4 | Verwaltungsgemeinschaft等の原典名称。 | 可 |
| 区域5 | GemeindeまたはGemeindefreies Gebietの原典名称。 | 不可 |
| 属性1 | 最下位区域種別`GEM_TYPE`。本版は`Gemeinde`、`Stadt`、`Gemeindefreies Gebiet`。 | 不可 |

スロットは`[LAND_NAME, RBZ_NAME, KRS_NAME, VWG_NAME, GEM_NAME, GEM_TYPE]`の順で6個を保持する。省略可能な階層が欠けても詰めずに空文字列を格納する。国名`Deutschland`と原典コードはStringSetに含めない。

区域4は、実際の自治体連合の名称だけでなく、原典の対応表が設けたGemeinschaftsfreie Gemeinde、Einheitsgemeinde、Gemeindefreies Gebiet等の枠も含む。そのため、同じ自治体名が区域3〜5へ繰り返し現れても、実際に複数の組織へ所属することを意味しない。原典に名称・キーがある枠を独自に空欄へ置き換えない。

名称は原典表記を保持し、ウムラウト、ß等をASCII化しない。区域1〜5がすべて同名でも、属性1が異なる区域は別辞書コードとする。本版の同名自治体と自治体非所属区域は、この区域種別で区別される。名称へAGSや独自の識別接尾辞を付加しない。

実データの例（辞書コード `8565`）：

```json
["Berlin","","Berlin","Berlin","Berlin","Stadt"]
```

地図の非ゼロ値が辞書コードです。この例は葉レコードの0始まりインデックス `8564` に対応します。コード `0` は未設定領域で、辞書レコードではありません。

## 表示例

<a href="../../docs/image/de-admin-vg250-2026-unit-inv-1000.png"><img src="../../docs/image/de-admin-vg250-2026-unit-inv-1000.png" alt="ドイツ行政区域 VG250 2026年版" width="640"></a>

ベルリン周辺を中心に、`unitInv=1000` の地図を描画しています。青色は未設定領域、その他の色は区域コードを表します。色自体に意味はありません。

## ライセンスと利用条件

原典：Bundesamt für Kartographie und Geodäsie（BKG）[VG250](https://gdz.bkg.bund.de/index.php/default/open-data/verwaltungsgebiete-1-250-000-stand-01-01-vg250-01-01.html)

原典ライセンス・利用条件：[Datenlizenz Deutschland – Namensnennung – Version 2.0（dl-de/by-2-0）](https://www.govdata.de/dl-de/by-2-0)、[VG250利用条件](https://sgx.geodatenzentrum.de/web_public/gdz/lizenz/deu/nutzungsbedingungen_vg250.pdf)

本パッケージは原典をGaluchat用に加工したものです。加工済みデータの利用条件は、上記の公式規約およびZIP内の `NOTICE.md` を参照してください。

### 商用利用・許諾申請（参考）

- 商用利用：dl-de/by-2-0は、条件に従う商用利用を認めています。 [公式説明](https://www.govdata.de/dl-de/by-2-0)
- 許諾申請：ライセンスが許諾するデータ利用の範囲内では、個別の利用許諾申請は原則不要です。 [公式説明](https://www.govdata.de/dl-de/by-2-0)

この説明は参考情報であり、正式な利用許諾や法的判断を示すものではありません。実際の利用方法に適用される条件・申請の要否は、利用者自身で公式規約とNOTICEを確認し、不明な場合は提供元へお問い合わせください。

### 出典・加工・承認表示

NOTICEに記載された出典・加工表示：

> © [BKG](https://www.bkg.bund.de) 2026 [dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0), Datenquellen: [https://sgx.geodatenzentrum.de/web_public/gdz/datenquellen/datenquellen_vg_nuts.pdf](https://sgx.geodatenzentrum.de/web_public/gdz/datenquellen/datenquellen_vg_nuts.pdf)
>
> Derived and processed by Galuchat. Not endorsed by BKG.

## 利用にあたって

地図と辞書は必ず同じZIPの組み合わせを使用してください。通常は用途に合うWGSMapSetを1つとUTF-8辞書を選びます。画素値0は未設定領域です。サイズは実ファイルサイズであり、実行時のメモリ使用量ではありません。1画素の距離は緯度方向の概算です。

データの対象範囲、名称・属性、制約はZIP内の `data-spec.md`、出典、加工内容、帰属表示、利用条件は `NOTICE.md` を参照してください。
