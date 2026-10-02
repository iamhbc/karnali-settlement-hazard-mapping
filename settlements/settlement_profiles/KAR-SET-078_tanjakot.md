# KAR-SET-078: Kolibada

*Generated 2026-10-02 by `analysis/hazard_exposure/compile_karnali_79.py` from the province-wide
screening run. All numbers are **derived** from the open datasets listed below; nothing here is a
field observation or a validated result. Sections marked "researcher input" are intentionally empty.*

## Identification

| Field | Value |
|---|---|
| Settlement ID | KAR-SET-078 |
| Name (display / primary script) | Kolibada / Kolibada |
| Local level | Tanjakot (rural municipality), P-code NP0666406 |
| District | Humla |
| Point (WGS 84) | 81.752051, 29.637849 |
| Selection method | `named_locality_max_buildings` (see docs/methodology.md) |
| Source record | Overture locality `df444228-c87c-4116-b95a-bbaf1a4c0385`; OSM `n10725172945@1`; class `hamlet` |

The point is the building-density-selected primary settlement of the local level, **not** an
officially designated headquarters. Confirm or correct it (researcher input).

## Geographic context

- Analysis window: 4 x 4 km centred on the point.
- Building footprints in window: 873 (OSM 575, Google 195, Microsoft 103; Overture de-duplicated).

## Nearby rivers / water bodies

- Nearest named mapped watercourse: **Palma Khola**, 1,679 m from the point.
- Nearest mapped river-class line: 3,269 m.
- Buildings within 100 m of a mapped river/stream: 57.
- Median HAND of buildings in window: 318.3 m.

## Historical imagery

![Time series](../../outputs/figures/karnali_79/imagery_timeseries/KAR-SET-078_tanjakot_timeseries_1972_2026.png)

| Epoch | Acquired | Platform | Resolution | Scene ID | Chip cloud/shadow/snow fraction |
|---|---|---|---|---|---|
| 1972 | 1972-11-11 | landsat-1 | 60 m | `LM01_L1TP_154039_19721111_02_T2` | 0.0 |
| 1977 | 1977-03-23 | landsat-2 | 60 m | `LM02_L1TP_154040_19770323_02_T2` | 0.0 |
| 1987 | 1989-12-16 | landsat-5 | 30 m | `LT05_L2SP_143040_19891216_02_T1` | 0.0 |
| 1992 | 1993-10-31 | landsat-5 | 30 m | `LT05_L2SP_144039_19931031_02_T1` | 0.0 |
| 1997 | 1997-02-12 | landsat-5 | 30 m | `LT05_L2SP_144039_19970212_02_T1` | 0.0008 |
| 2002 | 2001-10-13 | landsat-7 | 30 m | `LE07_L2SP_144039_20011013_02_T1` | 0.0 |
| 2007 | 2007-03-05 | landsat-5 | 30 m | `LT05_L2SP_143040_20070305_02_T1` | 0.0341 |
| 2012 | 2010-11-15 | landsat-5 | 30 m | `LT05_L2SP_144039_20101115_02_T1` | 0.0 |
| 2017 | 2017-01-24 | Sentinel-2A | 10 m | `S2A_MSIL2A_20170124T051101_R019_T44RNT_20210207T175513` | 0.0 |
| 2022 | 2022-03-14 | Sentinel-2B | 10 m | `S2B_MSIL2A_20220314T050649_R019_T44RNT_20220314T143917` | 0.0 |
| 2026 | 2026-04-22 | Sentinel-2B | 10 m | `S2B_MSIL2A_20260422T050649_R019_T44RNT_20260422T085212` | 0.0 |

Epochs without a row had no usable dry-season scene in the archive window.

## Observed transformation

**Derived (GHSL R2023A built-up surface, ha, 100 m grid):**

- Whole window: 1975: 1.1 | 1980: 1.2 | 1985: 1.3 | 1990: 1.4 | 1995: 1.4 | 2000: 1.6 | 2005: 2.1 | 2010: 2.8 | 2015: 3.9 | 2020: 5.2
- Inside the HAND <= 10 m zone: 1975: 0.0 | 1980: 0.0 | 1985: 0.0 | 1990: 0.0 | 1995: 0.0 | 2000: 0.0 | 2005: 0.0 | 2010: 0.0 | 2015: 0.1 | 2020: 0.1

**Visual observations from the image series:** researcher input. Record each in
`case_studies/.../metadata/observation_log.csv` style: image ID, feature, observed change, confidence.

## Hazard context (water-level scenarios)

![Scenarios](../../outputs/figures/karnali_79/water_level_scenarios/KAR-SET-078_tanjakot_water_level_scenarios.png)

| Scenario | Buildings in zone | Share of window buildings | Zone area in window (ha) |
|---|---|---|---|
| HAND <= 2 m | 4 | 0.5% | 20.9 |
| HAND <= 5 m | 4 | 0.5% | 25.0 |
| HAND <= 10 m | 8 | 0.9% | 31.9 |

Province rank by buildings with HAND <= 5 m: **71 of 79** (1 = most).

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
