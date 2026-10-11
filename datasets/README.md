# Galuchat GIS SDK datasets

English | [日本語](README.ja.md)

SDK 0.2.4 indexes 45 dataset releases. The original 16 were distributed without revision suffixes in [v0.2.1](https://github.com/nyatla/galuchat-gis-sdk/releases/tag/v0.2.1). The current SDK prepares revision-suffixed ZIPs for all 45 datasets in v0.2.4, including those 16 and 29 additional datasets. The Japanese administrative-area dataset for 2026 is also bundled with the SDK for its Get Started examples.

The direct v0.2.4 download links will work after that release is published. Serbia's boundary reference year remains unconfirmed and is labelled `undated`; this does not imply current boundaries.

Each ZIP contains `data-spec.md`, `NOTICE.md`, WGSMapSet files and GisWordBooks. Some also include `names.csv` mapping source identifiers to dictionary codes, metadata XML, or source licence PDFs. Read `data-spec.md` for the full data specification and `NOTICE.md` for sources, processing and terms of use.

Always pair a map and dictionary from the same ZIP. Typically choose one map at a suitable resolution and the UTF-8 dictionary. Pixel value 0 denotes an unset area. Each dataset page includes area counts, GisWordBook slot structures and actual data examples, resolutions, file sizes and rendering examples. Counts explicitly identify the dictionary-code unit and distinguish source-area counts where source areas share dictionary codes.

Each page's "License and terms of use" section links to the original-data license and official terms, provides informational notes on commercial use and permission applications, and lists attribution notices from the NOTICE. These notes are not a formal grant of permission or a legal determination; check the official terms and the ZIP's NOTICE for your intended use.

## Dataset index

| Dataset | Region | Area type | Reference year / edition |
| --- | --- | --- | --- |
| [Japanese administrative areas, 2024](../doc/dataset_guide/jp-admin-n03-2024.md) | Japan | Administrative areas | 2024 |
| [Japanese administrative areas, 2025](../doc/dataset_guide/jp-admin-n03-2025.md) | Japan | Administrative areas | 2025 |
| [Japanese administrative areas, 2026](../doc/dataset_guide/jp-admin-n03-2026.md) (bundled with SDK) | Japan | Administrative areas | 2026 |
| [Japanese e-Stat small areas, 2020](../doc/dataset_guide/jp-estat-r2ka-2020.md) | Japan | Census small areas | 2020 |
| [Japanese e-Stat areas with N03 coastline](../doc/dataset_guide/jp-gis-estat-integrated.md) | Japan | Small areas with N03 coastline | 2026 / 2020 |
| [Taiwan village boundaries, 2026](../doc/dataset_guide/tw-admin-nlsc-village-2026.md) | Taiwan | Villages | 2026 |
| [UK local authority districts, December 2025](../doc/dataset_guide/uk-admin-ons-lad-2025.md) | United Kingdom | Local authority districts | 2025 |
| [U.S. counties and county equivalents, 2025](../doc/dataset_guide/us-admin-census-county-2025.md) | United States | Counties and equivalents | 2025 |
| [U.S. states and state equivalents, 2025](../doc/dataset_guide/us-admin-census-state-2025.md) | United States | States and equivalents | 2025 |
| [Canadian census subdivisions, 2021](../doc/dataset_guide/ca-admin-statcan-csd-2021.md) | Canada | Census subdivisions | 2021 |
| [Worldwide administrative boundaries](../doc/dataset_guide/world-geoboundaries-cgaz.md) | Worldwide | Best-available administrative areas | 2024 |
| [Australian suburbs and localities, 2021](../doc/dataset_guide/au-abs-asgs-sal-2021.md) | Australia | Suburbs and localities (statistical) | 2021 |
| [German administrative areas, VG250 2026](../doc/dataset_guide/de-admin-vg250-2026.md) | Germany | Municipalities and unincorporated areas | 2026 |
| [French administrative areas, ADMIN EXPRESS COG 2026](../doc/dataset_guide/fr-admin-express-cog-2026.md) | France | Communes and municipal arrondissements | 2026 |
| [Dutch municipalities, 2026](../doc/dataset_guide/nl-admin-municipality-2026.md) | Netherlands | Municipalities | 2026 |
| [Dutch districts and neighbourhoods, 2026](../doc/dataset_guide/nl-stat-buurt-2026.md) | Netherlands | Districts and neighbourhoods | 2026 |
| [Spanish administrative areas, BDDAE 2026](../doc/dataset_guide/es-cnig-bddae-2026.md) | Spain | Municipalities and special areas | 2026 |
| [New Zealand Statistical Area 2, 2026](../doc/dataset_guide/nz-statsnz-sa2-2026.md) | New Zealand | SA2 statistical areas | 2026 |
| [South Korean SGIS administrative dongs, 2025 Q2](../doc/dataset_guide/kr-sgis-admin-2025.md) | South Korea | Administrative dongs | 2025 |
| [Austrian municipalities and Vienna districts, 2026](../doc/dataset_guide/at-2026-data-statistik-gv-at-gem-adm.md) | Austria | Municipalities and Vienna districts | 2026 |
| [Belgian statistical sectors, 2026](../doc/dataset_guide/be-2026-statbel-fgov-be-statistical-sectors-stat-sector.md) | Belgium | Statistical sectors | 2026 |
| [Swiss swissBOUNDARIES3D base areas, 2026](../doc/dataset_guide/ch-2026-swisstopo-admin-ch-swissboundaries3d-adm.md) | Switzerland | Municipalities and other base areas | 2026 |
| [Czech RÚIAN municipalities, 2026](../doc/dataset_guide/cz-2026-cuzk-gov-cz-ruian-adm.md) | Czechia | Municipalities and military areas | 2026 |
| [Danish DAGI municipalities, 2026](../doc/dataset_guide/dk-2026-datafordeler-dk-dagi-adm.md) | Denmark | Municipalities and Christiansø | 2026 |
| [Estonian settlement units, 2026](../doc/dataset_guide/ee-2026-geoportaal-maaamet-ee-asustusyksus-adm.md) | Estonia | Settlement units | 2026 |
| [Finnish municipal divisions, 2026](../doc/dataset_guide/fi-2026-maanmittauslaitos-fi-kuntajako-adm.md) | Finland | Municipalities | 2026 |
| [Croatian settlements, 2026](../doc/dataset_guide/hr-2026-dgu-gov-hr-au-adm.md) | Croatia | Settlements | 2026 |
| [Italian municipalities, 2026](../doc/dataset_guide/it-2026-istat-it-limiti-adm.md) | Italy | Municipalities | 2026 |
| [Lithuanian INSPIRE administrative units, 2026](../doc/dataset_guide/lt-2026-geoportal-lt-au-adm.md) | Lithuania | Elderships and municipality remainders | 2026 |
| [Latvian administrative areas, 2026](../doc/dataset_guide/lv-2026-data-gov-lv-varis-adm.md) | Latvia | Cities and parishes | 2026 |
| [Romanian ANCPI local administrative areas, 2025](../doc/dataset_guide/ro-2025-ancpi-ro-uat-adm.md) | Romania | UAT and Bucharest sectors | 2025 |
| [Swedish RegSO statistical areas, 2025](../doc/dataset_guide/se-2025-scb-se-regso-stat-regso.md) | Sweden | RegSO statistical areas | 2025 |
| [Côte d’Ivoire sub-prefecture boundaries (RGPH 2021-derived)](../doc/dataset_guide/ci-2021-anstat-ci-sprefectures-adm.md) | Côte d’Ivoire | Sub-prefectures | 2021 |
| [Cyprus administrative units (August 2024)](../doc/dataset_guide/cy-2024-data-gov-cy-administrative-units-adm.md) | Cyprus | Local units and quarters | 2024 |
| [Qatar municipalities (2015 census source)](../doc/dataset_guide/qa-2015-data-gov-qa-npc-od-c0-00621-adm1.md) | Qatar | Municipalities | 2015 source |
| [Singapore Master Plan 2019 subzones (No Sea)](../doc/dataset_guide/sg-2019-data-gov-sg-master-plan-subzone-no-sea.md) | Singapore | Planning subzones | 2019 plan |
| [Luxembourg cadastral sections (5 October 2026 edition)](../doc/dataset_guide/lu-2026-data-public-lu-limadmin-cadastral-section.md) | Luxembourg | Cadastral sections | 2026-10-05 |
| [Brazilian IBGE district boundaries (2022 census)](../doc/dataset_guide/br-2022-ibge-gov-br-distritos-adm.md) | Brazil | Districts | 2022 |
| [Chilean census districts (APC 2023)](../doc/dataset_guide/cl-2023-ine-gob-cl-apc-stat-distrito-censal.md) | Chile | Census districts | 2023 |
| [Slovenian RPE settlement boundaries (27 September 2026 distribution)](../doc/dataset_guide/si-2026-ipi-eprostor-gov-si-rpe-adm.md) | Slovenia | Settlements | 2026-09-27 |
| [Liberian LISGIS administrative areas (2022)](../doc/dataset_guide/lr-2022-lisgis-gov-lr-geography-adm.md) | Liberia | Clans | 2022 |
| [Icelandic municipalities (INSPIRE 2022)](../doc/dataset_guide/is-2022-natt-is-is-au-lmi-adm1.md) | Iceland | Municipalities | 2022 |
| [Montenegrin municipalities (source date unknown)](../doc/dataset_guide/me-undated-opendata-gov-me-opstine-adm1.md) | Montenegro | Municipalities | Undated |
| [Slovak ZBGIS municipality-level areas (2026)](../doc/dataset_guide/sk-2026-skgeodesy-sk-zbgis-adm.md) | Slovakia | Municipality-level areas | 2026 / 2024 exceptions |
| [Serbian Geoanalitičari settlement boundaries (reference year unknown)](../doc/dataset_guide/rs-undated-data-gov-rs-hypso-struct-settl-adm.md) | Serbia | Settlements | Undated |

Reference years identify the distributed packages. Consult each dataset page and its ZIP's `data-spec.md` for exact source dates and the dates of combined sources.
