# Reference data, baselines, and validation plan

## Scope and current evidence

This plan concerns the first-pass province-wide screening documented in
[`methodology.md`](methodology.md). The committed outputs describe one building-density-selected
settlement point in each local level and terrain-relative HAND exposure indicators. They are not
ground truth for settlement boundaries, flood extents, flood probability, or risk.

The repository currently contains:

- Overture/OSM place points used to select settlement points, plus Overture building and water
  features used in the screening. These are analysis inputs, not independent reference labels.
- Satellite scene IDs, acquisition dates, chip cloud/no-data fractions, and display panels in
  `data/metadata/imagery_catalog.csv` and `outputs/figures/karnali_79/`.
- COD-AB administrative units and derived settlement/HAND GeoJSON layers.
- No independently interpreted settlement labels, field-verified settlement boundaries,
  geocoded flood-event observations, observed flood footprints, or independent event inventory in
  the repository. The source registry records screening sources; it does not imply they provide
  validation truth.

Nepal BIPAD and DesInventar are leads for researcher-led source review only. No records have been
downloaded, queried, checked for license or completeness, or matched to the 79 sites. They must not
be cited as validation data until that work is documented. The repository does not establish that
any specific flood event affected any listed settlement.

## Reference-data requirements

Before validation, document at minimum: stable observation ID; source and source record; access or
acquisition date; event date or image date; geometry and CRS; event/settlement definition;
interpretation or collection method; license; positional and temporal uncertainty; inclusion and
exclusion rules; and reviewer/annotator. Keep observed event extents separate from reported event
points and administrative incident records. Record unavailable fields as `unknown`, not inferred
values.

Settlement references should be independently mapped or officially sourced and should include
multiple settlements where possible, rather than only the locality selected by the same building
data. Flood observations need event dates and a defensible event footprint or documented location
uncertainty. A place name or report point alone is not an observed inundation extent.

## Baseline comparisons

The existing HAND thresholds (2, 5, and 10 m) are deterministic terrain-exposure scenarios. They
are an interpretable screening baseline, not a trained model or flood-hazard classifier. Current
counts, shares, and rankings are descriptive derived outputs; no predictive skill or validation
metric has been calculated.

Once independent observations are curated:

1. Freeze event and settlement reference definitions before examining model performance.
2. Compare any proposed model against a no-skill prevalence baseline and the existing HAND
   threshold screen. For spatial binary labels, report confusion-matrix measures, precision, recall,
   specificity, balanced accuracy, and PR-AUC where class prevalence permits. For mapped extents,
   use predeclared overlap and omission/commission measures at the reference data's positional
   resolution.
3. If sample size and evidence support it, compare a simple regularized statistical model before
   considering machine learning. Do not fit a model or report scores without reference observations.
4. State the analysis unit, class balance, thresholds, uncertainty intervals, and limitations of
   any event inventory, including reporting, geolocation, and event-definition uncertainty.

No model, statistical fit, test metric, or validation result is created by this update.

## Spatially independent validation

Split by entire local-level locations, not by buildings, pixels, or nearby points. Freeze final test
locations before feature selection, threshold selection, or hyperparameter tuning. Keep training,
development/validation, and final test locations disjoint; record split IDs and random seed. Use
grouped spatial cross-validation only within the development set. Report the number and spatial
distribution of independent locations and events. If there are too few independent events or
locations, report the work as exploratory rather than claiming generalizable validation.

The current dataset has no independent reference labels, so a valid held-out test set cannot yet be
formed. The 79 screening sites must not be treated as test labels simply because there is one point
per local level.

## Sensitivity and uncertainty

After obtaining independent reference data, document reasonable parameter ranges before testing.
At minimum, assess:

- HAND thresholds already represented (2, 5, and 10 m), while stating DEM vertical error and that
  these are not return-period water levels.
- Channel-source completeness and channel burn/conditioning choices; unmapped channels remain a
  material uncertainty.
- DEM resolution/source and raster alignment. Resampling GLO-30 to 25 m does not create 25 m
  source terrain information.
- Building inclusion/source and positional uncertainty, and alternate settlement point choices.
- Image sensor, acquisition date/season, snow/cloud/no-data, and coarser historical resolution.
- Alternative held-out location groups, without using the final test group to choose a preferred
  model or threshold.

Report whether substantive conclusions and site ordering change across alternatives, including
reversals. Do not describe results as robust until those runs are performed.

## Paper readiness

The current verified contribution is a first-pass exposure-screening dataset and a documented
processing description. It does not yet support claims of flood prediction, hazard validation, or
risk estimates. A manuscript centered on screening methods may be drafted only after the output
audit and QC pass are reproducible and unresolved source/output inconsistencies are resolved.
Predictive-performance or validation claims must await independent references and
spatially-independent testing.
