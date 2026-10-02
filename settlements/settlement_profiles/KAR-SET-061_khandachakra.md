# KAR-SET-061: Manma

*Generated 2026-10-02 by `analysis/hazard_exposure/compile_karnali_79.py` from the province-wide
screening run. All numbers are **derived** from the open datasets listed below; nothing here is a
field observation or a validated result. Sections marked "researcher input" are intentionally empty.*

## Identification

| Field | Value |
|---|---|
| Settlement ID | KAR-SET-061 |
| Name (display / primary script) | Manma / Manma |
| Local level | Khandachakra (urban municipality), P-code NP0664302 |
| District | Kalikot |
| Point (WGS 84) | 81.612609, 29.150365 |
| Selection method | `named_locality_max_buildings` (see docs/methodology.md) |
| Source record | Overture locality `8c60590e-5db7-4c76-8024-b03f7ef8a18f`; OSM `n8309132733@7`; class `town` |

The point is the building-density-selected primary settlement of the local level, **not** an
officially designated headquarters. Confirm or correct it (researcher input).

## Geographic context

- Analysis window: 4 x 4 km centred on the point.
- Building footprints in window: 2,508 (OSM 1,992, Google 470, Microsoft 46; Overture de-duplicated).

## Nearby rivers / water bodies

- Nearest named mapped watercourse: **कर्णाली**, 1,666 m from the point.
- Nearest mapped river-class line: 1,632 m.
- Buildings within 100 m of a mapped river/stream: 99.
- Median HAND of buildings in window: 572.2 m.

## Historical imagery

![Time series](../../outputs/figures/karnali_79/imagery_timeseries/KAR-SET-061_khandachakra_timeseries_1972_2026.png)

| Epoch | Acquired | Platform | Resolution | Scene ID | Chip cloud/shadow/snow fraction |
|---|---|---|---|---|---|
| 1972 | 1972-11-30 | landsat-1 | 60 m | `LM01_L1TP_155040_19721130_02_T2` | 0.0 |
| 1977 | 1976-10-13 | landsat-2 | 60 m | `LM02_L1TP_155040_19761013_02_T2` | 0.0 |
| 1987 | 1989-04-11 | landsat-5 | 30 m | `LT05_L2SP_144040_19890411_02_T1` | 0.0 |
| 1992 | 1992-10-28 | landsat-5 | 30 m | `LT05_L2SP_144040_19921028_02_T1` | 0.0003 |
| 1997 | 1997-02-28 | landsat-5 | 30 m | `LT05_L2SP_144040_19970228_02_T1` | 0.0 |
| 2002 | 2002-11-01 | landsat-7 | 30 m | `LE07_L2SP_144040_20021101_02_T1` | 0.0004 |
| 2007 | 2008-11-02 | landsat-5 | 30 m | `LT05_L2SP_143040_20081102_02_T1` | 0.0 |
| 2012 | 2013-04-13 | landsat-8 | 30 m | `LC08_L2SP_144040_20130413_02_T1` | 0.0 |
| 2017 | 2017-01-24 | Sentinel-2A | 10 m | `S2A_MSIL2A_20170124T051101_R019_T44RNT_20210207T175513` | 0.0 |
| 2022 | 2022-03-14 | Sentinel-2B | 10 m | `S2B_MSIL2A_20220314T050649_R019_T44RNT_20220314T143917` | 0.0 |
| 2026 | 2026-04-22 | Sentinel-2B | 10 m | `S2B_MSIL2A_20260422T050649_R019_T44RNT_20260422T085212` | 0.0 |

Epochs without a row had no usable dry-season scene in the archive window.

## Observed transformation

**Derived (GHSL R2023A built-up surface, ha, 100 m grid):**

- Whole window: 1975: 5.2 | 1980: 5.4 | 1985: 5.5 | 1990: 5.7 | 1995: 5.8 | 2000: 6.0 | 2005: 8.0 | 2010: 10.9 | 2015: 16.1 | 2020: 22.6
- Inside the HAND <= 10 m zone: 1975: 0.0 | 1980: 0.0 | 1985: 0.0 | 1990: 0.0 | 1995: 0.0 | 2000: 0.0 | 2005: 0.0 | 2010: 0.0 | 2015: 0.1 | 2020: 0.1

**Visual observations from the image series:** researcher input. Record each in
`case_studies/.../metadata/observation_log.csv` style: image ID, feature, observed change, confidence.

## Hazard context (water-level scenarios)

![Scenarios](../../outputs/figures/karnali_79/water_level_scenarios/KAR-SET-061_khandachakra_water_level_scenarios.png)

| Scenario | Buildings in zone | Share of window buildings | Zone area in window (ha) |
|---|---|---|---|
| HAND <= 2 m | 5 | 0.2% | 35.9 |
| HAND <= 5 m | 5 | 0.2% | 36.8 |
| HAND <= 10 m | 12 | 0.5% | 41.8 |

Province rank by buildings with HAND <= 5 m: **70 of 79** (1 = most).

## Evidence

- Imagery: Landsat Collection 2 (USGS) and Sentinel-2 L2A (ESA Copernicus) via Microsoft Planetary Computer (scene IDs above; catalogued in `data/metadata/imagery_catalog.csv`).
- DEM: Copernicus GLO-30 (`Copernicus_DSM_COG_10_N29_00_E081_00_DEM`).
- Channels, places, buildings: Overture Maps 2026-09-23.1.
- Built-up history: JRC GHS-BUILT-S R2023A.

## Interpretation

Researcher input. The derived numbers show where buildings sit on low ground relative to mapped
drainage; they do not by themselves establish flood probability, depth, or risk to life.

## Uncertainty

- HAND from a 30 m DEM: vertical error of several metres in steep terrain; narrow gorges and small
  channels are poorly resolved; unmapped streams are missing from the drainage network.
- Scenario zones are static terrain thresholds, not modelled floods: no discharge, return period,
  velocity, debris flow, landslide-dam outburst or bank erosion is represented.
- Building footprints combine OSM and ML-derived datasets of different dates; counts are not people.
- 1970s Landsat MSS (60 m, false colour) cannot resolve individual buildings; sensor, season and
  resolution differ between epochs.

## Follow-up analysis

- [ ] Confirm the settlement point and name with local knowledge.
- [ ] Record visual observations per epoch (river channel shifts, new construction on floodplain/fan).
- [ ] Check flood/debris-flow history for this location (e.g. DesInventar Nepal, BIPAD portal).
- [ ] If prioritised: higher-resolution DEM and a hydraulic model with design discharges.
