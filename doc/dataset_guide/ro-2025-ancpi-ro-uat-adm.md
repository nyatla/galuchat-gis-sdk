# Romanian ANCPI local administrative areas, 2025

English | [日本語](ro-2025-ancpi-ro-uat-adm.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

This package contains uat and bucharest sectors in Romania, converted from the source described in the ZIP's `data-spec.md`. Nonzero WGSMapSet pixel values are codes in the accompanying GisWordBook. `names.csv` maps those codes to source identifiers.

## Area counts

**3,186 areas by dictionary code.** The parent levels in the name hierarchy are not separate map pixel values. The source specification records the underlying area counts and any special cases.

## Download

[Download ro-2025-ancpi-ro-uat-adm-rev1.zip (3.49 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/ro-2025-ancpi-ro-uat-adm-rev1.zip)

The download link becomes available after v0.2.4 is published; the ZIP is prepared locally.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | File | Size |
| ---: | ---: | --- | ---: |
| 100 | about 1.1 km | `romania_uat_2025-grid-512-100.wgsmapset.glc` | 57.6 KiB |
| 1000 (default) | about 111 m | `romania_uat_2025-grid-4096-1000.wgsmapset.glc` | 438.0 KiB |
| 10000 | about 11 m | `romania_uat_2025-grid-8192-10000.wgsmapset.glc` | 3.09 MiB |

## GisWordBooks and structure

| Encoding | File | Size |
| --- | --- | ---: |
| UTF-8 | `romania_uat_2025.giswordbook` | 37.3 KiB |
| UTF-16LE | `romania_uat_2025.utf16.giswordbook` | 37.4 KiB |

Each dictionary record has 3 fixed StringSet slots:

| Slot | Meaning |
| ---: | --- |
| 1 | County or Bucharest |
| 2 | UAT or Bucharest sector |
| 3 | UAT type |

Actual record at dictionary code `1`:

```json
["ALBA","CIUGUD","Comuna"]
```

Use a map and dictionary from the same ZIP. Pixel code `0` denotes background, not a separate water class. The `names.csv` file preserves source IDs.

## Rendering example

<a href="../../docs/image/ro-2025-ancpi-ro-uat-adm-unit-inv-1000.png"><img src="../../docs/image/ro-2025-ancpi-ro-uat-adm-unit-inv-1000.png" alt="UAT and Bucharest sectors near the national capital" width="640"></a>

Rendered from the `unitInv=1000` map; colors distinguish codes without semantic meaning.

## License and terms of use

Source: [Original provider page](https://geoportal.ancpi.ro/portal/apps/webappviewer/index.html?id=faeba2d173374445b1f13512bd477bb2). The source terms recorded in the ZIP's `NOTICE.md` are **OGL ROU 1.0 / ANCPI open-information licence**; see the [Official terms](https://geoportal.ancpi.ro/portal/sharing/rest/content/items/8077dd16e957477d9cc9b457f5f17cac/data).

### Commercial use and permission applications (informational)

The cited terms permit commercial reuse; the NOTICE does not identify a separate permission application for ordinary reuse. This summary is informational, not a formal grant of permission or a legal determination. Verify the current official terms and the ZIP's `NOTICE.md` for your intended use.

### Attribution, modification and approval notices

Keep the source attribution and processing information in the ZIP's `NOTICE.md` when redistributing the processed product. Do not present it as an official or endorsed product of the source provider.
