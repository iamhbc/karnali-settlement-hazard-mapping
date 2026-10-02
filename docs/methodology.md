# Methodology

Document study-area definitions, data selection, preprocessing, spatial and temporal methods, validation, uncertainty, and decision rules. Link each method to a configuration, script, notebook, or published source where applicable.

## Province-wide screening of 79 local-level settlements (first pass, 2026-10-02)

Scripts: `src/data/fetch_karnali_inputs.py` → `analysis/hazard_exposure/run_karnali_79.py` →
`analysis/hazard_exposure/compile_karnali_79.py`. Parameters: `configs/analysis_parameters.yaml`
(`karnali_79_screening`). Every value there is a first-pass screening choice, not a validated parameter.

### 1. Study units

- Karnali Province local levels from COD-AB Nepal `npl_admin3` (79 units, `adm1_name = Karnali`).
- Urban/rural type: 25 urban municipalities taken from Wikipedia *Administration in Karnali Province*,
  which cites the MoFALD local-level register (accessed 2026-10-02). The names were matched to COD-AB
  names, giving 25 urban + 54 rural (asserted in code).

### 2. Primary settlement per local level (derived)

1. Candidates: every named Overture `divisions/locality` point (OSM-derived) inside the local level.
2. Score: building footprints (Overture buildings: OSM + Google Open Buildings + Microsoft ML Buildings,
   de-duplicated by Overture) whose centroid lies within 500 m.
3. Highest score wins (`named_locality_max_buildings`).
4. Fallback (`densest_building_cluster_nearest_name`): if the winner holds < 50% of the buildings around
   the densest building in the local level, the centre of that densest 500 m cluster is used. It is
   labelled with the nearest named locality, or "area near <name>" when that name is > 1 km away.
   This was needed where the only named point is an administrative label (14 of 79).
5. IDs `KAR-SET-001…079` follow COD-AB P-code order.

This is a reproducible proxy for "main settlement", **not** an official headquarters list.

### 3. Satellite time series (observed imagery, derived selection)

- 4 × 4 km window centred on the settlement point, UTM 44N.
- Twelve epochs at 5-year steps from the first Landsat acquisition (1972) to the latest dry season
  (2026): 1972, 1977 and 1982 use Landsat MSS L1 (60 m, false colour); 1987–2012 use Landsat TM/ETM+/OLI
  L2 (30 m); 2017, 2022 and 2026 use Sentinel-2 L2A (10 m), falling back to Landsat. Each epoch has a
  ±2–3-year window (see config).
- Dry-season months October–April only.
- Scene choice: the 8 lowest scene-cloud candidates are checked against the scene QA band *over the
  chip*. Cloud, shadow, cirrus and snow count as obscured, and fill, out-of-footprint and SLC-off gaps
  count as no-data. Chips with ≤ 5% obscured and ≤ 2% no-data qualify. The winner is the
  terrain-corrected scene closest to the target year, then the one with the highest sun elevation. If
  none qualify, the least obscured scene is shown and its fraction is recorded. Landsat 7 after
  2003-05-31 (SLC-off) is used only when no other scene exists.
- Display: Landsat L2 and Sentinel-2 are converted to surface reflectance (including the Sentinel-2
  baseline-04.00 offset) and shown on one fixed scale (0–0.25, gamma 1.3) so dates are comparable.
  MSS DN uses a per-band 2–98% stretch.
- Imagery is streamed and not stored. Every displayed scene is catalogued in
  `data/metadata/imagery_catalog.csv`.

### 4. Water-level scenarios (derived, screening)

- DEM: Copernicus GLO-30, bilinear-resampled to 25 m over the window plus a 1 km context buffer.
- Drainage: Overture `base/water` features of subtype `river` or `stream` (OSM), rasterized (all-touched).
- HAND (Height Above Nearest Drainage; Nobre et al. 2011, *J. Hydrol.* 404:13–29):
  1. Channels are burned 5 m into the DEM.
  2. The DEM is conditioned (fill pits and depressions, resolve flats) and D8 flow directions are
     computed (pysheds 0.5).
  3. HAND is the DEM elevation minus the elevation of the channel cell the flow path reaches.
  4. Cells draining out of the context window before reaching a channel have no HAND value.
- Scenario zones: HAND ≤ 2, 5 and 10 m.
- Exposure metrics: building centroids inside each zone (count and share of window buildings), buildings
  within 100 m of a mapped channel, and median building HAND.
- Built-up history: JRC GHS-BUILT-S R2023A (1975–2020, 5-year epochs, 3″ ≈ 90 m). It is converted to
  built-up m² per 25 m cell and summed over the window and inside the HAND ≤ 10 m zone.
- Ranking: settlements are ranked by the number of buildings with HAND ≤ 5 m. The rank is a relative
  exposure indicator for prioritisation, not a risk class.

### What this method is not

Following the repository's hazard framework:

- **Hazard:** not modelled. There is no discharge, return period, depth, velocity, debris flow, GLOF or
  bank erosion.
- **Exposure:** screened, as buildings on low ground relative to mapped drainage.
- **Vulnerability:** not assessed (construction type, occupancy, warning, evacuation).
- **Risk to life:** **not estimated.** The outputs identify where a risk assessment would be most
  worthwhile.
