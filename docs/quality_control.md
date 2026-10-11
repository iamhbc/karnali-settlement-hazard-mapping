# Quality control

Record checks for geometry validity, CRS consistency, temporal comparability, positional accuracy, missing metadata, processing errors, and independent or field validation. Log corrective actions rather than silently replacing source data.

## 79-settlement screening (2026-10-02)

Run the repository checks from the root with:

```bash
python analysis/hazard_exposure/validate_karnali_79.py
pytest -q
```

The validator checks the screening table, stable IDs, counts/shares, coordinate agreement,
GeoJSON CRS and geometry validity, one local-level record per unit, HAND zone/site/threshold
coverage, settlement inventory consistency, source and imagery metadata, and scene dates against
the configured date/season windows. It does not validate scientific truth or positional accuracy.
Raster-grid checks are optional because raw rasters are held outside Git:

```bash
python analysis/hazard_exposure/validate_karnali_79.py --cache-dir "$KARNALI_CACHE"
```

When that cache is available, all configured GHSL epochs are checked for matching CRS, transform,
dimensions, and bounds. If the cache is not present, the validator reports raster alignment as
skipped, not passed.

Automated checks in code:

- 79 local levels in COD-AB Karnali.
- 25 urban + 54 rural after name matching.
- Exactly one settlement per local level (raises if a local level has no named locality).
- Every displayed image chip records its measured cloud/shadow/snow and no-data fractions.

Manual checks during development:

- Visual review of time series for Birendranagar (KAR-SET-019), Jajarkot/Bheri Malika (KAR-SET-027)
  and Simikot (KAR-SET-074).
- The first scenario method, nearest-channel relative elevation, gave Voronoi-shaped artefacts and
  over-wide zones on the Birendranagar valley floor. It was replaced with HAND (logged in
  docs/research_log.md).
- Snow saturated the high-altitude chips, and Landsat 7 SLC-off stripes were selected for Simikot 2012.
  Fixed by counting snow as obscured, treating out-of-footprint pixels as no-data and avoiding SLC-off.

Not yet done (needs researcher input): review of all 79 settlement points and names, comparison with
known flood/debris-flow events, and independent or field validation of any scenario zone.

No independent settlement labels, flood-event records, or observed event footprints are currently
tracked in the repository. See [`validation_plan.md`](validation_plan.md); do not calculate
predictive metrics from the current exposure outputs alone.
