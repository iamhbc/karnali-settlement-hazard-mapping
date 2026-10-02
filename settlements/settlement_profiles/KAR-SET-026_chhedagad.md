# KAR-SET-026: area near Rajikot

*Generated 2026-10-02 by `analysis/hazard_exposure/compile_karnali_79.py` from the province-wide
screening run. All numbers are **derived** from the open datasets listed below; nothing here is a
field observation or a validated result. Sections marked "researcher input" are intentionally empty.*

## Identification

| Field | Value |
|---|---|
| Settlement ID | KAR-SET-026 |
| Name (display / primary script) | area near Rajikot / Rajikot |
| Local level | Chhedagad (urban municipality), P-code NP0660301 |
| District | Jajarkot |
| Point (WGS 84) | 82.048368, 28.755486 |
| Selection method | `densest_building_cluster_nearest_name` (see docs/methodology.md) |
| Source record | Overture locality `f4070af6-7c08-49f0-b749-02fec0f59755`; OSM `n11331427824@1`; class `hamlet` |

The point is the building-density-selected primary settlement of the local level, **not** an
officially designated headquarters. Confirm or correct it (researcher input).

## Geographic context

- Analysis window: 4 x 4 km centred on the point.
- Building footprints in window: 1,617 (OSM 1,175, Google 334, Microsoft 108; Overture de-duplicated).

## Nearby rivers / water bodies

- Nearest named mapped watercourse: none named in OSM within the 6 x 6 km context window.
- Nearest mapped river-class line: 929 m.
- Buildings within 100 m of a mapped river/stream: 246.
- Median HAND of buildings in window: 340.2 m.

## Historical imagery

![Time series](../../outputs/figures/karnali_79/imagery_timeseries/KAR-SET-026_chhedagad_timeseries_1972_2026.png)

| Epoch | Acquired | Platform | Resolution | Scene ID | Chip cloud/shadow/snow fraction |
|---|---|---|---|---|---|
| 1972 | 1972-12-17 | landsat-1 | 60 m | `LM01_L1TP_154040_19721217_02_T2` | 0.0 |
| 1977 | 1977-03-23 | landsat-2 | 60 m | `LM02_L1TP_154040_19770323_02_T2` | 0.0 |
| 1987 | 1987-12-27 | landsat-5 | 30 m | `LT05_L2SP_143040_19871227_02_T1` | 0.0 |
| 1992 | 1992-11-06 | landsat-5 | 30 m | `LT05_L2SP_143040_19921106_02_T1` | 0.0 |
| 1997 | 1997-03-09 | landsat-5 | 30 m | `LT05_L2SP_143040_19970309_02_T1` | 0.0 |
| 2002 | 2002-10-25 | landsat-7 | 30 m | `LE07_L2SP_143040_20021025_02_T1` | 0.0 |
| 2007 | 2008-04-24 | landsat-5 | 30 m | `LT05_L2SP_143040_20080424_02_T1` | 0.0 |
| 2012 | 2013-10-31 | landsat-8 | 30 m | `LC08_L2SP_143040_20131031_02_T1` | 0.0 |
| 2017 | 2017-04-24 | Sentinel-2A | 10 m | `S2A_MSIL2A_20170424T050651_R019_T44RNS_20210209T101115` | 0.0 |
| 2022 | 2022-11-19 | Sentinel-2B | 10 m | `S2B_MSIL2A_20221119T051109_R019_T44RPS_20221119T163418` | 0.0 |
| 2026 | 2026-03-03 | Sentinel-2B | 10 m | `S2B_MSIL2A_20260303T050649_R019_T44RNS_20260303T091046` | 0.0 |

Epochs without a row had no usable dry-season scene in the archive window.

## Observed transformation

**Derived (GHSL R2023A built-up surface, ha, 100 m grid):**

- Whole window: 1975: 7.2 | 1980: 7.4 | 1985: 7.8 | 1990: 8.2 | 1995: 8.5 | 2000: 8.9 | 2005: 9.3 | 2010: 10.0 | 2015: 10.8 | 2020: 11.8
- Inside the HAND <= 10 m zone: 1975: 0.1 | 1980: 0.1 | 1985: 0.1 | 1990: 0.1 | 1995: 0.1 | 2000: 0.1 | 2005: 0.1 | 2010: 0.3 | 2015: 0.3 | 2020: 0.4

**Visual observations from the image series:** researcher input. Record each in
`case_studies/.../metadata/observation_log.csv` style: image ID, feature, observed change, confidence.

## Hazard context (water-level scenarios)

![Scenarios](../../outputs/figures/karnali_79/water_level_scenarios/KAR-SET-026_chhedagad_water_level_scenarios.png)

| Scenario | Buildings in zone | Share of window buildings | Zone area in window (ha) |
|---|---|---|---|
| HAND <= 2 m | 9 | 0.6% | 47.0 |
| HAND <= 5 m | 18 | 1.1% | 54.3 |
| HAND <= 10 m | 56 | 3.5% | 74.0 |

Province rank by buildings with HAND <= 5 m: **45 of 79** (1 = most).

## Evidence

- Imagery: Landsat Collection 2 (USGS) and Sentinel-2 L2A (ESA Copernicus) via Microsoft Planetary Computer (scene IDs above; catalogued in `data/metadata/imagery_catalog.csv`).
- DEM: Copernicus GLO-30 (`Copernicus_DSM_COG_10_N28_00_E082_00_DEM`).
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
