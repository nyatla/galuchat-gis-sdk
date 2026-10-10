# Galuchat GIS SDK データセット

[English](README.md) | 日本語

SDK 0.2.4では45種類のデータセットを案内します。従来の16件は[GitHub Release v0.2.1](https://github.com/nyatla/galuchat-gis-sdk/releases/tag/v0.2.1)で配布済みです。次の16件のZIPはv0.2.2向け、続く12件はv0.2.3向け、セルビアのZIPはv0.2.4向けに準備しています。Get Startedで使用する日本行政区域2026年版はSDKにも同梱しています。

追加ガイドに記載したv0.2.2〜v0.2.4のダウンロードリンクは、それぞれの公開後に有効になります。セルビアの境界基準年は未確認のため`undated`とし、現行境界とは表示しません。

各ZIPには `data-spec.md`、`NOTICE.md`、WGSMapSet、GisWordBookを収録しています。一部には原典識別子と辞書コードの対応を示す `names.csv`、メタデータXML、原典ライセンスPDFも含まれます。データの詳細はZIP内の `data-spec.md`、出典・加工内容・利用条件は `NOTICE.md` を参照してください。

地図と辞書は必ず同じZIPの組み合わせを使用します。通常は用途に合う地図1つとUTF-8辞書を選びます。画素値0は未設定領域です。各ページに区域数、GisWordBookのスロット構造と実データ例、解像度、ファイルサイズ、表示例を掲載しています。区域数は辞書コード単位の件数を明記し、原典区域が辞書コードを共有する場合は原典区域数と区別しています。

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
| [スペイン行政区域 BDDAE 2026年版](../doc/dataset_guide/es-2026-cnig-es-lilim-adm.ja.md) | スペイン | 市町村・特殊区域 | 2026 |
| [ニュージーランド Statistical Area 2 2026年版](../doc/dataset_guide/nz-2026-stats-govt-nz-sa2-stat-sa2.ja.md) | ニュージーランド | SA2統計区域 | 2026 |
| [韓国SGIS行政洞境界 2025年第2四半期版](../doc/dataset_guide/kr-2025-sgis-mods-go-kr-admin-boundary-adm.ja.md) | 韓国 | 行政洞 | 2025 |
| [オーストリア自治体・ウィーン市区 2026年版](../doc/dataset_guide/at-2026-data-statistik-gv-at-gem-adm-rev1.ja.md) | オーストリア | 自治体・ウィーン市区 | 2026 |
| [ベルギー統計区 2026年版](../doc/dataset_guide/be-2026-statbel-fgov-be-statistical-sectors-stat-sector-rev1.ja.md) | ベルギー | 統計区 | 2026 |
| [スイスswissBOUNDARIES3D 2026年版](../doc/dataset_guide/ch-2026-swisstopo-admin-ch-swissboundaries3d-adm-rev1.ja.md) | スイス | 自治体・その他基礎区域 | 2026 |
| [チェコRÚIAN自治体区域 2026年版](../doc/dataset_guide/cz-2026-cuzk-gov-cz-ruian-adm-rev1.ja.md) | チェコ | 自治体・軍事区域 | 2026 |
| [デンマークDAGI自治体区域 2026年版](../doc/dataset_guide/dk-2026-datafordeler-dk-dagi-adm-rev1.ja.md) | デンマーク | 自治体・Christiansø | 2026 |
| [エストニア集落区域 2026年版](../doc/dataset_guide/ee-2026-geoportaal-maaamet-ee-asustusyksus-adm-rev1.ja.md) | エストニア | 集落区域 | 2026 |
| [フィンランド自治体区域 2026年版](../doc/dataset_guide/fi-2026-maanmittauslaitos-fi-kuntajako-adm-rev1.ja.md) | フィンランド | 自治体 | 2026 |
| [クロアチア集落区域 2026年版](../doc/dataset_guide/hr-2026-dgu-gov-hr-au-adm-rev1.ja.md) | クロアチア | 集落 | 2026 |
| [イタリア自治体区域 2026年版](../doc/dataset_guide/it-2026-istat-it-limiti-adm-rev1.ja.md) | イタリア | 自治体 | 2026 |
| [リトアニアINSPIRE行政区域 2026年版](../doc/dataset_guide/lt-2026-geoportal-lt-au-adm-rev1.ja.md) | リトアニア | 地区・自治体の地区未所属部分 | 2026 |
| [ラトビア住所登録行政区域 2026年版](../doc/dataset_guide/lv-2026-data-gov-lv-varis-adm-rev1.ja.md) | ラトビア | 市・Pagasts | 2026 |
| [ルーマニアANCPI地方行政区域 2025年版](../doc/dataset_guide/ro-2025-ancpi-ro-uat-adm-rev1.ja.md) | ルーマニア | UAT・ブカレストのセクター | 2025 |
| [スウェーデンRegSO統計区域 2025年版](../doc/dataset_guide/se-2025-scb-se-regso-stat-regso-rev1.ja.md) | スウェーデン | RegSO統計区域 | 2025 |
| [コートジボワール副県区域（RGPH 2021由来）](../doc/dataset_guide/ci-2021-anstat-ci-sprefectures-adm-rev1.ja.md) | Côte d’Ivoire | 副県 | 2021 |
| [キプロス行政区域（2024年8月版）](../doc/dataset_guide/cy-2024-data-gov-cy-administrative-units-adm-rev1.ja.md) | Cyprus | 行政細区画・街区 | 2024 |
| [カタール自治体区域（2015年国勢調査付属境界）](../doc/dataset_guide/qa-2015-data-gov-qa-npc-od-c0-00621-adm1-rev1.ja.md) | Qatar | 自治体 | 2015 source |
| [シンガポールMaster Plan 2019計画区域（No Sea）](../doc/dataset_guide/sg-2019-data-gov-sg-master-plan-subzone-no-sea-rev1.ja.md) | Singapore | 計画下位区域 | 2019 plan |
| [ルクセンブルク地籍区域（2026-10-05更新版）](../doc/dataset_guide/lu-2026-data-public-lu-limadmin-cadastral-section-rev1.ja.md) | Luxembourg | 地籍Section | 2026-10-05 |
| [ブラジルIBGE地区区域（Censo Demográfico 2022）](../doc/dataset_guide/br-2022-ibge-gov-br-distritos-adm-rev1.ja.md) | Brazil | 地区 | 2022 |
| [チリ国勢調査District（APC2023）](../doc/dataset_guide/cl-2023-ine-gob-cl-apc-stat-distrito-censal-rev1.ja.md) | Chile | 国勢調査District | 2023 |
| [スロベニアRPE集落区域（2026-09-27配布版）](../doc/dataset_guide/si-2026-ipi-eprostor-gov-si-rpe-adm-rev1.ja.md) | Slovenia | 集落 | 2026-09-27 |
| [リベリア行政区域（LISGIS 2022）](../doc/dataset_guide/lr-2022-lisgis-gov-lr-geography-adm-rev1.ja.md) | Liberia | Clan | 2022 |
| [アイスランド自治体区域（INSPIRE 2022年版）](../doc/dataset_guide/is-2022-natt-is-is-au-lmi-adm1-rev1.ja.md) | Iceland | 自治体 | 2022 |
| [モンテネグロ原典収録自治体区分（基準年不詳）](../doc/dataset_guide/me-undated-opendata-gov-me-opstine-adm1-rev1.ja.md) | Montenegro | 自治体区分 | Undated |
| [スロバキアZBGIS自治体区域（2026年版）](../doc/dataset_guide/sk-2026-skgeodesy-sk-zbgis-adm-rev1.ja.md) | Slovakia | 自治体レベル区域 | 2026 / 2024 exceptions |
| [セルビアGeoanalitičari集落区域（境界基準年不詳）](../doc/dataset_guide/rs-undated-data-gov-rs-hypso-struct-settl-adm-rev1.ja.md) | セルビア | 集落 | 年度不詳 |

基準年・版は配布パッケージを識別する年を示します。原典の正確な基準日や、複数原典を組み合わせたデータの時点は各ページおよびZIP内の `data-spec.md` を確認してください。
