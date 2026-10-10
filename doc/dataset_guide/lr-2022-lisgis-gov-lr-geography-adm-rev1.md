# Liberian LISGIS administrative areas (2022)

English | [日本語](lr-2022-lisgis-gov-lr-geography-adm-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

Non-simplified County, District and Clan boundaries from LISGIS's 2022 population and housing census geography catalogue.

## Area counts

There are **902 areas by dictionary code**. 902 Clans under 160 Districts and 15 Counties. Parent names are dictionary levels, not additional pixel values. See the ZIP's `data-spec.md` for exact coverage and dates.

## Download

[Download lr-2022-lisgis-gov-lr-geography-adm-rev1.zip (695.2 KiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/lr-2022-lisgis-gov-lr-geography-adm-rev1.zip)

This link will work after v0.2.4 is published. The ZIP is already prepared in the local `release/` directory.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 13.6 KiB |
| 1000 (default) | approx. 111 m | 90.1 KiB |
| 10000 | approx. 11 m | 588.9 KiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 13.8 KiB |
| UTF-16LE | 13.8 KiB |

The included `names.csv` maps dictionary codes to source identifiers and names. Use the map and dictionary from the same ZIP.

### GisWordBook structure

Each record has 3 fixed StringSet slots.

| Position | Meaning |
| ---: | --- |
| 1 | County name |
| 2 | District name |
| 3 | Clan name |

Actual example (dictionary code `1`):

```json
["Bomi","Klay","Gorblah"]
```

Nonzero map values are dictionary codes. Code `0` is background and does not identify a dictionary record. Empty slots, where present, are retained rather than shifted.

## Rendering example

<a href="../../docs/image/lr-2022-lisgis-gov-lr-geography-adm-unit-inv-1000.png"><img src="../../docs/image/lr-2022-lisgis-gov-lr-geography-adm-unit-inv-1000.png" alt="Clans near Monrovia" width="640"></a>

Rendered near Monrovia at `unitInv=1000`. Blue denotes background; other colours distinguish area codes without additional meaning.

## License and terms of use

Original data: [official source 1](https://lisgis.gov.lr/data), [official source 2](https://lisgis.gov.lr/api/datasets), [official source 3](https://lisgis.gov.lr/data/api).

Original licence or terms: **CC BY 4.0 / LISGIS Open Data License** ([official licence/terms 1](https://creativecommons.org/licenses/by/4.0/), [official licence/terms 2](https://lisgis.gov.lr/open-data-license)). The ZIP's `NOTICE.md` records the source, applicable terms, attribution and processing for this release.

### Commercial use and permission applications (informational)

The cited CC BY 4.0 terms permit commercial reuse without a separate licence application when their conditions are met. Check the source's current terms and the ZIP's NOTICE.md for your use. This is informational, not a formal grant of permission or a legal determination.

### Attribution, modification and approval notices

Preserve the source and modification notices specified in the ZIP's `NOTICE.md`. This processed dataset is not presented as an official, approved or endorsed product of the source provider.

## Usage notes

Select one map resolution and one GisWordBook from this ZIP. File sizes are actual uncompressed member sizes; pixel distances are approximate. The source documents in the ZIP define coverage, code mapping and limitations.
