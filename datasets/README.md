# Galuchat GIS SDK datasets

English | [日本語](README.ja.md)

Galuchat GIS SDK datasets are available as ZIP archives from [GitHub Release v0.1.2](https://github.com/nyatla/galuchat-gis-sdk/releases/tag/v0.1.2). Download the dataset you need unless you are using the 2026 administrative-area data already bundled with the SDK.

Each ZIP contains WGSMapSet files, GisWordBooks, and a `NOTICE.md` describing sources and terms of use. Always use a WGSMapSet and GisWordBook from the same ZIP. For most applications, select one WGSMapSet suitable for the required resolution and use the UTF-8 GisWordBook.

The displayed ZIP sizes are the sizes of files published with the GitHub Release. Component sizes are approximate and do not represent runtime memory use.

## Japanese administrative areas, 2024 edition

This dataset is based on the 2024-01-01 edition of Japan's National Land Numerical Information Administrative Area Data N03. It identifies prefectures, municipalities, counties, and designated-city wards and is intended for applications that require historical 2024 boundaries.

[Download jp-admin-n03-2024.20260907.zip (approx. 6.05 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.1.2/jp-admin-n03-2024.20260907.zip)

| unitInv | Approx. north-south distance per pixel | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | approx. 52 KiB |
| 250 | approx. 445 m | approx. 123 KiB |
| 1000 (default) | approx. 111 m | approx. 479 KiB |
| 2500 | approx. 45 m | approx. 1.17 MiB |
| 10000 | approx. 11 m | approx. 4.48 MiB |

The ZIP includes UTF-8, Shift_JIS, and UTF-16 GisWordBooks of approximately 31 KiB each.

<a href="../docs/image/jp-admin-n03-2024-unit-inv-1000.png"><img src="../docs/image/jp-admin-n03-2024-unit-inv-1000.png" alt="2024 Japanese administrative-area data near Narashino" width="640"></a>

The image renders the area around Narashino at `unitInv=1000`. See `NOTICE.md` in the ZIP for sources, processing, and terms of use.

## Japanese administrative areas, 2025 edition

This dataset is based on the 2025-01-01 edition of Japan's National Land Numerical Information Administrative Area Data N03. It identifies prefectures, municipalities, counties, and designated-city wards as of 2025.

[Download jp-admin-n03-2025.20260907.zip (approx. 8.47 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.1.2/jp-admin-n03-2025.20260907.zip)

| unitInv | Approx. north-south distance per pixel | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | approx. 52 KiB |
| 250 | approx. 445 m | approx. 123 KiB |
| 500 | approx. 222 m | approx. 241 KiB |
| 1000 (default) | approx. 111 m | approx. 479 KiB |
| 2500 | approx. 45 m | approx. 1.17 MiB |
| 5000 | approx. 22 m | approx. 2.30 MiB |
| 10000 | approx. 11 m | approx. 4.48 MiB |

The ZIP includes UTF-8, Shift_JIS, and UTF-16 GisWordBooks of approximately 31 KiB each.

<a href="../docs/image/jp-admin-n03-2025-unit-inv-1000.png"><img src="../docs/image/jp-admin-n03-2025-unit-inv-1000.png" alt="2025 Japanese administrative-area data near Narashino" width="640"></a>

The image renders the area around Narashino at `unitInv=1000`. See `NOTICE.md` in the ZIP for sources, processing, and terms of use.

## Japanese administrative areas, 2026 edition

This dataset is based on the 2026-01-01 edition of Japan's National Land Numerical Information Administrative Area Data N03. It is the recommended edition for current administrative-area lookup and is used by the SDK's Get Started examples.

[Download jp-admin-n03-2026.20260907.zip (approx. 8.47 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.1.2/jp-admin-n03-2026.20260907.zip)

| unitInv | Approx. north-south distance per pixel | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | approx. 52 KiB |
| 250 | approx. 445 m | approx. 123 KiB |
| 500 | approx. 222 m | approx. 240 KiB |
| 1000 (default) | approx. 111 m | approx. 479 KiB |
| 2500 | approx. 45 m | approx. 1.17 MiB |
| 5000 | approx. 22 m | approx. 2.30 MiB |
| 10000 | approx. 11 m | approx. 4.47 MiB |

The ZIP includes UTF-8, Shift_JIS, and UTF-16 GisWordBooks of approximately 31 KiB each.

<a href="../docs/image/jp-admin-n03-2026-unit-inv-1000.png"><img src="../docs/image/jp-admin-n03-2026-unit-inv-1000.png" alt="2026 Japanese administrative-area data near Narashino" width="640"></a>

The image renders the area around Narashino at `unitInv=1000`. See `NOTICE.md` in the ZIP for sources, processing, and terms of use.

## e-Stat town-block and small-area boundaries, 2020 edition

This dataset is based on the Statistics Bureau of Japan's 2020 Population Census town-block and small-area boundary data. It supports reverse geocoding at town-block, small-area, and subordinate-area levels. These statistical boundaries do not necessarily match ordinary administrative divisions or official addressing areas.

[Download jp-estat-r2ka-2020.20260907.zip (approx. 37.09 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.1.2/jp-estat-r2ka-2020.20260907.zip)

| unitInv | Approx. north-south distance per pixel | WGSMapSet size |
| ---: | ---: | ---: |
| 5000 | approx. 22 m | approx. 12.94 MiB |
| 10000 (default) | approx. 11 m | approx. 22.70 MiB |

The ZIP includes UTF-8, Shift_JIS, and UTF-16 GisWordBooks of approximately 1.63 MiB each.

<a href="../docs/image/jp-estat-r2ka-2020-unit-inv-10000.png"><img src="../docs/image/jp-estat-r2ka-2020-unit-inv-10000.png" alt="e-Stat town-block data near Narashino" width="640"></a>

The image renders the area around Narashino at `unitInv=10000`. See `NOTICE.md` in the ZIP for sources, processing, and terms of use.

## Integrated GIS and e-Stat data

This dataset integrates N03 administrative areas with e-Stat town-block and small-area boundaries. A single GisWordBook provides place-name hierarchies from prefectures and municipalities through town blocks and small areas. It is intended for applications requiring unified reverse geocoding across these levels.

[Download jp-gis-estat-integrated.20260907.zip (approx. 26.06 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.1.2/jp-gis-estat-integrated.20260907.zip)

| unitInv | Approx. north-south distance per pixel | WGSMapSet size |
| ---: | ---: | ---: |
| 10000 (default) | approx. 11 m | approx. 24.07 MiB |

The ZIP includes UTF-8, Shift_JIS, and UTF-16 GisWordBooks of approximately 1.66 MiB each.

<a href="../docs/image/jp-gis-estat-integrated-unit-inv-10000.png"><img src="../docs/image/jp-gis-estat-integrated-unit-inv-10000.png" alt="Integrated administrative and small-area data near Narashino" width="640"></a>

The image renders the area around Narashino at `unitInv=10000`. See `NOTICE.md` in the ZIP for sources, processing, and terms of use.

## Taiwan village boundaries, 2026 edition

This dataset is based on the 2026-08-17 village-boundary data published by Taiwan's National Land Surveying and Mapping Center (NLSC). It provides Traditional Chinese place names as a three-level `[county/city, township/district, village]` hierarchy. Areas without a village name in the source are recorded as `未編定村里`.

[Download tw-admin-nlsc-village-2026.20260907.zip (approx. 1.51 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.1.2/tw-admin-nlsc-village-2026.20260907.zip)

| unitInv | Approx. north-south distance per pixel | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | approx. 26 KiB |
| 1000 (default) | approx. 111 m | approx. 202 KiB |
| 10000 | approx. 11 m | approx. 1.27 MiB |

The ZIP includes a UTF-8 GisWordBook of approximately 57 KiB and a UTF-16 GisWordBook of approximately 56 KiB.

<a href="../docs/image/tw-admin-nlsc-village-2026-unit-inv-10000.png"><img src="../docs/image/tw-admin-nlsc-village-2026-unit-inv-10000.png" alt="Taiwan village-boundary data near Taipei" width="640"></a>

The image renders the area around Taipei at `unitInv=10000`. See `NOTICE.md` in the ZIP for sources, processing, and terms of use.

## UK local authority districts, December 2025 edition

This dataset is based on the Office for National Statistics (ONS) "Local Authority Districts (December 2025) Boundaries UK BFC" data. It covers England, Scotland, Wales, and Northern Ireland and provides English place names as a three-level `[constituent country, county or empty string, local authority district]` hierarchy.

[Download uk-admin-ons-lad-2025.20260907.zip (approx. 2.35 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.1.2/uk-admin-ons-lad-2025.20260907.zip)

| unitInv | Approx. north-south distance per pixel | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | approx. 20 KiB |
| 1000 (default) | approx. 111 m | approx. 211 KiB |
| 10000 | approx. 11 m | approx. 2.23 MiB |

The ZIP includes UTF-8 and UTF-16 GisWordBooks of approximately 6.2 KiB each.

<a href="../docs/image/uk-admin-ons-lad-2025-unit-inv-1000.png"><img src="../docs/image/uk-admin-ons-lad-2025-unit-inv-1000.png" alt="UK local-authority-district data near London" width="640"></a>

The image renders the area around London at `unitInv=1000`. See `NOTICE.md` in the ZIP for sources, processing, and terms of use.

## Global administrative boundaries

This worldwide administrative-boundary dataset is based on geoBoundaries CGAZ. For each region, it contains the most detailed available boundary among ADM2, ADM1, ADM0, and disputed areas. It supports country and administrative-area lookup worldwide.

[Download world-geoboundaries-cgaz.20260907.zip (approx. 22.92 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.1.2/world-geoboundaries-cgaz.20260907.zip)

| unitInv | Approx. north-south distance per pixel | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | approx. 2.81 MiB |
| 1000 (default) | approx. 111 m | approx. 20.45 MiB |

The ZIP includes UTF-8 and UTF-16 GisWordBooks of approximately 561 KiB each.

<a href="../docs/image/world-geoboundaries-cgaz-unit-inv-1000.png"><img src="../docs/image/world-geoboundaries-cgaz-unit-inv-1000.png" alt="Global administrative-boundary rendering" width="640"></a>

The image is rendered at `unitInv=1000`. See `NOTICE.md` in the ZIP for sources, processing, and terms of use.

## Choosing a resolution

`unitInv` is the number of pixels per degree. Larger values represent boundaries and coastlines in greater detail but produce larger files.

| unitInv | Approx. north-south distance per pixel |
| ---: | ---: |
| 100 | approx. 1.1 km |
| 250 | approx. 445 m |
| 500 | approx. 222 m |
| 1000 | approx. 111 m |
| 2500 | approx. 45 m |
| 5000 | approx. 22 m |
| 10000 | approx. 11 m |

Distances are approximate north-south values; physical east-west distance varies with latitude. Increasing resolution does not change the region-code granularity from municipalities to town blocks, for example. First select a dataset containing the required place-name hierarchy, then choose a resolution based on the desired boundary precision and file size.
