# KAR-SET-018: Chhinchu

*Generated 2026-10-02 by `analysis/hazard_exposure/compile_karnali_79.py` from the province-wide
screening run. All numbers are **derived** from the open datasets listed below; nothing here is a
field observation or a validated result. Sections marked "researcher input" are intentionally empty.*

## Identification

| Field | Value |
|---|---|
| Settlement ID | KAR-SET-018 |
| Name (display / primary script) | Chhinchu / छिन्चु |
| Local level | Bheriganga (urban municipality), P-code NP0659302 |
| District | Surkhet |
| Point (WGS 84) | 81.718766, 28.459196 |
| Selection method | `named_locality_max_buildings` (see docs/methodology.md) |
| Source record | Overture locality `1163624d-cf6c-4127-b9e4-7b81dd2a1a98`; OSM `n3385326234@4`; class `village` |

The point is the building-density-selected primary settlement of the local level, **not** an
officially designated headquarters. Confirm or correct it (researcher input).

## Geographic context

- Analysis window: 4 x 4 km centred on the point.
- Building footprints in window: 3,341 (OSM 2,649, Google 495, Microsoft 197; Overture de-duplicated).

## Nearby rivers / water bodies

- Nearest named mapped watercourse: **Hattikahal**, 523 m from the point.
- Nearest mapped river-class line: 279 m.
- Buildings within 100 m of a mapped river/stream: 362.
- Median HAND of buildings in window: 19.2 m.

## Historical imagery

![Time series](../../outputs/figures/karnali_79/imagery_timeseries/KAR-SET-018_bheriganga_timeseries_1972_2026.png)

| Epoch | Acquired | Platform | Resolution | Scene ID | Chip cloud/shadow/snow fraction |
|---|---|---|---|---|---|
| 1972 | 1972-12-17 | landsat-1 | 60 m | `LM01_L1TP_154040_19721217_02_T2` | 0.0 |
| 1977 | 1977-03-23 | landsat-2 | 60 m | `LM02_L1TP_154040_19770323_02_T2` | 0.0 |
| 1987 | 1987-12-27 | landsat-5 | 30 m | `LT05_L2SP_143040_19871227_02_T1` | 0.0 |
| 1992 | 1992-10-28 | landsat-5 | 30 m | `LT05_L2SP_144040_19921028_02_T1` | 0.0 |
| 1997 | 1997-02-28 | landsat-5 | 30 m | `LT05_L2SP_144040_19970228_02_T1` | 0.0 |
| 2002 | 2002-11-01 | landsat-7 | 30 m | `LE07_L2SP_144040_20021101_02_T1` | 0.0 |
| 2007 | 2008-11-02 | landsat-5 | 30 m | `LT05_L2SP_143040_20081102_02_T1` | 0.0 |
| 2012 | 2013-04-13 | landsat-8 | 30 m | `LC08_L2SP_144040_20130413_02_T1` | 0.0 |
| 2017 | 2017-04-24 | Sentinel-2A | 10 m | `S2A_MSIL2A_20170424T050651_R019_T44RNS_20210209T101115` | 0.0 |
| 2022 | 2022-04-08 | Sentinel-2A | 10 m | `S2A_MSIL2A_20220408T050651_R019_T44RNS_20240524T030604` | 0.0 |
| 2026 | 2026-03-03 | Sentinel-2B | 10 m | `S2B_MSIL2A_20260303T050649_R019_T44RNS_20260303T091046` | 0.0 |

Epochs without a row had no usable dry-season scene in the archive window.

## Observed transformation

**Derived (GHSL R2023A built-up surface, ha, 100 m grid):**

- Whole window: 1975: 12.9 | 1980: 13.4 | 1985: 14.0 | 1990: 14.9 | 1995: 15.7 | 2000: 17.3 | 2005: 19.4 | 2010: 22.4 | 2015: 25.4 | 2020: 27.6
- Inside the HAND <= 10 m zone: 1975: 2.3 | 1980: 2.4 | 1985: 2.6 | 1990: 2.8 | 1995: 3.0 | 2000: 3.6 | 2005: 4.0 | 2010: 4.9 | 2015: 5.6 | 2020: 6.4

**Visual observations from the image series:** researcher input. Record each in
`case_studies/.../metadata/observation_log.csv` style: image ID, feature, observed change, confidence.

## Hazard context (water-level scenarios)

![Scenarios](../../outputs/figures/karnali_79/water_level_scenarios/KAR-SET-018_bheriganga_water_level_scenarios.png)

| Scenario | Buildings in zone | Share of window buildings | Zone area in window (ha) |
|---|---|---|---|
| HAND <= 2 m | 65 | 1.9% | 108.9 |
| HAND <= 5 m | 306 | 9.2% | 210.1 |
| HAND <= 10 m | 668 | 20.0% | 384.6 |

Province rank by buildings with HAND <= 5 m: **4 of 79** (1 = most).

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
