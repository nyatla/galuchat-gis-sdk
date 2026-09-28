# Australian suburbs and localities, 2021

English | [日本語](au-2021-abs-gov-au-sal-stat-sal.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

ABS ASGS Edition 3 Suburbs and Localities. Provides statistical representations of suburb and locality areas, rather than their legal boundaries.

## Area counts

There are **15,334 areas by dictionary code** (GisWordBook leaf records). This is not a count of parent areas, polygons, or areas represented by pixels at each resolution.

There are 15,334 adopted SALs. Of the 15,353 source records, 19 special-purpose codes without spatial geometry are excluded.

## Download

[Download au-2021-abs-gov-au-sal-stat-sal.zip (15.60 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/au-2021-abs-gov-au-sal-stat-sal.zip)

## Map resolutions and sizes

| unitInv | Approx. pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 315.9 KiB |
| 1000 (default) | approx. 111 m | 2.02 MiB |
| 10000 | approx. 11 m | 13.47 MiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 179.8 KiB |
| UTF-16LE | 179.8 KiB |

See the included `names.csv` for source area identifiers.

### GisWordBook structure

Each record is a fixed-length StringSet with 2 slots in the order below. Empty values are retained as `""`; later slots are not shifted forward.

| Position | Slot | Meaning | Empty values |
| ---: | --- | --- | --- |
| 1 | Area 1 | English state / territory or Other Territories name (`STE_NAME21`) | Required |
| 2 | Area 2 | English suburb / locality name (`SAL_NAME21`) | Required |

There is no shared Australia slot and no empty slots. Adopted areas are distinguished by the two-slot name path.

Example from the actual data (dictionary code `3866`):

```json
["New South Wales","Sydney"]
```

Nonzero map values are dictionary codes. This example corresponds to zero-based leaf-record index `3865`. Code `0` denotes unset areas, not a dictionary record.

## Rendering example

<a href="../../docs/image/au-abs-asgs-sal-2021-unit-inv-1000.png"><img src="../../docs/image/au-abs-asgs-sal-2021-unit-inv-1000.png" alt="Australian suburbs and localities, 2021" width="640"></a>

The image is centered around Sydney and rendered at `unitInv=1000`. Blue denotes unset areas; other colors distinguish area codes and have no semantic meaning.

## License and terms of use

Source: Australian Bureau of Statistics (ABS), [ASGS Edition 3 digital boundary files](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files)

Original-data license / terms: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); [Copyright guidance](https://www.abs.gov.au/website-privacy-copyright-and-disclaimer)

This package adapts the source for Galuchat. For the processed data's terms of use, refer to the official terms above and the ZIP's `NOTICE.md`.

### Commercial use and permission applications (informational)

- Commercial use: CC BY 4.0 permits commercial use subject to its terms. [Official guidance](https://creativecommons.org/licenses/by/4.0/)
- Permission applications: No individual application to the copyright holder is needed for uses covered by CC BY 4.0. [Official guidance](https://creativecommons.org/licenses/by/4.0/)

This explanation is informational, not a formal grant of permission or a legal determination. Check the official terms and NOTICE yourself for the conditions and application requirements applicable to your intended use; contact the provider if anything is unclear.

### Attribution, modification and approval notices

Attribution and modification notices recorded in the NOTICE (original wording):

> Source: Australian Bureau of Statistics, Australian Statistical Geography Standard (ASGS) Edition 3, Suburbs and Localities 2021. Licensed under CC BY 4.0.
>
> Derived and processed by the Galuchat project. This product is not endorsed by the Australian Bureau of Statistics.

## Usage notes

Always use a map and dictionary from the same ZIP. Typically choose one WGSMapSet at a suitable resolution and the UTF-8 dictionary. Pixel value 0 denotes an unset area. Sizes are actual file sizes, not runtime memory usage. Pixel distances are approximate north-south distances.

See the ZIP's `data-spec.md` for coverage, names, attributes and limitations, and `NOTICE.md` for sources, processing, attribution and terms of use.
