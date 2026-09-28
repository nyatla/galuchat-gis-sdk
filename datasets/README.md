# Galuchat GIS SDK datasets

English | [日本語](README.ja.md)

The 16 datasets for SDK 0.2.1 are intended for distribution with [GitHub Release v0.2.1](https://github.com/nyatla/galuchat-gis-sdk/releases/tag/v0.2.1). The Japanese administrative-area dataset for 2026 is also bundled with the SDK for its Get Started examples.

Each ZIP contains `data-spec.md`, `NOTICE.md`, WGSMapSet files and GisWordBooks. Some also include `names.csv` mapping source identifiers to dictionary codes, or metadata XML. Read `data-spec.md` for the full data specification and `NOTICE.md` for sources, processing and terms of use.

Always pair a map and dictionary from the same ZIP. Typically choose one map at a suitable resolution and the UTF-8 dictionary. Pixel value 0 denotes an unset area. Each dataset page includes area counts, GisWordBook slot structures and actual data examples, download links, resolutions, file sizes and rendering examples. Counts explicitly identify the dictionary-code unit and distinguish source-area counts where source areas share dictionary codes.

Each page's "License and terms of use" section links to the original-data license and official terms, provides informational notes on commercial use and permission applications, and lists attribution notices from the NOTICE. These notes are not a formal grant of permission or a legal determination; check the official terms and the ZIP's NOTICE for your intended use.

## Dataset index

| Dataset | Region | Area type | Reference year / edition |
| --- | --- | --- | --- |
| [Japanese administrative areas, 2024](../doc/dataset_guide/jp-2024-mlit-go-jp-n03-adm.md) | Japan | Administrative areas | 2024 |
| [Japanese administrative areas, 2025](../doc/dataset_guide/jp-2025-mlit-go-jp-n03-adm.md) | Japan | Administrative areas | 2025 |
| [Japanese administrative areas, 2026](../doc/dataset_guide/jp-2026-mlit-go-jp-n03-adm.md) (bundled with SDK) | Japan | Administrative areas | 2026 |
| [Japanese e-Stat small areas, 2020](../doc/dataset_guide/jp-2020-e-stat-go-jp-a002005212020-stat-small-area.md) | Japan | Census small areas | 2020 |
| [Japanese e-Stat areas with N03 coastline](../doc/dataset_guide/jp-2026-nyatla-jp-estat-coastline.md) | Japan | Small areas with N03 coastline | 2026 / 2020 |
| [Taiwan village boundaries, 2026](../doc/dataset_guide/tw-2026-maps-nlsc-gov-tw-village-adm.md) | Taiwan | Villages | 2026 |
| [UK local authority districts, December 2025](../doc/dataset_guide/gb-2025-geoportal-statistics-gov-uk-lad-adm-bfc.md) | United Kingdom | Local authority districts | 2025 |
| [U.S. counties and county equivalents, 2025](../doc/dataset_guide/us-2025-census-gov-tl-county-adm2.md) | United States | Counties and equivalents | 2025 |
| [U.S. states and state equivalents, 2025](../doc/dataset_guide/us-2025-census-gov-tl-state-adm1.md) | United States | States and equivalents | 2025 |
| [Canadian census subdivisions, 2021](../doc/dataset_guide/ca-2021-statcan-gc-ca-csd-cbf-stat-csd.md) | Canada | Census subdivisions | 2021 |
| [Worldwide administrative boundaries](../doc/dataset_guide/world-2024-geoboundaries-org-cgaz-adm.md) | Worldwide | Best-available administrative areas | 2024 |
| [Australian suburbs and localities, 2021](../doc/dataset_guide/au-2021-abs-gov-au-sal-stat-sal.md) | Australia | Suburbs and localities (statistical) | 2021 |
| [German administrative areas, VG250 2026](../doc/dataset_guide/de-2026-gdz-bkg-bund-de-vg250-adm.md) | Germany | Municipalities and unincorporated areas | 2026 |
| [French administrative areas, ADMIN EXPRESS COG 2026](../doc/dataset_guide/fr-2026-cartes-gouv-fr-admin-express-cog-adm.md) | France | Communes and municipal arrondissements | 2026 |
| [Dutch municipalities, 2026](../doc/dataset_guide/nl-2026-cbs-nl-wijkbuurtkaart-adm.md) | Netherlands | Municipalities | 2026 |
| [Dutch districts and neighbourhoods, 2026](../doc/dataset_guide/nl-2026-cbs-nl-wijkbuurtkaart-stat-buurt.md) | Netherlands | Districts and neighbourhoods | 2026 |

Reference years identify the distributed packages. Consult each dataset page and its ZIP's `data-spec.md` for exact source dates and the dates of combined sources.
