# Lithuanian INSPIRE administrative units, 2026

English | [日本語](lt-2026-geoportal-lt-au-adm-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

This package contains elderships and municipality remainders in Lithuania, converted from the source described in the ZIP's `data-spec.md`. Nonzero WGSMapSet pixel values are codes in the accompanying GisWordBook. `names.csv` maps those codes to source identifiers.

## Area counts

**593 areas by dictionary code.** The source contains 533 elderships and 60 municipalities; the dictionary also represents portions outside elderships. The source specification records the underlying area counts and any special cases.

## Download

[Download lt-2026-geoportal-lt-au-adm-rev1.zip (893.4 KiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.2/lt-2026-geoportal-lt-au-adm-rev1.zip)

The download link becomes available after v0.2.2 is published; the ZIP is prepared locally.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | File | Size |
| ---: | ---: | --- | ---: |
| 100 | about 1.1 km | `lithuania_au_2026-grid-512-100.wgsmapset.glc` | 12.7 KiB |
| 1000 (default) | about 111 m | `lithuania_au_2026-grid-4096-1000.wgsmapset.glc` | 104.8 KiB |
| 10000 | about 11 m | `lithuania_au_2026-grid-8192-10000.wgsmapset.glc` | 790.6 KiB |

## GisWordBooks and structure

| Encoding | File | Size |
| --- | --- | ---: |
| UTF-8 | `lithuania_au_2026.giswordbook` | 9.0 KiB |
| UTF-16LE | `lithuania_au_2026.utf16.giswordbook` | 9.1 KiB |

Each dictionary record has 3 fixed StringSet slots. The empty third slot denotes portions outside an eldership.

| Slot | Meaning |
| ---: | --- |
| 1 | County |
| 2 | Municipality |
| 3 | Eldership (empty outside an eldership) |

Actual record at dictionary code `1`:

```json
["Kauno apskr.","Birštono sav.",""]
```

Use a map and dictionary from the same ZIP. Pixel code `0` denotes background, not a separate water class. The `names.csv` file preserves source IDs.

## Rendering example

<a href="../../docs/image/lt-2026-geoportal-lt-au-adm-unit-inv-1000.png"><img src="../../docs/image/lt-2026-geoportal-lt-au-adm-unit-inv-1000.png" alt="Elderships and municipality remainders near the national capital" width="640"></a>

Rendered from the `unitInv=1000` map; colors distinguish codes without semantic meaning.

## License and terms of use

Source: [Original provider page](https://www.geoportal.lt/metadata-catalog/catalog/search/resource/details.page?uuid=%7B4795E964-7EAC-42BC-8692-376F676AAE1F%7D). The source terms recorded in the ZIP's `NOTICE.md` are **CC BY 4.0**; see the [Official terms](https://creativecommons.org/licenses/by/4.0/).

### Commercial use and permission applications (informational)

The cited terms permit commercial reuse; the NOTICE does not identify a separate permission application for ordinary reuse. This summary is informational, not a formal grant of permission or a legal determination. Verify the current official terms and the ZIP's `NOTICE.md` for your intended use.

### Attribution, modification and approval notices

Keep the source attribution and processing information in the ZIP's `NOTICE.md` when redistributing the processed product. Do not present it as an official or endorsed product of the source provider.
