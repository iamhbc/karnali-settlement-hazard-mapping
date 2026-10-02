# KAR-SET-017: area near Tallo Tanti

*Generated 2026-10-02 by `analysis/hazard_exposure/compile_karnali_79.py` from the province-wide
screening run. All numbers are **derived** from the open datasets listed below; nothing here is a
field observation or a validated result. Sections marked "researcher input" are intentionally empty.*

## Identification

| Field | Value |
|---|---|
| Settlement ID | KAR-SET-017 |
| Name (display / primary script) | area near Tallo Tanti / Tallo Tanti |
| Local level | Panchapuri (urban municipality), P-code NP0659301 |
| District | Surkhet |
| Point (WGS 84) | 81.387311, 28.793093 |
| Selection method | `densest_building_cluster_nearest_name` (see docs/methodology.md) |
| Source record | Overture locality `f09fe0a3-e86c-44ad-b0aa-d82afa5db271`; OSM `n11981065845@1`; class `hamlet` |

The point is the building-density-selected primary settlement of the local level, **not** an
officially designated headquarters. Confirm or correct it (researcher input).

## Geographic context

- Analysis window: 4 x 4 km centred on the point.
- Building footprints in window: 3,441 (OSM 2,793, Google 522, Microsoft 126; Overture de-duplicated).

## Nearby rivers / water bodies

- Nearest named mapped watercourse: **Bheri River**, 4,068 m from the point.
- Nearest mapped river-class line: 4,030 m.
- Buildings within 100 m of a mapped river/stream: 204.
- Median HAND of buildings in window: 59.8 m.

## Historical imagery

![Time series](../../outputs/figures/karnali_79/imagery_timeseries/KAR-SET-017_panchapuri_timeseries_1972_2026.png)

| Epoch | Acquired | Platform | Resolution | Scene ID | Chip cloud/shadow/snow fraction |
|---|---|---|---|---|---|
| 1972 | 1972-11-11 | landsat-1 | 60 m | `LM01_L1GS_154040_19721111_02_T2` | 0.0 |
| 1977 | 1977-03-24 | landsat-2 | 60 m | `LM02_L1TP_155040_19770324_02_T2` | 0.0 |
| 1987 | 1989-04-11 | landsat-5 | 30 m | `LT05_L2SP_144040_19890411_02_T1` | 0.0 |
| 1992 | 1992-10-28 | landsat-5 | 30 m | `LT05_L2SP_144040_19921028_02_T1` | 0.0 |
| 1997 | 1997-02-28 | landsat-5 | 30 m | `LT05_L2SP_144040_19970228_02_T1` | 0.0 |
| 2002 | 2002-11-01 | landsat-7 | 30 m | `LE07_L2SP_144040_20021101_02_T1` | 0.0 |
| 2007 | 2009-04-18 | landsat-5 | 30 m | `LT05_L2SP_144040_20090418_02_T1` | 0.0 |
| 2012 | 2013-04-13 | landsat-8 | 30 m | `LC08_L2SP_144040_20130413_02_T1` | 0.0 |
| 2017 | 2017-04-24 | Sentinel-2A | 10 m | `S2A_MSIL2A_20170424T050651_R019_T44RNS_20210209T101115` | 0.0 |
| 2022 | 2022-04-08 | Sentinel-2A | 10 m | `S2A_MSIL2A_20220408T050651_R019_T44RNS_20240524T030604` | 0.0 |
| 2026 | 2026-03-03 | Sentinel-2B | 10 m | `S2B_MSIL2A_20260303T050649_R019_T44RNS_20260303T091046` | 0.0 |

Epochs without a row had no usable dry-season scene in the archive window.

## Observed transformation

**Derived (GHSL R2023A built-up surface, ha, 100 m grid):**

- Whole window: 1975: 11.8 | 1980: 12.6 | 1985: 13.6 | 1990: 14.9 | 1995: 15.1 | 2000: 15.4 | 2005: 16.8 | 2010: 19.0 | 2015: 21.6 | 2020: 24.8
- Inside the HAND <= 10 m zone: 1975: 0.2 | 1980: 0.2 | 1985: 0.3 | 1990: 0.3 | 1995: 0.4 | 2000: 0.4 | 2005: 0.4 | 2010: 0.6 | 2015: 0.7 | 2020: 0.9

**Visual observations from the image series:** researcher input. Record each in
`case_studies/.../metadata/observation_log.csv` style: image ID, feature, observed change, confidence.

## Hazard context (water-level scenarios)

![Scenarios](../../outputs/figures/karnali_79/water_level_scenarios/KAR-SET-017_panchapuri_water_level_scenarios.png)

| Scenario | Buildings in zone | Share of window buildings | Zone area in window (ha) |
|---|---|---|---|
| HAND <= 2 m | 15 | 0.4% | 42.9 |
| HAND <= 5 m | 36 | 1.0% | 63.9 |
| HAND <= 10 m | 102 | 3.0% | 102.6 |

Province rank by buildings with HAND <= 5 m: **31 of 79** (1 = most).

## Evidence

- Imagery: Landsat Collection 2 (USGS) and Sentinel-2 L2A (ESA Copernicus) via Microsoft Planetary Computer (scene IDs above; catalogued in `data/metadata/imagery_catalog.csv`).
- DEM: Copernicus GLO-30 (`Copernicus_DSM_COG_10_N28_00_E081_00_DEM`).
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
