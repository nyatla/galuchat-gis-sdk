# e-Stat海岸線反映区域データ

[English](jp-2026-nyatla-jp-estat-coastline.md) | 日本語

[データセット一覧へ戻る](../../datasets/README.ja.md)

## 概要

本データセットは、令和2年国勢調査の町丁・字等境界データに、N03-2026の行政区域が示す海岸線を反映した区域地図である。N03の区域外にはe-Statの小地区値を残さない。N03の区域内ではe-Statの小地区値を優先し、e-Statで区域が定義されていない地点はN03の行政区域代表値で補う。

## 区域数

区域数（辞書コード単位）は **209,445件** です。これはGisWordBookの葉レコード数であり、上位区域数・ポリゴン数・各解像度で実際に画素化される区域数ではありません。

この値は辞書収録項目の数として示しており、原典の区域数とは区別します。

## ダウンロード

[ダウンロード jp-2026-nyatla-jp-estat-coastline.zip (26.06 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/jp-2026-nyatla-jp-estat-coastline.zip)

## 地図の解像度とサイズ

| unitInv | 1画素の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 10000（標準） | 約11 m | 24.07 MiB |

## 名称辞書

| GisWordBook文字コード | サイズ |
| --- | ---: |
| UTF-8 | 1.66 MiB |
| Shift_JIS | 1.66 MiB |
| UTF-16LE | 1.66 MiB |

### GisWordBookの構造

各レコードは6スロットの固定長StringSetです。下表の順に値が並びます。空欄は `""` として保持し、後続スロットを前へ詰めません。

GisWordBookの各レコードは次の6スロットの固定長パスを持つ。国名などの共通ノードは含めない。

| スロット | 意味 | 省略可否 |
| --- | --- | --- |
| 区域1 | 都道府県 | 不可 |
| 区域2 | 郡 | 可。存在しない場合は空文字列。 |
| 区域3 | 市区町村 | 不可 |
| 区域4 | 政令指定都市の行政区 | 可。存在しない場合は空文字列。 |
| 区域5 | e-Stat小地区 | 可。行政区域代表値では空文字列。 |
| 区域6 | e-Stat下位地区 | 可。存在しない場合は空文字列。 |

区域5・6がともに空文字列の項目はN03の行政区域代表値である。e-Statの小地区はN03の行政階層の下に配置する。同じ表示名が複数あっても、全階層の組合せとコードで区別する。3種類のGisWordBookは文字エンコーディングだけが異なり、レコード順序、コードおよび論理内容は同一である。

実データの例（辞書コード `70657`）：

```json
["東京都","","千代田区","","丸の内","一丁目"]
```

地図の非ゼロ値が辞書コードです。この例は葉レコードの0始まりインデックス `70656` に対応します。コード `0` は未設定領域で、辞書レコードではありません。

## 表示例

<a href="../../docs/image/jp-gis-estat-integrated-unit-inv-10000.png"><img src="../../docs/image/jp-gis-estat-integrated-unit-inv-10000.png" alt="e-Stat海岸線反映区域データ" width="640"></a>

習志野市周辺を中心に、`unitInv=10000` の地図を描画しています。青色は未設定領域、その他の色は区域コードを表します。色自体に意味はありません。

## ライセンスと利用条件

原典：国土交通省 [N03-20260101](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html)、総務省統計局・e-Stat [令和2年国勢調査 町丁・字等境界データ](https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=A&toukeiCode=00200521&toukeiYear=2020&serveyId=A002005212020&coordsys=1&format=shape&datum=2011)

原典ライセンス・利用条件：[N03: CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)、[国土数値情報サイト利用規約](https://nlftp.mlit.go.jp/ksj/other/agreement.html)、[e-Stat利用規約（CC BY 4.0互換）](https://www.e-stat.go.jp/terms-of-use)

本パッケージは原典をGaluchat用に加工したものです。加工済みデータの利用条件は、上記の公式規約およびZIP内の `NOTICE.md` を参照してください。

### 商用利用・許諾申請（参考）

- 商用利用：N03のCC BY 4.0とe-Stat利用規約はいずれも、条件に従う商用利用を認めています。統合データには両方の原典条件が関係します。 [公式説明](https://www.e-stat.go.jp/terms-of-use)
- 許諾申請：著作権上は各原典の許諾範囲内で個別申請は原則不要です。ただし、NOTICEは本統合成果物への測量法上の承認の適用範囲を再確認すると記載しています。本パッケージの申請要否はここでは断定せず、NOTICEと国土地理院の案内を確認してください。 [公式説明](https://service.gsi.go.jp/onestop/navi/nav3/)

この説明は参考情報であり、正式な利用許諾や法的判断を示すものではありません。実際の利用方法に適用される条件・申請の要否は、利用者自身で公式規約とNOTICEを確認し、不明な場合は提供元へお問い合わせください。

### 出典・加工・承認表示

NOTICEに記載された出典・加工表示：

> 出典：国土交通省国土数値情報ダウンロードサイト（https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html）
>
> 「国土数値情報（行政区域データ）」（国土交通省）をもとにGaluchat用に加工して作成
>
> 出典：「令和2年国勢調査 町丁・字等境界データ」（総務省統計局、政府統計の総合窓口（e-Stat））をGaluchat用に加工して作成

地図と `X7115_metadata.xml` について、NOTICEに記載された承認表示（適用範囲の再確認事項あり）：

> 測量法に基づく国土地理院長承認（使用）R 8JHs 319

## 利用にあたって

地図と辞書は必ず同じZIPの組み合わせを使用してください。通常は用途に合うWGSMapSetを1つとUTF-8辞書を選びます。画素値0は未設定領域です。サイズは実ファイルサイズであり、実行時のメモリ使用量ではありません。1画素の距離は緯度方向の概算です。

データの対象範囲、名称・属性、制約はZIP内の `data-spec.md`、出典、加工内容、帰属表示、利用条件は `NOTICE.md` を参照してください。
