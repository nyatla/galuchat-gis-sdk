# world-geoboundaries-cgaz NOTICE

This dataset is an adapted work produced from the geoBoundaries Comprehensive Global Administrative Zones (CGAZ) ADM2 global composite by the William & Mary geoLab and the geoBoundaries community.

## Source and attribution

- Source dataset: `geoBoundariesCGAZ_ADM2.zip`
- Product: Comprehensive Global Administrative Zones (CGAZ), ADM2 global Shapefile
- Creator: William & Mary geoLab and the geoBoundaries community
- Source URL: https://www.geoboundaries.org/globalDownloads.html
- Project URL: https://www.geoboundaries.org/
- License: Creative Commons Attribution 4.0 International (CC BY 4.0)
- License URL: https://creativecommons.org/licenses/by/4.0/
- Project license notice: https://github.com/wmgeolab/geoBoundaries/blob/main/LICENSE
- Acquired: 2026-07-25
- Source archive SHA-256: `598f6c70893d60a35b96eb0dc31fd1c045e69177e4b8203407710306f6585de1`
- Source archive member timestamp: 2024-04-20

The source archive has a mutable, unversioned CGAZ filename and does not contain a release manifest. It is therefore identified here as a main-line snapshot by its SHA-256 and archive member timestamp, and is not represented as a numbered geoBoundaries release.

The following attribution must be retained with redistribution:

> Contains information from geoBoundaries, produced by the William & Mary geoLab and the geoBoundaries community, licensed under CC BY 4.0. Adapted for Galuchat.

Recommended citation for the source project:

> Runfola, D., Anderson, A., Baier, H., Crittenden, M., Dowker, E., Fuhrig, S., et al. (2020). geoBoundaries: A global database of political administrative boundaries. PLOS ONE 15(4): e0231866. https://doi.org/10.1371/journal.pone.0231866

## Changes made

- Selected the best available administrative boundary for each `shapeGroup` in the order ADM2, ADM1, ADM0, then DISP
- Assigned dense Galuchat values and generated a `[shapeGroup, shapeType, shapeName]` GisWordBook/0
- Split and rasterized the selected boundaries at 1/100 degree and 1/1000 degree
- Converted and compressed the rasters to WGSMapSet/3 + GI01

## License notice

The geoBoundaries project license permits sharing and adaptation, including commercial use, under CC BY 4.0. Redistribution must give appropriate credit, link to the license and source where practicable, and indicate that changes were made. Attribution must not imply endorsement. Do not impose legal or technological restrictions that prevent recipients from exercising the licensed rights.

CGAZ is a simplified global composite. The project states that disputed areas are removed and replaced using United States Department of State definitions. Administrative boundaries and names are not authoritative for every jurisdiction and may not reflect other positions on disputed territories.

The source and this adapted dataset are provided without warranties. This NOTICE summarizes attribution and provenance and does not replace the CC BY 4.0 license text or any applicable third-party rights identified by geoBoundaries.
