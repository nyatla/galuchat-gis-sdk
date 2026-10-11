# Cyprus administrative units (August 2024)

English | [日本語](cy-2024-data-gov-cy-administrative-units-adm.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

Administrative boundaries from the Cyprus Department of Lands and Surveys. The source edition is August 2024 and reflects the 2024 municipal reorganisation where represented.

## Area counts

There are **744 areas by dictionary code**. 744 leaf areas: 585 local units without quarters and 159 quarters. These derive from 615 local units across six districts. Parent names are dictionary levels, not additional pixel values. See the ZIP's `data-spec.md` for exact coverage and dates.

## Download

[Download cy-2024-data-gov-cy-administrative-units-adm-rev1.zip (449.0 KiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/cy-2024-data-gov-cy-administrative-units-adm-rev1.zip)

This link will work after v0.2.4 is published. The ZIP is already prepared in the local `release/` directory.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 5.4 KiB |
| 1000 (default) | approx. 111 m | 43.9 KiB |
| 10000 | approx. 11 m | 370.3 KiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 11.7 KiB |
| UTF-16LE | 11.8 KiB |

The included `names.csv` maps dictionary codes to source identifiers and names. Use the map and dictionary from the same ZIP.

### GisWordBook structure

Each record has 4 fixed StringSet slots.

| Position | Meaning |
| ---: | --- |
| 1 | District name |
| 2 | Municipality or community name |
| 3 | Component locality name; empty where inapplicable |
| 4 | Quarter name; empty where inapplicable |

Actual example (dictionary code `1`):

```json
["ΛΕΥΚΩΣΙΑ","Δήμος Λευκωσίας","ΛΕΥΚΩΣΙΑ","ΑΓΙΟΣ ΑΝΔΡ"]
```

Nonzero map values are dictionary codes. Code `0` is background and does not identify a dictionary record. Empty slots, where present, are retained rather than shifted.

## Rendering example

<a href="../../docs/image/cy-2024-data-gov-cy-administrative-units-adm-unit-inv-1000.png"><img src="../../docs/image/cy-2024-data-gov-cy-administrative-units-adm-unit-inv-1000.png" alt="Local units and quarters near Nicosia" width="640"></a>

Rendered near Nicosia at `unitInv=1000`. Blue denotes background; other colours distinguish area codes without additional meaning.

## License and terms of use

Original data: [official source 1](https://www.data.gov.cy/en/dataset/187), [official source 2](https://www.data.gov.cy/sites/default/files/Administrative_Units_GR_Shapefiles_AUGUST2024_0.zip).

Original licence or terms: **CC BY 4.0** ([official licence/terms 1](https://creativecommons.org/licenses/by/4.0/), [official licence/terms 2](https://creativecommons.org/licenses/by/4.0/legalcode.en)). The ZIP's `NOTICE.md` records the source, applicable terms, attribution and processing for this release.

### Commercial use and permission applications (informational)

The cited CC BY 4.0 terms permit commercial reuse without a separate licence application when their conditions are met. Check the source's current terms and the ZIP's NOTICE.md for your use. This is informational, not a formal grant of permission or a legal determination.

### Attribution, modification and approval notices

Preserve the source and modification notices specified in the ZIP's `NOTICE.md`. This processed dataset is not presented as an official, approved or endorsed product of the source provider.

## Usage notes

Select one map resolution and one GisWordBook from this ZIP. File sizes are actual uncompressed member sizes; pixel distances are approximate. The source documents in the ZIP define coverage, code mapping and limitations.
