# Galuchat GIS SDK datasets

English | [日本語](README.ja.md)

The `datasets/` directory contains WGSMapSet/3 and GisWordBook/0 files shared by the JavaScript, Java, and Python implementations.

Each dataset directory contains the following files:

```text
manifest.json          Resolution, encoding, defaults, sizes, and SHA-256 hashes
NOTICE.md              Sources, processing, and terms of use
*.wgsmapset.glc        Map for reading region codes at points or within rectangles
*.giswordbook          WordBook for resolving region codes to place-name hierarchies
```

Always use a map and WordBook from the same dataset. Maps at different resolutions within a dataset share the same value-code system. WordBooks in different encodings also share the same content and place-name codes; the UTF-8 edition is the default.

The current standard readers and Get Started examples use UTF-8. To use the Shift_JIS or UTF-16 edition, select a compatible reader and use the `tokenEncoding` recorded in the manifest.

## Included datasets

The SDK includes four GIS datasets with different coverage and spatial granularity.

| dataset id | Coverage | Primary use | Included resolutions (`unitInv`) |
| --- | --- | --- | --- |
| `jp-admin-n03` | Administrative areas of Japan | Identifying prefectures, municipalities, and designated-city wards | 100, 250, 1000, 2500, 10000 |
| `jp-estat-r2ka-2020` | Japanese town-block and small-area boundaries | Identifying town blocks and census small areas | 5000, 10000 |
| `jp-gis-estat-integrated` | Integrated administrative and town-block boundaries | Reverse geocoding from administrative areas through small areas | 10000 |
| `world-geoboundaries-cgaz` | Global administrative boundaries | Identifying countries and administrative areas worldwide | 100, 1000 |

`unitInv` is the number of pixels per degree. For example, with `unitInv=1000`, one pixel corresponds to 1/1000 degree in both latitude and longitude.

## Reading the rendering examples

Every image below contains 1024 × 768 pixels read from a WGSMapSet and is centered near Funabashi, Japan (139.9825° E, 35.6947° N).

One GLC pixel maps directly to one image pixel, with no scaling. Lower-resolution data therefore covers a wider area, while higher-resolution data shows the area around Funabashi in greater detail.

Pixel value `0` is rendered in blue and represents unset areas such as the sea. Positive pixel values are region codes and are colored in HSV space to make different codes visible. The display colors have no administrative meaning.

| unitInv | Approximate north-south distance per pixel | Longitude/latitude span shown |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 10.24 × 7.68 degrees |
| 250 | approx. 445 m | 4.096 × 3.072 degrees |
| 1000 | approx. 111 m | 1.024 × 0.768 degrees |
| 2500 | approx. 45 m | 0.4096 × 0.3072 degrees |
| 5000 | approx. 22 m | 0.2048 × 0.1536 degrees |
| 10000 | approx. 11 m | 0.1024 × 0.0768 degrees |

Distances are approximate north-south values. The physical east-west distance varies with latitude. Click an image to view it at its original size.

## Data sizes and selection

Higher resolution represents boundaries and coastlines in greater detail, but also increases the GLC file size. Select a dataset and resolution according to the required spatial granularity, distribution size, and available storage.

| dataset | unitInv | GLC size |
| --- | ---: | ---: |
| `jp-admin-n03` | 100 | approx. 52 KiB |
|  | 250 | approx. 123 KiB |
|  | 1000 | approx. 479 KiB |
|  | 2500 | approx. 1.17 MiB |
|  | 10000 | approx. 4.48 MiB |
| `jp-estat-r2ka-2020` | 5000 | approx. 12.94 MiB |
|  | 10000 | approx. 22.70 MiB |
| `jp-gis-estat-integrated` | 10000 | approx. 24.16 MiB |
| `world-geoboundaries-cgaz` | 100 | approx. 2.81 MiB |
|  | 1000 | approx. 20.45 MiB |

To retrieve place-name hierarchies, use a GisWordBook from the same dataset in addition to the GLC. Approximate sizes of the UTF-8 editions used by the standard readers are shown below.

| dataset | UTF-8 GisWordBook size |
| --- | ---: |
| `jp-admin-n03` | approx. 31 KiB |
| `jp-estat-r2ka-2020` | approx. 1.63 MiB |
| `jp-gis-estat-integrated` | approx. 1.66 MiB |
| `world-geoboundaries-cgaz` | approx. 561 KiB |

For most applications, one suitable GLC and one GisWordBook in the required encoding are sufficient. You do not need to include every GLC and every WordBook encoding unless the application switches among multiple resolutions or encodings.

These are approximate sizes of the files currently included. See each dataset's `manifest.json` for exact byte counts, default selections, and SHA-256 hashes. File sizes indicate distribution and storage requirements; they do not represent runtime memory usage by a reader or application.

## Japanese administrative areas (`jp-admin-n03`)

This dataset is based on the Japanese Ministry of Land, Infrastructure, Transport and Tourism's National Land Numerical Information Administrative Area Data N03.

It identifies prefectures, municipalities, counties, and designated-city wards. Five resolutions are included, supporting uses ranging from wide-area visualization to detailed identification near municipal boundaries.

<table>
  <tr>
    <th>unitInv 100</th>
    <th>unitInv 250</th>
    <th>unitInv 1000</th>
  </tr>
  <tr>
    <td><a href="../docs/image/jp-admin-n03-unit-inv-100.png"><img src="../docs/image/jp-admin-n03-unit-inv-100.png" alt="jp-admin-n03 unitInv 100"></a></td>
    <td><a href="../docs/image/jp-admin-n03-unit-inv-250.png"><img src="../docs/image/jp-admin-n03-unit-inv-250.png" alt="jp-admin-n03 unitInv 250"></a></td>
    <td><a href="../docs/image/jp-admin-n03-unit-inv-1000.png"><img src="../docs/image/jp-admin-n03-unit-inv-1000.png" alt="jp-admin-n03 unitInv 1000"></a></td>
  </tr>
  <tr>
    <th>unitInv 2500</th>
    <th>unitInv 10000</th>
    <th></th>
  </tr>
  <tr>
    <td><a href="../docs/image/jp-admin-n03-unit-inv-2500.png"><img src="../docs/image/jp-admin-n03-unit-inv-2500.png" alt="jp-admin-n03 unitInv 2500"></a></td>
    <td><a href="../docs/image/jp-admin-n03-unit-inv-10000.png"><img src="../docs/image/jp-admin-n03-unit-inv-10000.png" alt="jp-admin-n03 unitInv 10000"></a></td>
    <td></td>
  </tr>
</table>

`unitInv=100` provides a broad view of Japan, `unitInv=1000` shows the Tokyo Bay area, and `unitInv=10000` reveals finer administrative-area shapes around ports and coastlines.

See the [jp-admin-n03 NOTICE](jp-admin-n03/NOTICE.md) for sources and terms of use.

## e-Stat town-block and small-area boundaries (`jp-estat-r2ka-2020`)

This dataset is based on the Statistics Bureau of Japan's 2020 Population Census town-block and small-area boundary data.

It contains statistical areas finer than ordinary administrative divisions and can be used for reverse geocoding at the town-block, small-area, and subordinate-area levels. These boundaries are defined for statistical surveys and may not match general administrative divisions or official addressing areas.

<table>
  <tr>
    <th>unitInv 5000</th>
    <th>unitInv 10000</th>
  </tr>
  <tr>
    <td><a href="../docs/image/jp-estat-r2ka-2020-unit-inv-5000.png"><img src="../docs/image/jp-estat-r2ka-2020-unit-inv-5000.png" alt="jp-estat-r2ka-2020 unitInv 5000"></a></td>
    <td><a href="../docs/image/jp-estat-r2ka-2020-unit-inv-10000.png"><img src="../docs/image/jp-estat-r2ka-2020-unit-inv-10000.png" alt="jp-estat-r2ka-2020 unitInv 10000"></a></td>
  </tr>
</table>

Compared with N03, this dataset contains many more finely divided regions, illustrating the difference in spatial granularity.

See the [jp-estat-r2ka-2020 NOTICE](jp-estat-r2ka-2020/NOTICE.md) for sources and terms of use.

## Integrated GIS and e-Stat data (`jp-gis-estat-integrated`)

This dataset integrates N03 administrative areas with e-Stat town-block and small-area boundaries.

A single GisWordBook provides both administrative hierarchies, such as prefectures and municipalities, and town-block or small-area hierarchies. Land areas for which e-Stat defines no small area are supplemented with N03 administrative-area information.

<a href="../docs/image/jp-gis-estat-integrated-unit-inv-10000.png"><img src="../docs/image/jp-gis-estat-integrated-unit-inv-10000.png" alt="jp-gis-estat-integrated unitInv 10000" width="640"></a>

This is the standard dataset when administrative areas and small areas need to be handled as one hierarchy.

See the [jp-gis-estat-integrated NOTICE](jp-gis-estat-integrated/NOTICE.md) for sources and terms of use.

## Global administrative boundaries (`world-geoboundaries-cgaz`)

This dataset is based on the global administrative boundaries from geoBoundaries CGAZ.

It supports point identification worldwide. For each region, it includes the most detailed available boundary among ADM2, ADM1, ADM0, and disputed-area boundaries.

<table>
  <tr>
    <th>unitInv 100</th>
    <th>unitInv 1000</th>
  </tr>
  <tr>
    <td><a href="../docs/image/world-geoboundaries-cgaz-unit-inv-100.png"><img src="../docs/image/world-geoboundaries-cgaz-unit-inv-100.png" alt="world-geoboundaries-cgaz unitInv 100"></a></td>
    <td><a href="../docs/image/world-geoboundaries-cgaz-unit-inv-1000.png"><img src="../docs/image/world-geoboundaries-cgaz-unit-inv-1000.png" alt="world-geoboundaries-cgaz unitInv 1000"></a></td>
  </tr>
</table>

`unitInv=100` is suitable for wide-area lookup with fewer pixels. `unitInv=1000` represents regional administrative boundaries and coastlines in greater detail.

See the [world-geoboundaries-cgaz NOTICE](world-geoboundaries-cgaz/NOTICE.md) for sources and terms of use.
