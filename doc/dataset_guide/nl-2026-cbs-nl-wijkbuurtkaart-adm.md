# Dutch municipalities, 2026

English | [日本語](nl-2026-cbs-nl-wijkbuurtkaart-adm.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

CBS Wijk- en Buurtkaart 2026 versie 0 municipalities. Provides province and municipality names for European Netherlands. Land and water faces retain distinct dictionary records with WATER attributes; Caribbean territories are excluded.

## Area counts

There are **423 areas by dictionary code** (GisWordBook leaf records). This is not a count of parent areas, polygons, or areas represented by pixels at each resolution.

There are 342 municipalities (distinct `GEM_CODE` values) and 423 adopted land/water surfaces. These correspond to 423 dictionary records.

## Download

[Download nl-2026-cbs-nl-wijkbuurtkaart-adm.zip (636.5 KiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/nl-2026-cbs-nl-wijkbuurtkaart-adm.zip)

## Map resolutions and sizes

| unitInv | Approx. pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 8.8 KiB |
| 1000 (default) | approx. 111 m | 68.7 KiB |
| 10000 | approx. 11 m | 566.8 KiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 6.7 KiB |
| UTF-16LE | 6.7 KiB |

See the included `names.csv` for source area identifiers.

### GisWordBook structure

Each record is a fixed-length StringSet with 3 slots in the order below. Empty values are retained as `""`; later slots are not shifted forward.

| Position | Slot | Meaning | Empty values |
| ---: | --- | --- | --- |
| 1 | Area 1 | Province (`PROV_NAME`) | Required |
| 2 | Area 2 | Municipality (`GEM_NAME`) | Required |
| 3 | Attribute 1 | `WATER`: `NEE` = land category; `JA` = water category | Required |

WATER is a surface attribute, not an administrative level. Land and water surfaces of the same municipality have separate dictionary codes. There is no Nederland slot or source-code slot; original spelling is preserved without synthetic suffixes.

Example from the actual data (dictionary code `128`):

```json
["Noord-Holland","Amsterdam","NEE"]
```

Nonzero map values are dictionary codes. This example corresponds to zero-based leaf-record index `127`. Code `0` denotes unset areas, not a dictionary record.

## Rendering example

<a href="../../docs/image/nl-admin-municipality-2026-unit-inv-1000.png"><img src="../../docs/image/nl-admin-municipality-2026-unit-inv-1000.png" alt="Dutch municipalities, 2026" width="640"></a>

The image is centered around Amsterdam and rendered at `unitInv=1000`. Blue denotes unset areas; other colors distinguish area codes and have no semantic meaning.

## License and terms of use

Source: CBS / Kadaster [Wijk- en Buurtkaart 2026](https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2026) and CBS [municipality-to-province table](https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/overig/gemeentelijke-indelingen-per-jaar/indeling-per-jaar/gemeentelijke-indeling-op-1-januari-2026)

Original-data license / terms: [Copyright policy (CC BY 4.0 unless otherwise stated)](https://www.cbs.nl/en-gb/about-us/website/copyright); [Source-attribution terms](https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2026)

This package adapts the source for Galuchat. For the processed data's terms of use, refer to the official terms above and the ZIP's `NOTICE.md`.

### Commercial use and permission applications (informational)

- Commercial use: Within CC BY 4.0's scope under CBS's general policy, commercial use is permitted subject to its terms. The geographic-data page also specifies CBS / Kadaster attribution. [Official guidance](https://www.cbs.nl/en-gb/about-us/website/copyright)
- Permission applications: No individual copyright permission application is needed within CC BY 4.0's scope; check the distribution page for any specific terms. [Official guidance](https://creativecommons.org/licenses/by/4.0/)

This explanation is informational, not a formal grant of permission or a legal determination. Check the official terms and NOTICE yourself for the conditions and application requirements applicable to your intended use; contact the provider if anything is unclear.

### Attribution, modification and approval notices

Attribution and modification notices recorded in the NOTICE (original wording):

> Source: CBS and Kadaster, Wijk- en Buurtkaart 2026 versie 0.
>
> Derived and processed by Galuchat. Not endorsed by CBS or Kadaster.
>
> Source: CBS, Gemeentelijke indeling op 1 januari 2026.
>
> Derived and processed by Galuchat. Not endorsed by CBS.

## Usage notes

Always use a map and dictionary from the same ZIP. Typically choose one WGSMapSet at a suitable resolution and the UTF-8 dictionary. Pixel value 0 denotes an unset area. Sizes are actual file sizes, not runtime memory usage. Pixel distances are approximate north-south distances.

See the ZIP's `data-spec.md` for coverage, names, attributes and limitations, and `NOTICE.md` for sources, processing, attribution and terms of use.
