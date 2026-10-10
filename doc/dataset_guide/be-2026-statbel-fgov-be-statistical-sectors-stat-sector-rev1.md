# Belgian statistical sectors, 2026

English | [日本語](be-2026-statbel-fgov-be-statistical-sectors-stat-sector-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

This package contains statistical sectors in Belgium, converted from the source described in the ZIP's `data-spec.md`. Nonzero WGSMapSet pixel values are codes in the accompanying GisWordBook. `names.csv` maps those codes to source identifiers.

## Area counts

**20,781 areas by dictionary code.** The parent levels in the name hierarchy are not separate map pixel values. The source specification records the underlying area counts and any special cases.

## Download

[Download be-2026-statbel-fgov-be-statistical-sectors-stat-sector-rev1.zip (4.90 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.2/be-2026-statbel-fgov-be-statistical-sectors-stat-sector-rev1.zip)

The download link becomes available after v0.2.2 is published; the ZIP is prepared locally.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | File | Size |
| ---: | ---: | --- | ---: |
| 100 | about 1.1 km | `belgium_statbel_2026-grid-512-100.wgsmapset.glc` | 52.6 KiB |
| 1000 (default) | about 111 m | `belgium_statbel_2026-grid-4096-1000.wgsmapset.glc` | 464.5 KiB |
| 10000 | about 11 m | `belgium_statbel_2026-grid-8192-10000.wgsmapset.glc` | 3.12 MiB |

## GisWordBooks and structure

| Encoding | File | Size |
| --- | --- | ---: |
| UTF-8 | `belgium_statbel_2026.giswordbook` | 509.0 KiB |
| UTF-16LE | `belgium_statbel_2026.utf16.giswordbook` | 509.0 KiB |

Each dictionary record has 6 fixed StringSet slots:

| Slot | Meaning |
| ---: | --- |
| 1 | Region |
| 2 | Province (empty in Brussels) |
| 3 | Arrondissement |
| 4 | Municipality |
| 5 | Statistical sector |
| 6 | Source sector code |

Actual record at dictionary code `1`:

```json
["Vlaams Gewest","Provincie Antwerpen","Arrondissement Antwerpen","Aartselaar","DE LEEUWERIK","11001A01-"]
```

Use a map and dictionary from the same ZIP. Pixel code `0` denotes background, not a separate water class. The `names.csv` file preserves source IDs.

## Rendering example

<a href="../../docs/image/be-2026-statbel-fgov-be-statistical-sectors-stat-sector-unit-inv-1000.png"><img src="../../docs/image/be-2026-statbel-fgov-be-statistical-sectors-stat-sector-unit-inv-1000.png" alt="Statistical sectors near the national capital" width="640"></a>

Rendered from the `unitInv=1000` map; colors distinguish codes without semantic meaning.

## License and terms of use

Source: [Original provider page](https://statbel.fgov.be/fr/open-data/secteurs-statistiques-2026). The source terms recorded in the ZIP's `NOTICE.md` are **Statbel Licence open data**; see the [Official terms](https://statbel.fgov.be/sites/default/files/files/opendata/Licence%20open%20data_FR.pdf). The ZIP also carries the original French and Dutch licence PDFs.

### Commercial use and permission applications (informational)

The cited terms permit commercial reuse; the NOTICE does not identify a separate permission application for ordinary reuse. This summary is informational, not a formal grant of permission or a legal determination. Verify the current official terms and the ZIP's `NOTICE.md` for your intended use.

### Attribution, modification and approval notices

Keep the source attribution and processing information in the ZIP's `NOTICE.md` when redistributing the processed product. Do not present it as an official or endorsed product of the source provider.
