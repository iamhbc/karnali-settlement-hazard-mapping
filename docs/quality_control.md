# Quality control

Record checks for geometry validity, CRS consistency, temporal comparability, positional accuracy, missing metadata, processing errors, and independent or field validation. Log corrective actions rather than silently replacing source data.

## 79-settlement screening (2026-10-02)

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
