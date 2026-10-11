# Singapore Master Plan 2019 subzones (No Sea)

English | [日本語](sg-2019-data-gov-sg-master-plan-subzone-no-sea.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

URA Master Plan 2019 planning subzones excluding sea. The planning-plan year and source data update date are distinct.

## Area counts

There are **332 areas by dictionary code**. 332 subzones under 55 Planning Areas and five Regions. Parent names are dictionary levels, not additional pixel values. See the ZIP's `data-spec.md` for exact coverage and dates.

## Download

[Download sg-2019-data-gov-sg-master-plan-subzone-no-sea-rev1.zip (78.3 KiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/sg-2019-data-gov-sg-master-plan-subzone-no-sea-rev1.zip)

This link will work after v0.2.4 is published. The ZIP is already prepared in the local `release/` directory.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 1.2 KiB |
| 1000 (default) | approx. 111 m | 8.0 KiB |
| 10000 | approx. 11 m | 50.1 KiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 5.0 KiB |
| UTF-16LE | 5.0 KiB |

The included `names.csv` maps dictionary codes to source identifiers and names. Use the map and dictionary from the same ZIP.

### GisWordBook structure

Each record has 3 fixed StringSet slots.

| Position | Meaning |
| ---: | --- |
| 1 | Region name |
| 2 | Planning Area name |
| 3 | Subzone name |

Actual example (dictionary code `1`):

```json
["NORTH-EAST REGION","ANG MO KIO","ANG MO KIO TOWN CENTRE"]
```

Nonzero map values are dictionary codes. Code `0` is background and does not identify a dictionary record. Empty slots, where present, are retained rather than shifted.

## Rendering example

<a href="../../docs/image/sg-2019-data-gov-sg-master-plan-subzone-no-sea-unit-inv-1000.png"><img src="../../docs/image/sg-2019-data-gov-sg-master-plan-subzone-no-sea-unit-inv-1000.png" alt="Planning subzones near Singapore" width="640"></a>

Rendered near Singapore at `unitInv=1000`. Blue denotes background; other colours distinguish area codes without additional meaning.

## License and terms of use

Original data: [official source](https://data.gov.sg/datasets/d_8594ae9ff96d0c708bc2af633048edfb/view).

Original licence or terms: **Singapore Open Data Licence 1.0** ([official licence/terms](https://data.gov.sg/open-data-licence)). The ZIP's `NOTICE.md` records the source, applicable terms, attribution and processing for this release.

### Commercial use and permission applications (informational)

The cited Singapore Open Data Licence permits commercial use. Its conditions include limits on sublicensing; check the current licence and NOTICE.md before redistributing through another product. No separate application is identified for ordinary licensed use. This is informational, not a formal grant of permission or a legal determination.

### Attribution, modification and approval notices

Preserve the source and modification notices specified in the ZIP's `NOTICE.md`. This processed dataset is not presented as an official, approved or endorsed product of the source provider.

## Usage notes

Select one map resolution and one GisWordBook from this ZIP. File sizes are actual uncompressed member sizes; pixel distances are approximate. The source documents in the ZIP define coverage, code mapping and limitations.
