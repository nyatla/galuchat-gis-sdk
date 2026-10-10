# Icelandic municipalities (INSPIRE 2022)

English | [日本語](is-2022-natt-is-is-au-lmi-adm1-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

Municipality boundaries from the INSPIRE edition identified as 4 October 2022. Per-feature lifecycle dates are distinct from the edition date.

## Area counts

There are **64 areas by dictionary code**. 64 municipalities at one dictionary level. See the ZIP's `data-spec.md` for exact coverage and dates.

## Download

[Download is-2022-natt-is-is-au-lmi-adm1-rev1.zip (667.7 KiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.3/is-2022-natt-is-is-au-lmi-adm1-rev1.zip)

This link will work after v0.2.3 is published. The ZIP is already prepared in the local `release/` directory.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 6.9 KiB |
| 1000 (default) | approx. 111 m | 67.4 KiB |
| 10000 | approx. 11 m | 624.6 KiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 1.9 KiB |
| UTF-16LE | 1.9 KiB |

The included `names.csv` maps dictionary codes to source identifiers and names. Use the map and dictionary from the same ZIP.

### GisWordBook structure

Each record has 1 fixed StringSet slot.

| Position | Meaning |
| ---: | --- |
| 1 | Municipality name (source text) |

Actual example (dictionary code `1`):

```json
["Reykjavíkurborg"]
```

Nonzero map values are dictionary codes. Code `0` is background and does not identify a dictionary record. Empty slots, where present, are retained rather than shifted.

## Rendering example

<a href="../../docs/image/is-2022-natt-is-is-au-lmi-adm1-unit-inv-1000.png"><img src="../../docs/image/is-2022-natt-is-is-au-lmi-adm1-unit-inv-1000.png" alt="Municipalities near Reykjavík" width="640"></a>

Rendered near Reykjavík at `unitInv=1000`. Blue denotes background; other colours distinguish area codes without additional meaning.

## License and terms of use

Original data: [official source 1](https://www.natt.is/en/resources/open-data/data-download), [official source 2](https://gatt.natt.is/geonetwork/srv/api/records/%7B7CF6A33E-2588-42A8-A483-0B6F729B528A%7D/formatters/xml).

Original licence or terms: **CC BY 4.0 and Náttúrufræðistofnun terms** ([official licence/terms 1](https://creativecommons.org/licenses/by/4.0/), [official licence/terms 2](https://www.natt.is/en/resources/open-data), [official licence/terms 3](https://www-gamli.lmi.is/landupplysingar/leyfi-fyrir-gjaldfrjals-gogn/)). The ZIP's `NOTICE.md` records the source, applicable terms, attribution and processing for this release.

### Commercial use and permission applications (informational)

The cited CC BY 4.0 terms permit commercial reuse without a separate licence application when their conditions are met. Check the source's current terms and the ZIP's NOTICE.md for your use. This is informational, not a formal grant of permission or a legal determination.

### Attribution, modification and approval notices

Preserve the source and modification notices specified in the ZIP's `NOTICE.md`. This processed dataset is not presented as an official, approved or endorsed product of the source provider.

## Usage notes

Select one map resolution and one GisWordBook from this ZIP. File sizes are actual uncompressed member sizes; pixel distances are approximate. The source documents in the ZIP define coverage, code mapping and limitations.
