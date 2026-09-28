# French administrative areas, ADMIN EXPRESS COG 2026

English | [日本語](fr-2026-cartes-gouv-fr-admin-express-cog-adm.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

IGN ADMIN EXPRESS COG 4.0, as of 2026-01-01. Covers communes and municipal arrondissements in Paris, Lyon and Marseille, across mainland France including Corsica, five DROM and Saint-Pierre-et-Miquelon. Source INSEE identifiers are in names.csv.

## Area counts

There are **34,919 areas by dictionary code** (GisWordBook leaf records). This is not a count of parent areas, polygons, or areas represented by pixels at each resolution.

There are 34,919 adopted communes / municipal arrondissements. No matching name paths are merged into shared dictionary codes in this release.

## Download

[Download fr-2026-cartes-gouv-fr-admin-express-cog-adm.zip (18.56 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/fr-2026-cartes-gouv-fr-admin-express-cog-adm.zip)

## Map resolutions and sizes

| unitInv | Approx. pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 300.5 KiB |
| 1000 (default) | approx. 111 m | 2.22 MiB |
| 10000 | approx. 11 m | 15.60 MiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 578.5 KiB |
| UTF-16LE | 578.3 KiB |

See the included `names.csv` for source area identifiers.

### GisWordBook structure

Each record is a fixed-length StringSet with 4 slots in the order below. Empty values are retained as `""`; later slots are not shifted forward.

| Position | Slot | Meaning | Empty values |
| ---: | --- | --- | --- |
| 1 | Area 1 | Région (`RGN_NAME`) | Empty if absent |
| 2 | Area 2 | Département (`DEP_NAME`) | Empty if absent |
| 3 | Area 3 | Commune (`COM_NAME`); parent commune for a municipal arrondissement | Required |
| 4 | Area 4 | Arrondissement municipal (`ARR_NAME`) | Empty if absent |

Ordinary communes have an empty fourth slot. The two Saint-Pierre-et-Miquelon areas have empty region and department slots. There is no shared France slot or INSEE-code slot. Original French spelling is preserved and names are compared using all four slots, not the commune name alone.

Example from the actual data (dictionary code `135`):

```json
["Île-de-France","Paris","Paris","Paris 4e Arrondissement"]
```

Nonzero map values are dictionary codes. This example corresponds to zero-based leaf-record index `134`. Code `0` denotes unset areas, not a dictionary record.

## Rendering example

<a href="../../docs/image/fr-admin-express-cog-2026-unit-inv-1000.png"><img src="../../docs/image/fr-admin-express-cog-2026-unit-inv-1000.png" alt="French administrative areas, ADMIN EXPRESS COG 2026" width="640"></a>

The image is centered around Paris and rendered at `unitInv=1000`. Blue denotes unset areas; other colors distinguish area codes and have no semantic meaning.

## License and terms of use

Source: Institut national de l'information géographique et forestière (IGN), [ADMIN EXPRESS COG](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_ADMIN-EXPRESS)

Original-data license / terms: [Licence Ouverte / Open Licence 2.0（Etalab）](https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf)

This package adapts the source for Galuchat. For the processed data's terms of use, refer to the official terms above and the ZIP's `NOTICE.md`.

### Commercial use and permission applications (informational)

- Commercial use: Licence Ouverte 2.0 permits commercial use subject to its terms. [Official guidance](https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf)
- Permission applications: An individual permission application is generally unnecessary for data uses covered by the license. [Official guidance](https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf)

This explanation is informational, not a formal grant of permission or a legal determination. Check the official terms and NOTICE yourself for the conditions and application requirements applicable to your intended use; contact the provider if anything is unclear.

### Attribution, modification and approval notices

Attribution and modification notices recorded in the NOTICE (original wording):

> Source: IGN, ADMIN EXPRESS COG 4.0, edition 2026-01-01.
>
> Derived and processed by Galuchat. Not endorsed by IGN or INSEE.

## Usage notes

Always use a map and dictionary from the same ZIP. Typically choose one WGSMapSet at a suitable resolution and the UTF-8 dictionary. Pixel value 0 denotes an unset area. Sizes are actual file sizes, not runtime memory usage. Pixel distances are approximate north-south distances.

See the ZIP's `data-spec.md` for coverage, names, attributes and limitations, and `NOTICE.md` for sources, processing, attribution and terms of use.
