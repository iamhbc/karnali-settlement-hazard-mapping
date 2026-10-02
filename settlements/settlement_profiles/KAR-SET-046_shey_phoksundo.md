# KAR-SET-046: Khoma

*Generated 2026-10-02 by `analysis/hazard_exposure/compile_karnali_79.py` from the province-wide
screening run. All numbers are **derived** from the open datasets listed below; nothing here is a
field observation or a validated result. Sections marked "researcher input" are intentionally empty.*

## Identification

| Field | Value |
|---|---|
| Settlement ID | KAR-SET-046 |
| Name (display / primary script) | Khoma / Khoma |
| Local level | Shey Phoksundo (rural municipality), P-code NP0662401 |
| District | Dolpa |
| Point (WGS 84) | 83.137495, 29.430468 |
| Selection method | `named_locality_max_buildings` (see docs/methodology.md) |
| Source record | Overture locality `e8ddad0d-3d05-4c6c-9bed-6734c90bbc6c`; OSM `n5290153116@1`; class `hamlet` |

The point is the building-density-selected primary settlement of the local level, **not** an
officially designated headquarters. Confirm or correct it (researcher input).

## Geographic context

- Analysis window: 4 x 4 km centred on the point.
- Building footprints in window: 176 (OSM 127, Google 29, Microsoft 20; Overture de-duplicated).

## Nearby rivers / water bodies

- Nearest named mapped watercourse: **Koran Khola**, 1,180 m from the point.
- Nearest mapped river-class line: 1,180 m.
- Buildings within 100 m of a mapped river/stream: 43.
- Median HAND of buildings in window: 227.6 m.

## Historical imagery

![Time series](../../outputs/figures/karnali_79/imagery_timeseries/KAR-SET-046_shey_phoksundo_timeseries_1972_2026.png)

| Epoch | Acquired | Platform | Resolution | Scene ID | Chip cloud/shadow/snow fraction |
|---|---|---|---|---|---|
| 1972 | 1972-12-17 | landsat-1 | 60 m | `LM01_L1GS_154039_19721217_02_T2` | 0.2903 |
| 1977 | 1976-10-12 | landsat-2 | 60 m | `LM02_L1TP_154040_19761012_02_T2` | 0.0 |
| 1987 | 1988-10-26 | landsat-5 | 30 m | `LT05_L2SP_143040_19881026_02_T1` | 0.0 |
| 1992 | 1993-11-09 | landsat-5 | 30 m | `LT05_L2SP_143040_19931109_02_T1` | 0.0 |
| 1997 | 1999-12-28 | landsat-5 | 30 m | `LT05_L2SP_143040_19991228_02_T1` | 0.0166 |
| 2002 | 2002-12-28 | landsat-7 | 30 m | `LE07_L2SP_143040_20021228_02_T1` | 0.0264 |
| 2007 | 2008-04-24 | landsat-5 | 30 m | `LT05_L2SP_143040_20080424_02_T1` | 0.0 |
| 2012 | 2013-12-02 | landsat-8 | 30 m | `LC08_L2SP_143039_20131202_02_T1` | 0.023 |
| 2017 | 2017-10-01 | Sentinel-2A | 10 m | `S2A_MSIL2A_20171001T050651_R019_T44RQT_20210202T121720` | 0.0 |
| 2022 | 2024-10-29 | Sentinel-2B | 10 m | `S2B_MSIL2A_20241029T050839_R019_T44RQT_20241029T073249` | 0.0 |
| 2026 | 2025-10-14 | Sentinel-2B | 10 m | `S2B_MSIL2A_20251014T050659_R019_T44RPT_20251014T082528` | 0.0 |

Epochs without a row had no usable dry-season scene in the archive window.

## Observed transformation

**Derived (GHSL R2023A built-up surface, ha, 100 m grid):**

- Whole window: 1975: 0.0 | 1980: 0.0 | 1985: 0.0 | 1990: 0.0 | 1995: 0.0 | 2000: 0.0 | 2005: 0.0 | 2010: 0.0 | 2015: 0.0 | 2020: 0.0
- Inside the HAND <= 10 m zone: 1975: 0.0 | 1980: 0.0 | 1985: 0.0 | 1990: 0.0 | 1995: 0.0 | 2000: 0.0 | 2005: 0.0 | 2010: 0.0 | 2015: 0.0 | 2020: 0.0

**Visual observations from the image series:** researcher input. Record each in
`case_studies/.../metadata/observation_log.csv` style: image ID, feature, observed change, confidence.

## Hazard context (water-level scenarios)

![Scenarios](../../outputs/figures/karnali_79/water_level_scenarios/KAR-SET-046_shey_phoksundo_water_level_scenarios.png)

| Scenario | Buildings in zone | Share of window buildings | Zone area in window (ha) |
|---|---|---|---|
| HAND <= 2 m | 3 | 1.7% | 32.6 |
| HAND <= 5 m | 3 | 1.7% | 42.6 |
| HAND <= 10 m | 8 | 4.5% | 67.7 |

Province rank by buildings with HAND <= 5 m: **75 of 79** (1 = most).

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
