# Brazilian IBGE district boundaries (2022 census)

English | [日本語](br-2022-ibge-gov-br-distritos-adm-rev1.ja.md)

[Back to dataset index](../../datasets/README.md)

## Overview

IBGE district boundaries from the final 2022 census territorial grid, referenced to 31 July 2022.

## Area counts

There are **10,699 areas by dictionary code**. 10,699 leaf areas: 10,698 ordinary districts and one state-level lake operational area. Parent names include 27 federal units and 5,570 municipality-equivalent areas. Parent names are dictionary levels, not additional pixel values. See the ZIP's `data-spec.md` for exact coverage and dates.

## Download

[Download br-2022-ibge-gov-br-distritos-adm-rev1.zip (22.78 MiB)](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/br-2022-ibge-gov-br-distritos-adm-rev1.zip)

This link will work after v0.2.4 is published. The ZIP is already prepared in the local `release/` directory.

## Map resolutions and sizes

| unitInv | Approx. north–south pixel distance | WGSMapSet size |
| ---: | ---: | ---: |
| 100 | approx. 1.1 km | 368.5 KiB |
| 1000 (default) | approx. 111 m | 2.75 MiB |
| 10000 | approx. 11 m | 21.30 MiB |

## Dictionaries

| GisWordBook encoding | Size |
| --- | ---: |
| UTF-8 | 149.1 KiB |
| UTF-16LE | 149.2 KiB |

The included `names.csv` maps dictionary codes to source identifiers and names. Use the map and dictionary from the same ZIP.

### GisWordBook structure

Each record has 3 fixed StringSet slots.

| Position | Meaning |
| ---: | --- |
| 1 | Federal unit name |
| 2 | Municipality-equivalent name; empty for state-level operational area |
| 3 | District or operational-area display name |

Actual example (dictionary code `1`):

```json
["Rio Grande do Sul","","Área operacional: Lagoa dos Patos e Lagoa Mirim"]
```

Nonzero map values are dictionary codes. Code `0` is background and does not identify a dictionary record. Empty slots, where present, are retained rather than shifted.

## Rendering example

<a href="../../docs/image/br-2022-ibge-gov-br-distritos-adm-unit-inv-1000.png"><img src="../../docs/image/br-2022-ibge-gov-br-distritos-adm-unit-inv-1000.png" alt="Districts near Brasília" width="640"></a>

Rendered near Brasília at `unitInv=1000`. Blue denotes background; other colours distinguish area codes without additional meaning.

## License and terms of use

Original data: [official source 1](https://www.ibge.gov.br/estatisticas/sociais/populacao/22827-censo-demografico-2022.html?edicao=41851&t=resultados), [official source 2](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/distritos/shp/BR/BR_distritos_CD2022.zip).

Original licence or terms: **Brazilian federal open-data legislation and IBGE policy; no individual CC licence identified** ([official licence/terms 1](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/decreto/d8777.htm), [official licence/terms 2](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14129.htm), [official licence/terms 3](https://www.ibge.gov.br/acesso-informacao/acoes-e-programas/infraestrutura-nacional-de-dados-abertos-inda.html?lang=pt-BR)). The ZIP's `NOTICE.md` records the source, applicable terms, attribution and processing for this release.

### Commercial use and permission applications (informational)

The cited Brazilian open-data rules are the stated basis for reuse; the source material reviewed does not state an individual prior-approval step. No separate Creative Commons licence is asserted for this edition. Check the current official rules and NOTICE.md. This is informational, not a formal grant of permission or a legal determination.

### Attribution, modification and approval notices

Preserve the source and modification notices specified in the ZIP's `NOTICE.md`. This processed dataset is not presented as an official, approved or endorsed product of the source provider.

## Usage notes

Select one map resolution and one GisWordBook from this ZIP. File sizes are actual uncompressed member sizes; pixel distances are approximate. The source documents in the ZIP define coverage, code mapping and limitations.
