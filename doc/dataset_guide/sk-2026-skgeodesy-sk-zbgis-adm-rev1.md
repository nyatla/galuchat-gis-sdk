# Slovak ZBGIS municipality-level areas (2026)

English | [日本語](sk-2026-skgeodesy-sk-zbgis-adm-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

ZBGIS municipality-level boundaries: generally 30 June 2026, with eight districts using 31 December 2024 source boundaries.

## Area counts

There are **2,927 areas by dictionary code**. 2,927 municipality-level areas under 79 Okres and eight Kraj. Parent names are dictionary levels, not additional pixel values. See the ZIP's `data-spec.md` for exact coverage and dates.

## Download

[Download sk-2026-skgeodesy-sk-zbgis-adm-rev1.zip (1.61 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/sk-2026-skgeodesy-sk-zbgis-adm-rev1.zip)

This link will work after v0.2.4 is published. The ZIP is already prepared in the local `release/` directory.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 28.4 KiB |
| 1000 (default) | approx. 111 m | 199.8 KiB |
| 10000 | approx. 11 m | 1.34 MiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 42.6 KiB |
| UTF-16LE | 42.7 KiB |

The included `names.csv` maps dictionary codes to source identifiers and names. Use the map and dictionary from the same ZIP.

### GisWordBook structure

Each record has 3 fixed StringSet slots.

| Position | Meaning |
| ---: | --- |
| 1 | Kraj name |
| 2 | Okres name |
| 3 | Obec-level area name |

Actual example (dictionary code `1`):

```json
["Nitriansky","Nitra","Nitra"]
```

Nonzero map values are dictionary codes. Code `0` is background and does not identify a dictionary record. Empty slots, where present, are retained rather than shifted.

## Rendering example

<a href="../../docs/image/sk-2026-skgeodesy-sk-zbgis-adm-unit-inv-1000.png"><img src="../../docs/image/sk-2026-skgeodesy-sk-zbgis-adm-unit-inv-1000.png" alt="Municipality-level areas near Bratislava" width="640"></a>

Rendered near Bratislava at `unitInv=1000`. Blue denotes background; other colours distinguish area codes without additional meaning.

## License and terms of use

Original data: [official source](https://www.gku.sk/gku/produkty-sluzby/na-stiahnutie/zbgis.html).

Original licence or terms: **CC BY 4.0 and provider terms** ([official licence/terms 1](https://creativecommons.org/licenses/by/4.0/), [official licence/terms 2](https://www.gku.sk/gku/produkty-sluzby/na-stiahnutie/zbgis.html)). The ZIP's `NOTICE.md` records the source, applicable terms, attribution and processing for this release.

### Commercial use and permission applications (informational)

The cited CC BY 4.0 terms permit commercial reuse without a separate licence application when their conditions are met. Check the source's current terms and the ZIP's NOTICE.md for your use. This is informational, not a formal grant of permission or a legal determination.

### Attribution, modification and approval notices

Preserve the source and modification notices specified in the ZIP's `NOTICE.md`. This processed dataset is not presented as an official, approved or endorsed product of the source provider.

## Usage notes

Select one map resolution and one GisWordBook from this ZIP. File sizes are actual uncompressed member sizes; pixel distances are approximate. The source documents in the ZIP define coverage, code mapping and limitations.
