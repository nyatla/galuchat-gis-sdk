# English / ASCII language pack

English | [日本語](en.ja.md)

The [en rev1 language pack (29.36 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.7/galuchat-languagepack-en-rev1.zip) covers 46 map datasets and the optional e-Stat four-level dictionary. Its `rev1` is the language pack's own revision.

## Use

1. Download the map ZIP listed in the [dataset guide](../../datasets/README.md) and the language pack ZIP.
2. Open `galuchat-languagepack-en/datasets/<source ZIP name without .zip>/`, matching its `revN`. For the optional e-Stat four-level dictionary, use its `subdiv` ZIP name.
3. Keep the map file and load `.en.giswordbook` in place of the original dictionary. Read the adjacent `NOTICE.md` for sources and terms.

For an implementation example, replace the dictionary path in the [Python Get Started](../../python/getstarted/README.md) with the `.en.giswordbook` path.

The dictionaries use UTF-8 with printable ASCII display names, which are not always official English names. Each directory contains a `.en.names.csv` comparison table; the pack's `README.md` lists the matching source ZIPs.
