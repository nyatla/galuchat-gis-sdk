# Austrian municipalities and Vienna districts, 2026

English | [日本語](at-2026-data-statistik-gv-at-gem-adm-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

This package contains municipalities and vienna districts in Austria, converted from the source described in the ZIP's `data-spec.md`. Nonzero WGSMapSet pixel values are codes in the accompanying GisWordBook. `names.csv` maps those codes to source identifiers.

## Area counts

**2,114 areas by dictionary code.** The parent levels in the name hierarchy are not separate map pixel values. The source specification records the underlying area counts and any special cases.

## Download

[Download at-2026-data-statistik-gv-at-gem-adm-rev1.zip (1.78 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/at-2026-data-statistik-gv-at-gem-adm-rev1.zip)

The download link becomes available after v0.2.4 is published; the ZIP is prepared locally.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | File | Size |
| ---: | ---: | --- | ---: |
| 100 | about 1.1 km | `austria_gem_2026-grid-512-100.wgsmapset.glc` | 27.0 KiB |
| 1000 (default) | about 111 m | `austria_gem_2026-grid-4096-1000.wgsmapset.glc` | 210.5 KiB |
| 10000 | about 11 m | `austria_gem_2026-grid-8192-10000.wgsmapset.glc` | 1.54 MiB |

## GisWordBooks and structure

| Encoding | File | Size |
| --- | --- | ---: |
| UTF-8 | `austria_gem_2026.giswordbook` | 30.9 KiB |
| UTF-16LE | `austria_gem_2026.utf16.giswordbook` | 31.0 KiB |

Each dictionary record has 2 fixed StringSet slots:

| Slot | Meaning |
| ---: | --- |
| 1 | Federal state (Bundesland) |
| 2 | Municipality or Vienna district |

Actual record at dictionary code `1`:

```json
["Burgenland","Rust"]
```

Use a map and dictionary from the same ZIP. Pixel code `0` denotes background, not a separate water class. The `names.csv` file preserves source IDs.

## Rendering example

<a href="../../docs/image/at-2026-data-statistik-gv-at-gem-adm-unit-inv-1000.png"><img src="../../docs/image/at-2026-data-statistik-gv-at-gem-adm-unit-inv-1000.png" alt="Municipalities and Vienna districts near the national capital" width="640"></a>

Rendered from the `unitInv=1000` map; colors distinguish codes without semantic meaning.

## License and terms of use

Source: [Original provider page](https://data.statistik.gv.at/web/meta.jsp?dataset=OGDEXT_GEM_1). The source terms recorded in the ZIP's `NOTICE.md` are **CC BY 4.0**; see the [Official terms](https://creativecommons.org/licenses/by/4.0/).

### Commercial use and permission applications (informational)

The cited terms permit commercial reuse; the NOTICE does not identify a separate permission application for ordinary reuse. This summary is informational, not a formal grant of permission or a legal determination. Verify the current official terms and the ZIP's `NOTICE.md` for your intended use.

### Attribution, modification and approval notices

Keep the source attribution and processing information in the ZIP's `NOTICE.md` when redistributing the processed product. Do not present it as an official or endorsed product of the source provider.
