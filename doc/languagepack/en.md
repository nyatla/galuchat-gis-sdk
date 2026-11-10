# English / ASCII language pack

English | [日本語](en.ja.md)

The [en rev1 language pack (29.36 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.7/galuchat-languagepack-en-rev1.zip) contains display dictionaries for 46 map datasets and the optional e-Stat four-level dictionary. Its `rev1` is the language pack's own revision; it does not track the SDK version or the source map ZIP revisions.

## Use

1. Download the map ZIP listed in the [dataset guide](../../datasets/README.md) and the language pack ZIP.
2. In the language pack, open `galuchat-languagepack-en/datasets/<map ZIP name without .zip>/`. The full map ZIP name, including its `revN`, must match the directory name. For the optional e-Stat four-level dictionary, use the directory named for its `subdiv` ZIP.
3. Keep the map file, and load that directory's `.en.giswordbook` in place of the map ZIP's original dictionary. Existing SDK readers accept this file directly. Read the adjacent `NOTICE.md` for attribution and terms.

For example, the bundled N03-2026 map pairs with `datasets/jp-2026-mlit-go-jp-n03-adm-rev1/N03-20260101.en.giswordbook` inside the language pack. In the [Python Get Started](../../python/getstarted/README.md), replace the path passed to `GisWordBookReaderAdapter.fromFile(...)` with that extracted file's path; keep the WGSMapSet path unchanged. Other language readers likewise accept a dictionary path or bytes.

The pack's `README.md` lists all 47 matching source ZIPs and files. Each directory also contains a `.en.names.csv` table of original and adopted names. The GisWordBook is UTF-8 and uses printable ASCII for display strings. Names may be official English names, published romanizations, transliterations, or descriptive renderings; they are not all official English translations. The code order and slot structure match the listed source ZIP.
