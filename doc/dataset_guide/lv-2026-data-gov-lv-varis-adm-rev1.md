# Latvian address-register administrative areas, 2026

English | [日本語](lv-2026-data-gov-lv-varis-adm-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

This package contains cities and parishes in Latvia, converted from the source described in the ZIP's `data-spec.md`. Nonzero WGSMapSet pixel values are codes in the accompanying GisWordBook. `names.csv` maps those codes to source identifiers.

## Area counts

**593 areas by dictionary code.** The parent levels in the name hierarchy are not separate map pixel values. The source specification records the underlying area counts and any special cases.

## Download

[Download lv-2026-data-gov-lv-varis-adm-rev1.zip (907.8 KiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.2/lv-2026-data-gov-lv-varis-adm-rev1.zip)

The download link becomes available after v0.2.2 is published; the ZIP is prepared locally.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | File | Size |
| ---: | ---: | --- | ---: |
| 100 | about 1.1 km | `latvia_varis_2026-grid-512-100.wgsmapset.glc` | 13.2 KiB |
| 1000 (default) | about 111 m | `latvia_varis_2026-grid-4096-1000.wgsmapset.glc` | 106.7 KiB |
| 10000 | about 11 m | `latvia_varis_2026-grid-8192-10000.wgsmapset.glc` | 806.6 KiB |

## GisWordBooks and structure

| Encoding | File | Size |
| --- | --- | ---: |
| UTF-8 | `latvia_varis_2026.giswordbook` | 7.8 KiB |
| UTF-16LE | `latvia_varis_2026.utf16.giswordbook` | 7.9 KiB |

Each dictionary record has 2 fixed StringSet slots:

| Slot | Meaning |
| ---: | --- |
| 1 | Municipality or independent city |
| 2 | City or parish (empty for independent cities) |

Actual record at dictionary code `1`:

```json
["Daugavpils",""]
```

Use a map and dictionary from the same ZIP. Pixel code `0` denotes background, not a separate water class. The `names.csv` file preserves source IDs.

## Rendering example

<a href="../../docs/image/lv-2026-data-gov-lv-varis-adm-unit-inv-1000.png"><img src="../../docs/image/lv-2026-data-gov-lv-varis-adm-unit-inv-1000.png" alt="Cities and parishes near the national capital" width="640"></a>

Rendered from the `unitInv=1000` map; colors distinguish codes without semantic meaning.

## License and terms of use

Source: [Original provider page](https://data.gov.lv/dati/eng/dataset/varis-atvertie-dati). The source terms recorded in the ZIP's `NOTICE.md` are **CC BY 4.0**; see the [Official terms](https://creativecommons.org/licenses/by/4.0/).

### Commercial use and permission applications (informational)

The cited terms permit commercial reuse; the NOTICE does not identify a separate permission application for ordinary reuse. This summary is informational, not a formal grant of permission or a legal determination. Verify the current official terms and the ZIP's `NOTICE.md` for your intended use.

### Attribution, modification and approval notices

Keep the source attribution and processing information in the ZIP's `NOTICE.md` when redistributing the processed product. Do not present it as an official or endorsed product of the source provider.
