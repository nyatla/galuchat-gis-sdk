# Czech RÚIAN municipalities, 2026

English | [日本語](cz-2026-cuzk-gov-cz-ruian-adm-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

This package contains municipalities and military areas in Czechia, converted from the source described in the ZIP's `data-spec.md`. Nonzero WGSMapSet pixel values are codes in the accompanying GisWordBook. `names.csv` maps those codes to source identifiers.

## Area counts

**6,258 areas by dictionary code.** The parent levels in the name hierarchy are not separate map pixel values. The source specification records the underlying area counts and any special cases.

## Download

[Download cz-2026-cuzk-gov-cz-ruian-adm-rev1.zip (3.47 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.2/cz-2026-cuzk-gov-cz-ruian-adm-rev1.zip)

The download link becomes available after v0.2.2 is published; the ZIP is prepared locally.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | File | Size |
| ---: | ---: | --- | ---: |
| 100 | about 1.1 km | `czechia_ruian_2026-grid-512-100.wgsmapset.glc` | 53.6 KiB |
| 1000 (default) | about 111 m | `czechia_ruian_2026-grid-4096-1000.wgsmapset.glc` | 401.4 KiB |
| 10000 | about 11 m | `czechia_ruian_2026-grid-8192-10000.wgsmapset.glc` | 2.85 MiB |

## GisWordBooks and structure

| Encoding | File | Size |
| --- | --- | ---: |
| UTF-8 | `czechia_ruian_2026.giswordbook` | 133.2 KiB |
| UTF-16LE | `czechia_ruian_2026.utf16.giswordbook` | 133.3 KiB |

Each dictionary record has 4 fixed StringSet slots:

| Slot | Meaning |
| ---: | --- |
| 1 | Region (VÚSC) |
| 2 | District (Okres) |
| 3 | Municipality or military area |
| 4 | Source KOD |

Actual record at dictionary code `1`:

```json
["Olomoucký kraj","Šumperk","Petrov nad Desnou","500020"]
```

Use a map and dictionary from the same ZIP. Pixel code `0` denotes background, not a separate water class. The `names.csv` file preserves source IDs.

## Rendering example

<a href="../../docs/image/cz-2026-cuzk-gov-cz-ruian-adm-unit-inv-1000.png"><img src="../../docs/image/cz-2026-cuzk-gov-cz-ruian-adm-unit-inv-1000.png" alt="Municipalities and military areas near the national capital" width="640"></a>

Rendered from the `unitInv=1000` map; colors distinguish codes without semantic meaning.

## License and terms of use

Source: [Original provider page](https://services.cuzk.gov.cz/). The source terms recorded in the ZIP's `NOTICE.md` are **CC BY 4.0**; see the [Official terms](https://creativecommons.org/licenses/by/4.0/).

### Commercial use and permission applications (informational)

The cited terms permit commercial reuse; the NOTICE does not identify a separate permission application for ordinary reuse. This summary is informational, not a formal grant of permission or a legal determination. Verify the current official terms and the ZIP's `NOTICE.md` for your intended use.

### Attribution, modification and approval notices

Keep the source attribution and processing information in the ZIP's `NOTICE.md` when redistributing the processed product. Do not present it as an official or endorsed product of the source provider.
