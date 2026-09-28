# Taiwan village boundaries, 2026

English | [日本語](tw-2026-maps-nlsc-gov-tw-village-adm.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

NLSC village boundaries revised on 2026-08-17. Traditional Chinese names identify county/city, township/district and village. Unassigned village areas are included.

## Area counts

There are **7,828 areas by dictionary code** (GisWordBook leaf records). This is not a count of parent areas, polygons, or areas represented by pixels at each resolution.

There are 7,987 adopted source areas: 7,781 named villages and 206 unassigned areas. The latter are grouped into 47 records, giving 7,828 dictionary records.

## Download

[Download tw-2026-maps-nlsc-gov-tw-village-adm.zip (1.65 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/tw-2026-maps-nlsc-gov-tw-village-adm.zip)

## Map resolutions and sizes

| unitInv | Approx. pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 25.7 KiB |
| 1000 (default) | approx. 111 m | 201.7 KiB |
| 10000 | approx. 11 m | 1.27 MiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 57.1 KiB |
| UTF-16LE | 56.0 KiB |

See the included `names.csv` for source area identifiers.

### GisWordBook structure

Each record is a fixed-length StringSet with 3 slots in the order below. Empty values are retained as `""`; later slots are not shifted forward.

| Position | Slot | Meaning | Empty values |
| ---: | --- | --- | --- |
| 1 | Area 1 | County / city (`COUNTYNAME`) | Required |
| 2 | Area 2 | Township / town / city / district (`TOWNNAME`) | Required |
| 3 | Area 3 | Village (`VILLNAME`), or `未編定村里` | Required |

There is no shared country/region-name slot. Source areas without a village name are grouped by `TOWNCODE` under `未編定村里`, not stored as empty names. Use `names.csv` for correspondence with `VILLCODE` and `GRVALUE`.

Example from the actual data (dictionary code `3648`):

```json
["臺北市","信義區","西村里"]
```

Nonzero map values are dictionary codes. This example corresponds to zero-based leaf-record index `3647`. Code `0` denotes unset areas, not a dictionary record.

## Rendering example

<a href="../../docs/image/tw-admin-nlsc-village-2026-unit-inv-10000.png"><img src="../../docs/image/tw-admin-nlsc-village-2026-unit-inv-10000.png" alt="Taiwan village boundaries, 2026" width="640"></a>

The image is centered around Taipei and rendered at `unitInv=10000`. Blue denotes unset areas; other colors distinguish area codes and have no semantic meaning.

## License and terms of use

Source: National Land Surveying and Mapping Center (NLSC), [village boundaries](https://data.gov.tw/dataset/7438)

Original-data license / terms: [Open Government Data License 1.0](https://data.gov.tw/license)

This package adapts the source for Galuchat. For the processed data's terms of use, refer to the official terms above and the ZIP's `NOTICE.md`.

### Commercial use and permission applications (informational)

- Commercial use: The Open Government Data License permits use for any purpose, including commercial use, subject to its terms. [Official guidance](https://data.gov.tw/license)
- Permission applications: The license expressly states that separate written or other permission from the providing organization is unnecessary within its scope. [Official guidance](https://data.gov.tw/license)

This explanation is informational, not a formal grant of permission or a legal determination. Check the official terms and NOTICE yourself for the conditions and application requirements applicable to your intended use; contact the provider if anything is unclear.

### Attribution, modification and approval notices

Attribution and modification notices recorded in the NOTICE (original wording):

> 內政部國土測繪中心 2026 村里界圖(TWD97經緯度)（2026-08-17版）
>
> 此開放資料依政府資料開放授權條款 (Open Government Data License) 進行公眾釋出，使用者於遵守本條款各項規定之前提下，得利用之。
>
> 政府資料開放授權條款：https://data.gov.tw/license

## Usage notes

Always use a map and dictionary from the same ZIP. Typically choose one WGSMapSet at a suitable resolution and the UTF-8 dictionary. Pixel value 0 denotes an unset area. Sizes are actual file sizes, not runtime memory usage. Pixel distances are approximate north-south distances.

See the ZIP's `data-spec.md` for coverage, names, attributes and limitations, and `NOTICE.md` for sources, processing, attribution and terms of use.
