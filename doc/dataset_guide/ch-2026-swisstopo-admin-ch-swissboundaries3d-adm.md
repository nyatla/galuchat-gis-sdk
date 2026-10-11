# Swiss swissBOUNDARIES3D base areas, 2026

English | [日本語](ch-2026-swisstopo-admin-ch-swissboundaries3d-adm.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

This package contains municipalities and other base areas in Switzerland, converted from the source described in the ZIP's `data-spec.md`. Nonzero WGSMapSet pixel values are codes in the accompanying GisWordBook. `names.csv` maps those codes to source identifiers.

## Area counts

**2,123 areas by dictionary code.** The parent levels in the name hierarchy are not separate map pixel values. The source specification records the underlying area counts and any special cases.

## Download

[Download ch-2026-swisstopo-admin-ch-swissboundaries3d-adm-rev1.zip (1.19 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/ch-2026-swisstopo-admin-ch-swissboundaries3d-adm-rev1.zip)

The download link becomes available after v0.2.4 is published; the ZIP is prepared locally.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | File | Size |
| ---: | ---: | --- | ---: |
| 100 | about 1.1 km | `switzerland_swissboundaries3d_2026-grid-512-100.wgsmapset.glc` | 19.1 KiB |
| 1000 (default) | about 111 m | `switzerland_swissboundaries3d_2026-grid-4096-1000.wgsmapset.glc` | 141.2 KiB |
| 10000 | about 11 m | `switzerland_swissboundaries3d_2026-grid-8192-10000.wgsmapset.glc` | 1018.2 KiB |

## GisWordBooks and structure

| Encoding | File | Size |
| --- | --- | ---: |
| UTF-8 | `switzerland_swissboundaries3d_2026.giswordbook` | 37.7 KiB |
| UTF-16LE | `switzerland_swissboundaries3d_2026.utf16.giswordbook` | 37.8 KiB |

Each dictionary record has 4 fixed StringSet slots:

| Slot | Meaning |
| ---: | --- |
| 1 | Canton |
| 2 | District (may be empty) |
| 3 | Base-area name |
| 4 | Source area type (OBJEKTART) |

Actual record at dictionary code `1`:

```json
["Zürich","Affoltern","Affoltern am Albis","Gemeindegebiet"]
```

Use a map and dictionary from the same ZIP. Pixel code `0` denotes background, not a separate water class. The `names.csv` file preserves source IDs.

## Rendering example

<a href="../../docs/image/ch-2026-swisstopo-admin-ch-swissboundaries3d-adm-unit-inv-1000.png"><img src="../../docs/image/ch-2026-swisstopo-admin-ch-swissboundaries3d-adm-unit-inv-1000.png" alt="Municipalities and other base areas near the national capital" width="640"></a>

Rendered from the `unitInv=1000` map; colors distinguish codes without semantic meaning.

## License and terms of use

Source: [Original provider page](https://www.swisstopo.admin.ch/en/landscape-model-swissboundaries3d). The source terms recorded in the ZIP's `NOTICE.md` are **swisstopo free-geodata terms**; see the [Official terms](https://www.swisstopo.admin.ch/en/terms-of-use-free-geodata-and-geoservices).

### Commercial use and permission applications (informational)

The cited terms permit commercial reuse; the NOTICE does not identify a separate permission application for ordinary reuse. This summary is informational, not a formal grant of permission or a legal determination. Verify the current official terms and the ZIP's `NOTICE.md` for your intended use.

### Attribution, modification and approval notices

Keep the source attribution and processing information in the ZIP's `NOTICE.md` when redistributing the processed product. Do not present it as an official or endorsed product of the source provider.
