# Montenegrin municipalities (source date unknown)

English | [日本語](me-undated-opendata-gov-me-opstine-adm1-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

Municipal areas from the original optine source. The boundary reference year is unknown; later portal and DBF dates are not presented as boundary dates.

## Area counts

There are **22 areas by dictionary code**. 22 dictionary codes: 21 non-empty municipality names and one unnamed area. The source contains 26 geometries, which are not 26 distinct dictionary codes. See the ZIP's `data-spec.md` for exact coverage and dates.

## Download

[Download me-undated-opendata-gov-me-opstine-adm1-rev1.zip (96.5 KiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.3/me-undated-opendata-gov-me-opstine-adm1-rev1.zip)

This link will work after v0.2.3 is published. The ZIP is already prepared in the local `release/` directory.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 1.5 KiB |
| 1000 (default) | approx. 111 m | 10.0 KiB |
| 10000 | approx. 11 m | 82.5 KiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 0.6 KiB |
| UTF-16LE | 0.6 KiB |

The included `names.csv` maps dictionary codes to source identifiers and names. Use the map and dictionary from the same ZIP.

### GisWordBook structure

Each record has 1 fixed StringSet slot.

| Position | Meaning |
| ---: | --- |
| 1 | Original municipality name, or an empty string for the unnamed area |

Actual example (dictionary code `1`):

```json
["Andrijevica"]
```

Nonzero map values are dictionary codes. Code `0` is background and does not identify a dictionary record. Empty slots, where present, are retained rather than shifted.

## Rendering example

<a href="../../docs/image/me-undated-opendata-gov-me-opstine-adm1-unit-inv-1000.png"><img src="../../docs/image/me-undated-opendata-gov-me-opstine-adm1-unit-inv-1000.png" alt="Municipalities near Podgorica" width="640"></a>

Rendered near Podgorica at `unitInv=1000`. Blue denotes background; other colours distinguish area codes without additional meaning.

## License and terms of use

Original data: [official source 1](https://opendata.gov.me/dataset/zasticena-podrucja-prirode-crne-gore), [official source 2](https://data.gov.me/dataset/189a0ae7-5d0b-419a-a2a0-a1a1ccbda8b8/resource/b82f7fe0-492b-4f8b-873d-9ced4187b6ce/download/optine.zip), [official source 3](https://opendata.gov.me/api/3/action/package_show?id=zasticena-podrucja-prirode-crne-gore).

Original licence or terms: **CC0 1.0** ([official licence/terms](https://creativecommons.org/publicdomain/zero/1.0/)). The ZIP's `NOTICE.md` records the source, applicable terms, attribution and processing for this release.

### Commercial use and permission applications (informational)

The source identifies CC0 1.0, which does not state a commercial-use or individual-permission requirement for the covered rights. Check NOTICE.md and any rights outside CC0's scope. This is informational, not a formal grant of permission or a legal determination.

### Attribution, modification and approval notices

Preserve the source and modification notices specified in the ZIP's `NOTICE.md`. This processed dataset is not presented as an official, approved or endorsed product of the source provider.

## Usage notes

Select one map resolution and one GisWordBook from this ZIP. File sizes are actual uncompressed member sizes; pixel distances are approximate. The source documents in the ZIP define coverage, code mapping and limitations.
