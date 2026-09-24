# Jhupra River Basin case study

## Purpose

This case study documents settlement growth and transformation, river proximity, and potential water-related hazard exposure in and around the Jubrakhola River Basin (also referred to as the Jubrakhola area) near Birendranagar, Karnali Province, Nepal. It is maintained as a traceable research record: source materials are preserved, observations are separated from interpretation, and derived products are linked to their inputs and processing notes.

The folder name uses the project-standard ASCII spelling `jubrakhola_river_basin`. Source files may retain their original names; important original names are recorded in the inventories.

## Geographic context

The study area is the Jubrakhola/Jubrakhola river-basin area near Birendranagar. Exact study-area boundaries, coordinates, drainage definitions, and coordinate reference systems remain to be confirmed from authoritative geospatial sources and are recorded as `unknown` until verified. The basin is studied in relation to nearby channels, tributaries, settlements, roads, agricultural land, and other water bodies that may influence exposure or accessibility.

## Why this area was selected

- It provides a focused local case for examining settlement change alongside a river system.
- Its proximity to Birendranagar supports investigation of settlement expansion, road growth, and land-cover conversion.
- A time series of historical and recent imagery can support visual comparison of river channels, riverbanks, built-up areas, and agricultural-to-built-up transitions.
- The case can provide a documented, reproducible unit for comparison with other Karnali settlement and hazard contexts.

These are study motivations, not findings. No hazard or settlement conclusion should be inferred until supported by documented evidence and analysis.

## Research questions

1. How has settlement extent and building density changed across the represented historical periods?
2. Where have settlements expanded toward or away from the Jubrakhola and connected channels?
3. How have river channels, banks, crossings, roads, and adjacent agricultural areas visibly changed?
4. Which settlements and infrastructure appear potentially exposed to water-related processes, and what evidence supports that assessment?
5. How sensitive are these observations to image date, resolution, season, cloud cover, georeferencing, and study-area definition?

## Available imagery and time periods

Imagery is organized by purpose under `imagery/`:

- `historical/` — historical photographs, scans, or historical imagery exports.
- `recent/` — recent reference imagery and photographs.
- `satellite/` — satellite scenes, exports, and scene subsets.
- `google_earth/` — Google Earth imagery or screenshots, subject to source licensing and terms.

The represented years, acquisition dates, sensors, resolutions, extents, and processing states are not assumed. They must be entered in `metadata/imagery_inventory.csv`. Use `unknown` or `NA` rather than fabricating values.

For comparable multi-year material, retain consistent extent, orientation, scale, and coordinate reference where feasible. Record departures from those targets in the inventory and observation log.

## Planned analyses

- Temporal visual comparison of settlement footprint, density, roads, agriculture, and river channels.
- River-proximity measurements using documented river-network and settlement layers.
- Settlement-expansion mapping with explicit dates, thresholds, and processing parameters.
- Hazard-exposure context mapping for proximity to channels, flood-prone locations, crossings, banks, and other water-related features.
- Quality and uncertainty review based on source provenance, image resolution, cloud/seasonal conditions, georeferencing, and analyst confidence.

Analyses belong under `analysis/`; reproducible scripts or notebooks should be stored in the repository's project-level workflow area when added. Derived figures, maps, and tables belong under `outputs/` and must reference their inputs and processing method.

## Data sources and provenance

Potential sources include satellite providers, historical imagery archives, Google Earth, government or institutional geospatial datasets, OpenStreetMap, field observations, and project-derived layers. The actual source, license or access terms, acquisition date, provider, original filename, and processing history must be recorded in the inventories. Do not commit credentials or restricted source data.

Raw/source materials must not be overwritten. Processed copies and derived products should use a new filename and document the transformation. When a file cannot be redistributed, keep a metadata record and a stable source/access description instead of copying the restricted file.

## Observation protocol

`metadata/observation_log.csv` records what is visibly observed in an image or map. It deliberately does not encode an automatic conclusion. Each observation should identify the image, feature, date/year, evidence source, confidence, and any analyst notes. Interpretive claims and model outputs should be documented separately in analysis notes and outputs.

## Known limitations

- Exact basin and study-area boundaries have not yet been verified in this repository.
- Historical imagery may differ in season, viewing geometry, spatial resolution, georeferencing quality, and coverage.
- Google Earth and other imagery may have usage, attribution, and redistribution restrictions.
- Visual evidence alone cannot establish flood probability, causation, structural safety, or future hazard.
- Settlement boundaries and river proximity depend on the definitions, positional accuracy, and date of the underlying layers.
- Missing metadata is recorded explicitly; unknown values should not be silently inferred.

## Current research status

**Status:** case-study structure and metadata templates created; source ingestion, boundary verification, imagery inventory, observations, and analyses pending.

Update this section as the research develops. Every substantive update should preserve provenance and identify the relevant source, method, date, and limitations.

## Directory guide

| Directory | Contents |
| --- | --- |
| `imagery/` | Raw and processed visual imagery, organized by source/use. |
| `maps/` | Basin, settlement, river, and hazard-context maps. |
| `settlement_observations/` | Identified settlements and documented historical change observations. |
| `geospatial_data/` | River, basin, settlement, road, and other spatial layers. |
| `analysis/` | Reproducible analysis inputs, notes, scripts, and intermediate products. |
| `outputs/` | Publication-oriented figures, maps, and tables. |
| `metadata/` | Inventories and observation log. |
