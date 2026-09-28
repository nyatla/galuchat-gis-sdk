# UK local authority districts, December 2025

English | [日本語](gb-2025-geoportal-statistics-gov-uk-lad-adm-bfc.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

ONS Local Authority Districts (December 2025) Boundaries UK BFC. Covers England, Scotland, Wales and Northern Ireland.

## Area counts

There are **361 areas by dictionary code** (GisWordBook leaf records). This is not a count of parent areas, polygons, or areas represented by pixels at each resolution.

There are 361 LADs: England 296, Scotland 32, Wales 22 and Northern Ireland 11.

## Download

[Download gb-2025-geoportal-statistics-gov-uk-lad-adm-bfc.zip (2.36 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/gb-2025-geoportal-statistics-gov-uk-lad-adm-bfc.zip)

## Map resolutions and sizes

| unitInv | Approx. pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 19.8 KiB |
| 1000 (default) | approx. 111 m | 210.7 KiB |
| 10000 | approx. 11 m | 2.23 MiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 6.2 KiB |
| UTF-16LE | 6.3 KiB |

See the included `names.csv` for source area identifiers.

### GisWordBook structure

Each record is a fixed-length StringSet with 3 slots in the order below. Empty values are retained as `""`; later slots are not shifted forward.

| Position | Slot | Meaning | Empty values |
| ---: | --- | --- | --- |
| 1 | Area 1 | Constituent country: England, Scotland, Wales or Northern Ireland | Required |
| 2 | Area 2 | Parent administrative county | Empty if not applicable |
| 3 | Area 3 | English local-authority district name (`LAD25NM`) | Required |

There is no shared United Kingdom slot. Welsh names are stored in `names.csv` as `LAD25NMW`, not in the StringSet. Use the full path and GSS codes in `names.csv` to distinguish names.

Example from the actual data (dictionary code `296`):

```json
["England","","Westminster"]
```

Nonzero map values are dictionary codes. This example corresponds to zero-based leaf-record index `295`. Code `0` denotes unset areas, not a dictionary record.

## Rendering example

<a href="../../docs/image/uk-admin-ons-lad-2025-unit-inv-1000.png"><img src="../../docs/image/uk-admin-ons-lad-2025-unit-inv-1000.png" alt="UK local authority districts, December 2025" width="640"></a>

The image is centered around London and rendered at `unitInv=1000`. Blue denotes unset areas; other colors distinguish area codes and have no semantic meaning.

## License and terms of use

Source: Office for National Statistics (ONS), [LAD boundaries](https://www.data.gov.uk/dataset/aa5a9ccf-fbea-43cb-81cc-fdc04d89f128/local-authority-districts-december-2025-boundaries-uk-bfc) and [LAD-to-county lookup](https://www.data.gov.uk/dataset/a76a9de2-d0f4-4fd7-bcc9-e63bbf28bbb5/local-authority-district-to-county-and-unitary-authority-april-2025-lookup-in-ew-v2)

Original-data license / terms: [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/); [Licensing guidance](https://www.ons.gov.uk/methodology/geography/licences)

This package adapts the source for Galuchat. For the processed data's terms of use, refer to the official terms above and the ZIP's `NOTICE.md`.

### Commercial use and permission applications (informational)

- Commercial use: ONS permits commercial use subject to the Open Government Licence. [Official guidance](https://www.ons.gov.uk/methodology/geography/licences)
- Permission applications: ONS states that reuse within the terms does not require a specific license application. [Official guidance](https://www.ons.gov.uk/methodology/geography/licences)

This explanation is informational, not a formal grant of permission or a legal determination. Check the official terms and NOTICE yourself for the conditions and application requirements applicable to your intended use; contact the provider if anything is unclear.

### Attribution, modification and approval notices

Attribution and modification notices recorded in the NOTICE (original wording):

> Source: Office for National Statistics licensed under the Open Government Licence v.3.0
>
> Contains OS data © Crown copyright and database right 2026

## Usage notes

Always use a map and dictionary from the same ZIP. Typically choose one WGSMapSet at a suitable resolution and the UTF-8 dictionary. Pixel value 0 denotes an unset area. Sizes are actual file sizes, not runtime memory usage. Pixel distances are approximate north-south distances.

See the ZIP's `data-spec.md` for coverage, names, attributes and limitations, and `NOTICE.md` for sources, processing, attribution and terms of use.
