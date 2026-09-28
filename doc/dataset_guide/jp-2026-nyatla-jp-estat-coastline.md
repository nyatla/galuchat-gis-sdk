# Japanese e-Stat areas with N03 coastline

English | [日本語](jp-2026-nyatla-jp-estat-coastline.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

Combines 2020 e-Stat small areas with the extent represented by N03-2026 administrative-area rasters. Small areas are retained within that extent; gaps are filled with representative administrative-area values. Values outside the N03 extent are zero.

## Area counts

There are **209,445 areas by dictionary code** (GisWordBook leaf records). This is not a count of parent areas, polygons, or areas represented by pixels at each resolution.

This figure describes dictionary entries and is distinct from a source-area count.

## Download

[Download jp-2026-nyatla-jp-estat-coastline.zip (26.06 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.1/jp-2026-nyatla-jp-estat-coastline.zip)

## Map resolutions and sizes

| unitInv | Approx. pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 10000 (default) | approx. 11 m | 24.07 MiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 1.66 MiB |
| Shift_JIS | 1.66 MiB |
| UTF-16LE | 1.66 MiB |

### GisWordBook structure

Each record is a fixed-length StringSet with 6 slots in the order below. Empty values are retained as `""`; later slots are not shifted forward.

| Position | Slot | Meaning | Empty values |
| ---: | --- | --- | --- |
| 1 | Area 1 | Prefecture | Required |
| 2 | Area 2 | District / gun | Empty if absent |
| 3 | Area 3 | Municipality | Required |
| 4 | Area 4 | Ward of a designated city | Empty if absent |
| 5 | Area 5 | e-Stat small area | Empty for an N03 administrative-area representative |
| 6 | Area 6 | e-Stat lower-level section | Empty if absent |

Records with both areas 5 and 6 empty represent N03 administrative areas; e-Stat small areas are placed under the N03 hierarchy. There is no subprefecture slot or shared country-name slot. Codes identify dictionary entries, not individual polygons.

Example from the actual data (dictionary code `70657`):

```json
["東京都","","千代田区","","丸の内","一丁目"]
```

Nonzero map values are dictionary codes. This example corresponds to zero-based leaf-record index `70656`. Code `0` denotes unset areas, not a dictionary record.

## Rendering example

<a href="../../docs/image/jp-gis-estat-integrated-unit-inv-10000.png"><img src="../../docs/image/jp-gis-estat-integrated-unit-inv-10000.png" alt="Japanese e-Stat areas with N03 coastline" width="640"></a>

The image is centered around Narashino and rendered at `unitInv=10000`. Blue denotes unset areas; other colors distinguish area codes and have no semantic meaning.

## License and terms of use

Source: MLIT [N03-20260101](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html) and Statistics Bureau of Japan / e-Stat [2020 Census small-area boundary data](https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=A&toukeiCode=00200521&toukeiYear=2020&serveyId=A002005212020&coordsys=1&format=shape&datum=2011)

Original-data license / terms: [N03: CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); [MLIT download-site terms](https://nlftp.mlit.go.jp/ksj/other/agreement.html); [e-Stat terms (compatible with CC BY 4.0)](https://www.e-stat.go.jp/terms-of-use)

This package adapts the source for Galuchat. For the processed data's terms of use, refer to the official terms above and the ZIP's `NOTICE.md`.

### Commercial use and permission applications (informational)

- Commercial use: Both N03's CC BY 4.0 and the e-Stat terms permit commercial use subject to their conditions; both sources' terms are relevant to this integrated dataset. [Official guidance](https://www.e-stat.go.jp/terms-of-use)
- Permission applications: Individual copyright permission applications are generally unnecessary within each source's grant. However, the NOTICE records a pending recheck of the Survey Act approval's scope for the integrated product. This guide does not determine the application's necessity for this package; consult the NOTICE and GSI guidance. [Official guidance](https://service.gsi.go.jp/onestop/navi/nav3/)

This explanation is informational, not a formal grant of permission or a legal determination. Check the official terms and NOTICE yourself for the conditions and application requirements applicable to your intended use; contact the provider if anything is unclear.

### Attribution, modification and approval notices

Attribution and modification notices recorded in the NOTICE (original wording):

> 出典：国土交通省国土数値情報ダウンロードサイト（https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html）
>
> 「国土数値情報（行政区域データ）」（国土交通省）をもとにGaluchat用に加工して作成
>
> 出典：「令和2年国勢調査 町丁・字等境界データ」（総務省統計局、政府統計の総合窓口（e-Stat））をGaluchat用に加工して作成

Approval notice recorded in the NOTICE for the map and `X7115_metadata.xml` (scope recheck recorded):

> 測量法に基づく国土地理院長承認（使用）R 8JHs 319

## Usage notes

Always use a map and dictionary from the same ZIP. Typically choose one WGSMapSet at a suitable resolution and the UTF-8 dictionary. Pixel value 0 denotes an unset area. Sizes are actual file sizes, not runtime memory usage. Pixel distances are approximate north-south distances.

See the ZIP's `data-spec.md` for coverage, names, attributes and limitations, and `NOTICE.md` for sources, processing, attribution and terms of use.
