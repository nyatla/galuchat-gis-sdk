# Worldwide administrative boundaries

English | [日本語](world-2024-geoboundaries-org-cgaz-adm.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

geoBoundaries CGAZ best-available administrative areas. Selects the most detailed available ADM2, ADM1, ADM0 or disputed-area boundaries for each shapeGroup.

## Area counts

There are **49,349 areas by dictionary code** (GisWordBook leaf records). This is not a count of parent areas, polygons, or areas represented by pixels at each resolution.

This figure describes dictionary entries and is distinct from a source-area count.

## Download

[Download world-2024-geoboundaries-org-cgaz-adm.zip (22.93 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/world-2024-geoboundaries-org-cgaz-adm.zip)

## Map resolutions and sizes

| unitInv | Approx. pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 2.81 MiB |
| 1000 (default) | approx. 111 m | 20.45 MiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 561.2 KiB |
| UTF-16LE | 561.4 KiB |

### GisWordBook structure

Each record is a fixed-length StringSet with 3 slots in the order below. Empty values are retained as `""`; later slots are not shifted forward.

| Position | Slot | Meaning | Empty values |
| ---: | --- | --- | --- |
| 1 | Area 1 | Source group identifier (`shapeGroup`), e.g. `JPN` | Required |
| 2 | Attribute 1 | Selected source level (`shapeType`): `ADM2`, `ADM1`, `ADM0` or `DISP` | Required |
| 3 | Area 2 | `shapeName`; falls back to `shapeID` when the name is empty | Required |

This is not a country → ADM1 → ADM2 hierarchy: the second slot records the selected source level, and levels are mixed across regions. `shapeGroup` is a source identifier, not a translated country name. UTF-8 and UTF-16LE versions are provided; there is no Shift_JIS version.

Example from the actual data (dictionary code `20675`):

```json
["JPN","ADM2","Chiyoda"]
```

Nonzero map values are dictionary codes. This example corresponds to zero-based leaf-record index `20674`. Code `0` denotes unset areas, not a dictionary record.

## Rendering example

<a href="../../docs/image/world-geoboundaries-cgaz-unit-inv-1000.png"><img src="../../docs/image/world-geoboundaries-cgaz-unit-inv-1000.png" alt="Worldwide administrative boundaries" width="640"></a>

The image is centered around Narashino and rendered at `unitInv=1000`. Blue denotes unset areas; other colors distinguish area codes and have no semantic meaning.

## License and terms of use

Source: William & Mary geoLab / geoBoundaries community, [CGAZ](https://www.geoboundaries.org/globalDownloads.html)

Original-data license / terms: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); [License statement](https://github.com/wmgeolab/geoBoundaries/blob/main/LICENSE)

This package adapts the source for Galuchat. For the processed data's terms of use, refer to the official terms above and the ZIP's `NOTICE.md`.

### Commercial use and permission applications (informational)

- Commercial use: CC BY 4.0 permits commercial use subject to its terms. [Official guidance](https://creativecommons.org/licenses/by/4.0/)
- Permission applications: No individual application to the copyright holder is needed for uses covered by CC BY 4.0. [Official guidance](https://creativecommons.org/licenses/by/4.0/)

This explanation is informational, not a formal grant of permission or a legal determination. Check the official terms and NOTICE yourself for the conditions and application requirements applicable to your intended use; contact the provider if anything is unclear.

### Attribution, modification and approval notices

Attribution and modification notices recorded in the NOTICE (original wording):

> Contains information from geoBoundaries, produced by the William & Mary geoLab and the geoBoundaries community, licensed under CC BY 4.0. Adapted for Galuchat.

## Usage notes

Always use a map and dictionary from the same ZIP. Typically choose one WGSMapSet at a suitable resolution and the UTF-8 dictionary. Pixel value 0 denotes an unset area. Sizes are actual file sizes, not runtime memory usage. Pixel distances are approximate north-south distances.

See the ZIP's `data-spec.md` for coverage, names, attributes and limitations, and `NOTICE.md` for sources, processing, attribution and terms of use.
