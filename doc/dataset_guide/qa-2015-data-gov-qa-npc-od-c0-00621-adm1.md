# Qatar municipalities (2015 census source)

English | [日本語](qa-2015-data-gov-qa-npc-od-c0-00621-adm1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

Eight municipal boundaries from a dataset associated with Qatar's 2015 census. The census year does not establish the exact boundary reference date.

## Area counts

There are **8 areas by dictionary code**. Eight municipalities, represented by one dictionary level. The portal's later update date is not treated as the boundary date. See the ZIP's `data-spec.md` for exact coverage and dates.

## Download

[Download qa-2015-data-gov-qa-npc-od-c0-00621-adm1-rev1.zip (70.0 KiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/qa-2015-data-gov-qa-npc-od-c0-00621-adm1-rev1.zip)

This link will work after v0.2.4 is published. The ZIP is already prepared in the local `release/` directory.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 0.9 KiB |
| 1000 (default) | approx. 111 m | 6.6 KiB |
| 10000 | approx. 11 m | 57.1 KiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 0.4 KiB |
| UTF-16LE | 0.4 KiB |

The included `names.csv` maps dictionary codes to source identifiers and names. Use the map and dictionary from the same ZIP.

### GisWordBook structure

Each record has 1 fixed StringSet slot.

| Position | Meaning |
| ---: | --- |
| 1 | Municipality name |

Actual example (dictionary code `1`):

```json
["Al-Daayen"]
```

Nonzero map values are dictionary codes. Code `0` is background and does not identify a dictionary record. Empty slots, where present, are retained rather than shifted.

## Rendering example

<a href="../../docs/image/qa-2015-data-gov-qa-npc-od-c0-00621-adm1-unit-inv-1000.png"><img src="../../docs/image/qa-2015-data-gov-qa-npc-od-c0-00621-adm1-unit-inv-1000.png" alt="Municipalities near Doha" width="640"></a>

Rendered near Doha at `unitInv=1000`. Blue denotes background; other colours distinguish area codes without additional meaning.

## License and terms of use

Original data: [official source](https://www.data.gov.qa/explore/dataset/distribution-of-business-establishments-and-employees-by-municipalities-according-to-census-2015/).

Original licence or terms: **CC BY 4.0** ([official licence/terms](https://creativecommons.org/licenses/by/4.0/)). The ZIP's `NOTICE.md` records the source, applicable terms, attribution and processing for this release.

### Commercial use and permission applications (informational)

The cited CC BY 4.0 terms permit commercial reuse without a separate licence application when their conditions are met. Check the source's current terms and the ZIP's NOTICE.md for your use. This is informational, not a formal grant of permission or a legal determination.

### Attribution, modification and approval notices

Preserve the source and modification notices specified in the ZIP's `NOTICE.md`. This processed dataset is not presented as an official, approved or endorsed product of the source provider.

## Usage notes

Select one map resolution and one GisWordBook from this ZIP. File sizes are actual uncompressed member sizes; pixel distances are approximate. The source documents in the ZIP define coverage, code mapping and limitations.
