# KAR-SET-051: Chharka Bhot

*Generated 2026-10-02 by `analysis/hazard_exposure/compile_karnali_79.py` from the province-wide
screening run. All numbers are **derived** from the open datasets listed below; nothing here is a
field observation or a validated result. Sections marked "researcher input" are intentionally empty.*

## Identification

| Field | Value |
|---|---|
| Settlement ID | KAR-SET-051 |
| Name (display / primary script) | Chharka Bhot / Chharka Bhot |
| Local level | Chharka Tangsong (rural municipality), P-code NP0662406 |
| District | Dolpa |
| Point (WGS 84) | 83.4154, 29.089887 |
| Selection method | `named_locality_max_buildings` (see docs/methodology.md) |
| Source record | Overture locality `c374411f-696b-4f5d-b8dd-332e56aa1c6b`; OSM `n3633999023@6`; class `village` |

The point is the building-density-selected primary settlement of the local level, **not** an
officially designated headquarters. Confirm or correct it (researcher input).

## Geographic context

- Analysis window: 4 x 4 km centred on the point.
- Building footprints in window: 137 (OSM 103, Google 19, Microsoft 15; Overture de-duplicated).

## Nearby rivers / water bodies

- Nearest named mapped watercourse: **Chyanjun Khola**, 114 m from the point.
- Nearest mapped river-class line: 114 m.
- Buildings within 100 m of a mapped river/stream: 87.
- Median HAND of buildings in window: 18.5 m.

## Historical imagery

![Time series](../../outputs/figures/karnali_79/imagery_timeseries/KAR-SET-051_chharka_tangsong_timeseries_1972_2026.png)

| Epoch | Acquired | Platform | Resolution | Scene ID | Chip cloud/shadow/snow fraction |
|---|---|---|---|---|---|
| 1972 | 1972-12-16 | landsat-1 | 60 m | `LM01_L1TP_153039_19721216_02_T2` | 0.1283 |
| 1977 | 1977-01-09 | landsat-2 | 60 m | `LM02_L1TP_153040_19770109_02_T2` | 0.0 |
| 1987 | 1988-10-19 | landsat-5 | 30 m | `LT05_L2SP_142040_19881019_02_T1` | 0.0 |
| 1992 | 1991-10-12 | landsat-5 | 30 m | `LT05_L2SP_142040_19911012_02_T1` | 0.0 |
| 1997 | 1999-12-04 | landsat-7 | 30 m | `LE07_L2SP_143040_19991204_02_T1` | 0.0015 |
| 2002 | 2003-11-30 | landsat-5 | 30 m | `LT05_L2SP_142040_20031130_02_T1` | 0.0085 |
| 2007 | 2008-12-13 | landsat-5 | 30 m | `LT05_L2SP_142040_20081213_02_T1` | 0.0253 |
| 2012 | 2011-10-19 | landsat-5 | 30 m | `LT05_L2SP_142040_20111019_02_T1` | 0.0079 |
| 2017 | 2017-10-01 | Sentinel-2A | 10 m | `S2A_MSIL2A_20171001T050651_R019_T44RQT_20210202T121720` | 0.0175 |
| 2022 | 2023-10-05 | Sentinel-2B | 10 m | `S2B_MSIL2A_20231005T050649_R019_T44RQT_20231005T101343` | 0.003 |
| 2026 | 2025-10-24 | Sentinel-2B | 10 m | `S2B_MSIL2A_20251024T050809_R019_T44RQT_20251024T071733` | 0.0 |

Epochs without a row had no usable dry-season scene in the archive window.

## Observed transformation

**Derived (GHSL R2023A built-up surface, ha, 100 m grid):**

- Whole window: 1975: 0.2 | 1980: 0.2 | 1985: 0.2 | 1990: 0.2 | 1995: 0.2 | 2000: 0.2 | 2005: 0.2 | 2010: 0.2 | 2015: 0.3 | 2020: 0.3
- Inside the HAND <= 10 m zone: 1975: 0.0 | 1980: 0.0 | 1985: 0.0 | 1990: 0.0 | 1995: 0.0 | 2000: 0.0 | 2005: 0.0 | 2010: 0.0 | 2015: 0.1 | 2020: 0.1

**Visual observations from the image series:** researcher input. Record each in
`case_studies/.../metadata/observation_log.csv` style: image ID, feature, observed change, confidence.

## Hazard context (water-level scenarios)

![Scenarios](../../outputs/figures/karnali_79/water_level_scenarios/KAR-SET-051_chharka_tangsong_water_level_scenarios.png)

| Scenario | Buildings in zone | Share of window buildings | Zone area in window (ha) |
|---|---|---|---|
| HAND <= 2 m | 15 | 10.9% | 63.7 |
| HAND <= 5 m | 27 | 19.7% | 84.9 |
| HAND <= 10 m | 38 | 27.7% | 122.0 |

Province rank by buildings with HAND <= 5 m: **34 of 79** (1 = most).

## Evidence

- Imagery: Landsat Collection 2 (USGS) and Sentinel-2 L2A (ESA Copernicus) via Microsoft Planetary Computer (scene IDs above; catalogued in `data/metadata/imagery_catalog.csv`).
- DEM: Copernicus GLO-30 (`Copernicus_DSM_COG_10_N29_00_E083_00_DEM`).
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
