# KAR-SET-074: Simikot

*Generated 2026-10-02 by `analysis/hazard_exposure/compile_karnali_79.py` from the province-wide
screening run. All numbers are **derived** from the open datasets listed below; nothing here is a
field observation or a validated result. Sections marked "researcher input" are intentionally empty.*

## Identification

| Field | Value |
|---|---|
| Settlement ID | KAR-SET-074 |
| Name (display / primary script) | Simikot / सिमिकोट |
| Local level | Simkot (rural municipality), P-code NP0666402 |
| District | Humla |
| Point (WGS 84) | 81.82016, 29.972864 |
| Selection method | `named_locality_max_buildings` (see docs/methodology.md) |
| Source record | Overture locality `23eb1476-05a5-4f70-872e-d9ccecad866c`; OSM `n3385201652@12`; class `town` |

The point is the building-density-selected primary settlement of the local level, **not** an
officially designated headquarters. Confirm or correct it (researcher input).

## Geographic context

- Analysis window: 4 x 4 km centred on the point.
- Building footprints in window: 1,187 (OSM 864, Google 242, Microsoft 81; Overture de-duplicated).

## Nearby rivers / water bodies

- Nearest named mapped watercourse: **कर्णाली**, 1,645 m from the point.
- Nearest mapped river-class line: 668 m.
- Buildings within 100 m of a mapped river/stream: 42.
- Median HAND of buildings in window: 717.7 m.

## Historical imagery

![Time series](../../outputs/figures/karnali_79/imagery_timeseries/KAR-SET-074_simkot_timeseries_1972_2026.png)

| Epoch | Acquired | Platform | Resolution | Scene ID | Chip cloud/shadow/snow fraction |
|---|---|---|---|---|---|
| 1972 | 1972-11-11 | landsat-1 | 60 m | `LM01_L1TP_154039_19721111_02_T2` | 0.012 |
| 1977 | 1977-03-24 | landsat-2 | 60 m | `LM02_L1TP_155039_19770324_02_T2` | 0.0 |
| 1987 | 1989-04-11 | landsat-5 | 30 m | `LT05_L2SP_144039_19890411_02_T1` | 0.2087 |
| 1992 | 1993-10-31 | landsat-5 | 30 m | `LT05_L2SP_144039_19931031_02_T1` | 0.0 |
| 1997 | 1997-01-11 | landsat-5 | 30 m | `LT05_L2SP_144039_19970111_02_T1` | 0.0004 |
| 2002 | 2001-10-13 | landsat-7 | 30 m | `LE07_L2SP_144039_20011013_02_T1` | 0.0 |
| 2007 | 2008-11-02 | landsat-5 | 30 m | `LT05_L2SP_143039_20081102_02_T1` | 0.0 |
| 2012 | 2013-12-09 | landsat-8 | 30 m | `LC08_L2SP_144039_20131209_02_T1` | 0.0 |
| 2017 | 2017-10-01 | Sentinel-2A | 10 m | `S2A_MSIL2A_20171001T050651_R019_T44RNU_20210202T121734` | 0.0016 |
| 2022 | 2023-01-08 | Sentinel-2B | 10 m | `S2B_MSIL2A_20230108T051209_R019_T44RNU_20230108T174623` | 0.0 |
| 2026 | 2026-01-12 | Sentinel-2B | 10 m | `S2B_MSIL2A_20260112T051059_R019_T44RNU_20260112T073848` | 0.0 |

Epochs without a row had no usable dry-season scene in the archive window.

## Observed transformation

**Derived (GHSL R2023A built-up surface, ha, 100 m grid):**

- Whole window: 1975: 2.6 | 1980: 2.8 | 1985: 2.9 | 1990: 3.0 | 1995: 3.1 | 2000: 3.2 | 2005: 4.6 | 2010: 7.1 | 2015: 9.0 | 2020: 10.8
- Inside the HAND <= 10 m zone: 1975: 0.0 | 1980: 0.0 | 1985: 0.0 | 1990: 0.0 | 1995: 0.0 | 2000: 0.0 | 2005: 0.0 | 2010: 0.0 | 2015: 0.0 | 2020: 0.0

**Visual observations from the image series:** researcher input. Record each in
`case_studies/.../metadata/observation_log.csv` style: image ID, feature, observed change, confidence.

## Hazard context (water-level scenarios)

![Scenarios](../../outputs/figures/karnali_79/water_level_scenarios/KAR-SET-074_simkot_water_level_scenarios.png)

| Scenario | Buildings in zone | Share of window buildings | Zone area in window (ha) |
|---|---|---|---|
| HAND <= 2 m | 1 | 0.1% | 37.9 |
| HAND <= 5 m | 4 | 0.3% | 42.2 |
| HAND <= 10 m | 6 | 0.5% | 51.7 |

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
