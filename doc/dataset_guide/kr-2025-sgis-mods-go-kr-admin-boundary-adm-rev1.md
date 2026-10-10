# South Korean SGIS administrative-dong boundaries, 2025 Q2

English | [日本語](kr-2025-sgis-mods-go-kr-admin-boundary-adm-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

Administrative-dong boundaries from the National Data Agency's SGIS administrative-area dataset, with a dictionary of si/do, si/gun/gu and administrative-dong names. `names.csv` maps dictionary codes to source administrative codes. Population and other statistics from the source download are not included. The boundary reference date is 2025-06-30.

## Area counts

There are **3,559 areas by dictionary code**, matching 3,559 adopted source administrative dongs. Distinct areas do not share a full name path in this edition. Parent si/do and si/gun/gu names are dictionary levels, not separate pixel values.

## Download

[Download kr-2025-sgis-mods-go-kr-admin-boundary-adm-rev1.zip (2.47 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/kr-2025-sgis-mods-go-kr-admin-boundary-adm-rev1.zip)

This link will work after v0.2.4 is published. The ZIP is already prepared in the local `release/` directory.

## Map resolutions and sizes

| unitInv | Approx. pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 34.3 KiB |
| 1000 (default) | approx. 111 m | 282.6 KiB |
| 10000 | approx. 11 m | 2.18 MiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 24.7 KiB |
| UTF-16LE | 24.4 KiB |

The included `names.csv` maps dictionary codes to source `SIDO_CD`, `SIGUNGU_CD` and `ADM_CD` values.

### GisWordBook structure

Each record has three fixed StringSet slots.

| Position | Meaning | Empty values |
| ---: | --- | --- |
| Area 1 | Si/do name | Not allowed |
| Area 2 | Si/gun/gu name | Not allowed |
| Area 3 | Administrative-dong name | Not allowed |

Actual example (dictionary code `1`):

```json
["서울특별시","종로구","사직동"]
```

Areas with the same leaf name but different full three-slot paths have different codes. Nonzero map values are dictionary codes. Code `0` is background, not a water-only value.

## Rendering example

<a href="../../docs/image/kr-sgis-admin-2025-unit-inv-1000.png"><img src="../../docs/image/kr-sgis-admin-2025-unit-inv-1000.png" alt="Administrative dongs near Seoul" width="640"></a>

Rendered near Seoul at `unitInv=1000`. Blue denotes background; other colors distinguish area codes without additional meaning.

## License and terms of use

Source: [Korean public-data portal, “국가데이터처_SGIS 행정구역 통계 및 경계_20250630”](https://www.data.go.kr/data/15129688/fileData.do).

The source page labels the scope of permitted use “이용허락범위 제한 없음” (no stated limit on the scope of permission). It does not identify a particular Creative Commons license or a public-domain dedication. Retain the ZIP's `NOTICE.md` to identify the source and processing.

### Commercial use and permission applications (informational)

The source page does not state an individual scope restriction or application requirement. This is not a formal license grant or a guarantee that every use is lawful. Check the current source-page terms and the ZIP's `NOTICE.md` for your intended use, and ask the provider if anything is unclear.

### Attribution, modification and approval notices

The NOTICE identifies the source and its download page, explains reprojection, parent-area matching and format conversion, and states that the processed package is not endorsed by the National Data Agency.

## Usage notes

Always use a map and dictionary from the same ZIP. Typically choose one map and the UTF-8 dictionary. Sizes are actual file sizes and pixel distances are approximate north-south distances. Administrative dongs are not legal dongs. See the ZIP's `data-spec.md` for coverage and limitations and `NOTICE.md` for rights and terms.
