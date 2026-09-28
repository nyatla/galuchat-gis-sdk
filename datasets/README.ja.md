# Galuchat GIS SDK データセット

[English](README.md) | 日本語

SDK 0.2.1の16種類のデータセットは、[GitHub Release v0.2.1](https://github.com/nyatla/galuchat-gis-sdk/releases/tag/v0.2.1)の配布対象です。Get Startedで使用する日本行政区域2026年版はSDKにも同梱しています。

各ZIPには `data-spec.md`、`NOTICE.md`、WGSMapSet、GisWordBookを収録しています。一部には原典識別子と辞書コードの対応を示す `names.csv` やメタデータXMLも含まれます。データの詳細はZIP内の `data-spec.md`、出典・加工内容・利用条件は `NOTICE.md` を参照してください。

地図と辞書は必ず同じZIPの組み合わせを使用します。通常は用途に合う地図1つとUTF-8辞書を選びます。画素値0は未設定領域です。各ページに区域数、GisWordBookのスロット構造と実データ例、ダウンロードリンク、解像度、ファイルサイズ、表示例を掲載しています。区域数は辞書コード単位の件数を明記し、原典区域が辞書コードを共有する場合は原典区域数と区別しています。

各ページの「ライセンスと利用条件」に、原典のライセンス・公式規約へのリンク、商用利用・許諾申請に関する参考情報、NOTICEの出典表示を掲載しています。正式な許諾や法的判断ではないため、利用時は自身の用途に適用される公式規約とZIP内のNOTICEを確認してください。

## データセット一覧

| データセット | 対象地域 | 区域の種類 | 基準年・版 |
| --- | --- | --- | --- |
| [日本行政区域 2024年版](../doc/dataset_guide/jp-2024-mlit-go-jp-n03-adm.ja.md) | 日本 | 行政区域 | 2024 |
| [日本行政区域 2025年版](../doc/dataset_guide/jp-2025-mlit-go-jp-n03-adm.ja.md) | 日本 | 行政区域 | 2025 |
| [日本行政区域 2026年版](../doc/dataset_guide/jp-2026-mlit-go-jp-n03-adm.ja.md)（SDK同梱） | 日本 | 行政区域 | 2026 |
| [e-Stat町丁・字等境界 2020年版](../doc/dataset_guide/jp-2020-e-stat-go-jp-a002005212020-stat-small-area.ja.md) | 日本 | 町丁・字等の統計区域 | 2020 |
| [e-Stat海岸線反映区域データ](../doc/dataset_guide/jp-2026-nyatla-jp-estat-coastline.ja.md) | 日本 | 海岸線反映小地区・行政区域 | 2026 / 2020 |
| [台湾村里界 2026年版](../doc/dataset_guide/tw-2026-maps-nlsc-gov-tw-village-adm.ja.md) | 台湾 | 村・里 | 2026 |
| [英国地方自治体地区 2025年12月版](../doc/dataset_guide/gb-2025-geoportal-statistics-gov-uk-lad-adm-bfc.ja.md) | 英国 | 地方自治体地区 | 2025 |
| [米国County境界 2025年版](../doc/dataset_guide/us-2025-census-gov-tl-county-adm2.ja.md) | 米国 | County・County Equivalent | 2025 |
| [米国State境界 2025年版](../doc/dataset_guide/us-2025-census-gov-tl-state-adm1.ja.md) | 米国 | State・State Equivalent | 2025 |
| [カナダCensus Subdivision 2021年版](../doc/dataset_guide/ca-2021-statcan-gc-ca-csd-cbf-stat-csd.ja.md) | カナダ | Census Subdivision | 2021 |
| [世界行政境界](../doc/dataset_guide/world-2024-geoboundaries-org-cgaz-adm.ja.md) | 世界 | 利用可能な最詳細行政区域 | 2024 |
| [オーストラリアSuburb・Locality 2021年版](../doc/dataset_guide/au-2021-abs-gov-au-sal-stat-sal.ja.md) | オーストラリア | Suburb・Locality（統計区域） | 2021 |
| [ドイツ行政区域 VG250 2026年版](../doc/dataset_guide/de-2026-gdz-bkg-bund-de-vg250-adm.ja.md) | ドイツ | 自治体・自治体非所属区域 | 2026 |
| [フランス行政区域 ADMIN EXPRESS COG 2026年版](../doc/dataset_guide/fr-2026-cartes-gouv-fr-admin-express-cog-adm.ja.md) | フランス | Commune・Arrondissement municipal | 2026 |
| [オランダ自治体区域 2026年版](../doc/dataset_guide/nl-2026-cbs-nl-wijkbuurtkaart-adm.ja.md) | オランダ | 自治体 | 2026 |
| [オランダ詳細区域 Wijk・Buurt 2026年版](../doc/dataset_guide/nl-2026-cbs-nl-wijkbuurtkaart-stat-buurt.ja.md) | オランダ | Wijk・Buurt（詳細区域） | 2026 |

基準年・版は配布パッケージを識別する年を示します。原典の正確な基準日や、複数原典を組み合わせたデータの時点は各ページおよびZIP内の `data-spec.md` を確認してください。
