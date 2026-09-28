# Japanese e-Stat small areas, 2020

English | [日本語](jp-2020-e-stat-go-jp-a002005212020-stat-small-area.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

Town-block and small-area statistical boundaries from the 2020 Population Census. These boundaries do not necessarily match administrative divisions or official addresses.

## Area counts

There are **207,798 areas by dictionary code** (GisWordBook leaf records). This is not a count of parent areas, polygons, or areas represented by pixels at each resolution.

This figure describes dictionary entries and is distinct from a source-area count.

## Download

[Download jp-2020-e-stat-go-jp-a002005212020-stat-small-area.zip (37.09 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/jp-2020-e-stat-go-jp-a002005212020-stat-small-area.zip)

## Map resolutions and sizes

| unitInv | Approx. pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 5000 | approx. 22 m | 12.95 MiB |
| 10000 (default) | approx. 11 m | 22.70 MiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 1.63 MiB |
| Shift_JIS | 1.63 MiB |
| UTF-16LE | 1.63 MiB |

### GisWordBook structure

Each record is a fixed-length StringSet with 4 slots in the order below. Empty values are retained as `""`; later slots are not shifted forward.

| Position | Slot | Meaning | Empty values |
| ---: | --- | --- | --- |
| 1 | Area 1 | Prefecture | Required |
| 2 | Area 2 | Municipality | Required |
| 3 | Area 3 | Small area: town / aza name from the source | Required |
| 4 | Area 4 | Lower-level section from the source | Empty if absent |

There is no shared country-name slot. These are statistical small-area names, not a universal administrative hierarchy. Identical display names can have different dictionary codes.

Example from the actual data (dictionary code `69154`):

```json
["東京都","千代田区","丸の内","一丁目"]
```

Nonzero map values are dictionary codes. This example corresponds to zero-based leaf-record index `69153`. Code `0` denotes unset areas, not a dictionary record.

## Rendering example

<a href="../../docs/image/jp-estat-r2ka-2020-unit-inv-10000.png"><img src="../../docs/image/jp-estat-r2ka-2020-unit-inv-10000.png" alt="Japanese e-Stat small areas, 2020" width="640"></a>

The image is centered around Narashino and rendered at `unitInv=10000`. Blue denotes unset areas; other colors distinguish area codes and have no semantic meaning.

## License and terms of use

Source: Statistics Bureau of Japan / e-Stat [2020 Census small-area boundary data](https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=A&toukeiCode=00200521&toukeiYear=2020&serveyId=A002005212020&coordsys=1&format=shape&datum=2011)

Original-data license / terms: [e-Stat terms (based on Government Standard Terms 2.0; compatible with CC BY 4.0)](https://www.e-stat.go.jp/terms-of-use)

This package adapts the source for Galuchat. For the processed data's terms of use, refer to the official terms above and the ZIP's `NOTICE.md`.

### Commercial use and permission applications (informational)

- Commercial use: The e-Stat terms permit commercial use subject to their conditions. [Official guidance](https://www.e-stat.go.jp/terms-of-use)
- Permission applications: An individual permission application is generally unnecessary for information covered by the terms; check separately for third-party rights or separately specified terms. [Official guidance](https://www.e-stat.go.jp/terms-of-use)

This explanation is informational, not a formal grant of permission or a legal determination. Check the official terms and NOTICE yourself for the conditions and application requirements applicable to your intended use; contact the provider if anything is unclear.

### Attribution, modification and approval notices

Attribution and modification notices recorded in the NOTICE (original wording):

> 出典：「令和2年国勢調査 町丁・字等境界データ」（総務省統計局、政府統計の総合窓口（e-Stat））をGaluchat用に加工して作成

## Usage notes

Always use a map and dictionary from the same ZIP. Typically choose one WGSMapSet at a suitable resolution and the UTF-8 dictionary. Pixel value 0 denotes an unset area. Sizes are actual file sizes, not runtime memory usage. Pixel distances are approximate north-south distances.

See the ZIP's `data-spec.md` for coverage, names, attributes and limitations, and `NOTICE.md` for sources, processing, attribution and terms of use.
