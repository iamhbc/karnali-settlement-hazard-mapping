# GitHub Copilot Instructions
## Karnali Settlement & Water-Related Hazard Mapping

You are working on a long-term academic geospatial and remote-sensing research repository.

Repository:

`iamhbc/karnali-settlement-hazard-mapping`

The repository concerns historical settlement transformation, river/water-body relationships, and potential water-related hazard/exposure across Karnali Province, Nepal.

---

# 1. GENERAL PRINCIPLE

Treat this repository as a scientific research record, not as a generic software project.

Prioritize:

1. Scientific integrity
2. Data provenance
3. Reproducibility
4. Clear organization
5. Metadata
6. Transparent methodology
7. Explicit uncertainty
8. Long-term maintainability

Do not optimize for unnecessary code or complexity.

---

# 2. BEFORE MAKING CHANGES

Before modifying the repository:

1. Inspect the existing structure.
2. Identify existing related files.
3. Preserve existing research material.
4. Determine whether the requested file/folder already exists.
5. Modify only what is necessary.
6. Do not rename files merely for cosmetic reasons.
7. Do not move existing research material unless there is a clear documented reason.
8. Do not delete existing material unless explicitly instructed.

If there is uncertainty, preserve the existing material and report the issue.

---

# 3. NEVER FABRICATE RESEARCH INFORMATION

Never invent:

- Coordinates
- Dates
- Satellite scenes
- Imagery sources
- Population values
- Administrative boundaries
- Settlement names
- Hazard classifications
- River names
- Dataset metadata
- Model results
- Accuracy metrics
- Citations
- DOI numbers
- Research findings
- Field observations

If information is unavailable, use:

`unknown`

or

`NA`

according to the repository convention.

---

# 4. RESEARCH EVIDENCE

Always distinguish:

### Observed

Something directly visible or measured.

### Derived

Something calculated from documented data and methods.

### Inferred

An interpretation based on available evidence.

### Hypothesized

A proposed explanation requiring further investigation.

### Validated

A result supported by an appropriate validation procedure.

Do not turn an observation into a conclusion automatically.

---

# 5. HAZARD FRAMEWORK

Maintain the distinction:

```text
Hazard
Exposure
Vulnerability
Risk
```

Examples of potential hazards:

- Flood
- Flash flood
- River overflow
- Riverbank erosion
- Debris flow
- Landslide-related water processes
- Drainage concentration

Examples of exposure:

- Buildings
- Settlements
- Population
- Roads
- Bridges
- Schools
- Health facilities
- Other infrastructure

Do not describe simple proximity to a river as "risk."

Do not calculate or claim risk unless an appropriate methodological framework exists.

---

# 6. IMAGE AND REMOTE-SENSING DATA

When new imagery is added:

1. Preserve the original file.
2. Do not overwrite the original.
3. Do not silently delete images.
4. Inspect available filenames and metadata.
5. Record known source information.
6. Record acquisition date/year when known.
7. Record coordinates only when supported.
8. Record uncertainty where metadata is incomplete.
9. Add the image to the appropriate inventory.
10. Use `unknown` when classification cannot be established.

Never invent a sensor, acquisition date, resolution, or location.

---

# 7. HISTORICAL IMAGERY

Historical imagery must be treated carefully.

When comparing images from different years, consider:

* Spatial resolution
* Sensor differences
* Acquisition date
* Season
* Viewing angle
* Cloud/shadow
* Georeferencing
* Image quality
* Mosaicking
* Different geographic coverage

Do not claim that an apparent difference is definitely a real-world change without considering these factors.

---

# 8. GOOGLE EARTH / VISUAL INTERPRETATION

When Google Earth or similar historical imagery is used:

* Clearly identify it as historical imagery or visual interpretation.
* Do not represent it as equivalent to raw scientific satellite data.
* Respect applicable licensing and redistribution restrictions.
* Preserve source information.
* Prefer metadata, screenshots, observations, and derived measurements when raw imagery cannot legally be redistributed.

---

# 9. DATA ORGANIZATION

Maintain the distinction:

```text
data/raw/
```

Original/source data.

```text
data/processed/
```

Processed or derived datasets.

```text
data/metadata/
```

Dataset and processing metadata.

```text
analysis/
```

Analytical workflows.

```text
outputs/
```

Generated research outputs.

```text
docs/
```

Research documentation.

```text
case_studies/
```

Detailed investigations of specific locations.

Do not mix raw data and generated outputs.

---

# 10. JHUPRAKHOLA CASE STUDY

The first detailed case study is:

```text
case_studies/JhupraKhola/
```

Treat this as an important research case study.

Possible contents include:

```text
imagery/
geospatial_data/
settlement_observations/
analysis/
outputs/
metadata/
```

Do not assume the exact JhupraKhola basin boundary unless supported by a documented geospatial source.

Preserve existing JhupraKhola material.

---

# 11. WHEN NEW DATA IS PROVIDED

When I add a new dataset:

1. Inspect it.
2. Determine its type.
3. Preserve the original.
4. Place it in the appropriate directory.
5. Add metadata.
6. Record the source.
7. Record the access date if known.
8. Record the license if known.
9. Record processing steps.
10. Record limitations.
11. Update relevant documentation.
12. Do not modify unrelated research files.

---

# 12. WHEN NEW IMAGES ARE PROVIDED

When I provide a folder of images:

1. Treat it as research source material.
2. Preserve original filenames.
3. Do not randomly rename images.
4. Do not delete ambiguous images.
5. Create unique image IDs if required.
6. Create or update an imagery inventory.
7. Classify images only when supported.
8. Use `unclassified/` if necessary.
9. Record unknown metadata as `unknown`.
10. Keep original and derived versions separate.

---

# 13. WHEN NEW SETTLEMENTS ARE ADDED

Use a unique settlement identifier.

Preferred format:

```text
KAR-SET-001
KAR-SET-002
KAR-SET-003
```

Do not use settlement names alone as identifiers.

If a settlement profile is required, use:

```text
settlements/settlement_profiles/
```

Document:

* Identification
* Geographic context
* Nearby rivers/water bodies
* Historical imagery
* Observed transformation
* Hazard context
* Evidence
* Interpretation
* Uncertainty
* Follow-up analysis

---

# 14. METADATA

Whenever new data are introduced, ask:

```text
Where did this come from?
When was it obtained?
What does it represent?
What is its spatial resolution?
What is its temporal coverage?
What processing was performed?
What license applies?
What are its limitations?
```

If the answer is unknown, record that explicitly.

Never fill missing metadata with guesses.

---

# 15. SOURCE CODE

Reusable processing functions belong in:

```text
src/
```

Organize by purpose:

```text
src/
├── data/
├── geospatial/
├── remote_sensing/
├── change_detection/
├── hazard/
├── machine_learning/
└── visualization/
```

Do not duplicate identical processing logic across notebooks.

If code becomes reusable, move it into `src/`.

---

# 16. NOTEBOOKS

Notebooks should be understandable by another researcher.

Where applicable, include:

1. Purpose
2. Research question
3. Inputs
4. Data sources
5. Method
6. Parameters
7. Analysis
8. Results
9. Limitations
10. Next steps

Do not hide unexplained processing inside notebooks.

---

# 17. CONFIGURATION

Use configuration files for values that may change.

Examples:

```text
configs/project.yaml
configs/study_area.yaml
configs/analysis_parameters.yaml
```

Avoid unnecessary hard-coded:

* Paths
* CRS
* Buffer distances
* Time periods
* Random seeds
* Model parameters
* Study-area settings

Do not invent scientific parameter values simply to populate configuration files.

Use clearly marked defaults or `null`/`unknown` when appropriate.

---

# 18. MACHINE LEARNING

Only introduce machine learning when it addresses a meaningful research question.

For each experiment, document where applicable:

```text
experiment_id
objective
dataset
study_area
input_features
target
model
architecture
training_data
validation_data
test_data
validation_method
metrics
hyperparameters
random_seed
results
limitations
```

Never fabricate:

* Accuracy
* Precision
* Recall
* F1
* IoU
* Training results
* Validation results
* Model performance

---

# 19. OUTPUTS

Generated outputs belong in:

```text
outputs/
```

Use clear filenames.

Examples:

```text
JHUPRA_settlement_expansion_1995_2025.png
JHUPRA_river_proximity_2025.png
JHUPRA_historical_comparison_1995_2025.png
```

Do not treat generated figures as raw research data.

---

# 20. DOCUMENTATION

When a methodological decision is important, document it.

Important documentation includes:

```text
docs/research_questions.md
docs/methodology.md
docs/data_sources.md
docs/terminology.md
docs/quality_control.md
docs/reproducibility.md
docs/limitations.md
docs/research_log.md
```

Keep documentation synchronized with actual methods.

Do not claim that a method was used if it was not actually used.

---

# 21. RESEARCH LOG

When a significant research decision is made, update:

```text
docs/research_log.md
```

Use:

```markdown
## YYYY-MM-DD

### Objective

### Data Added

### Analysis Performed

### Observations

### Problems

### Methodological Decisions

### Changes to Repository

### Next Steps
```

---

# 22. GIT COMMITS

Use meaningful commit messages.

Preferred examples:

```text
init: establish research repository structure
data: add administrative boundary dataset
data: add settlement inventory template
case-study: organize JhupraKhola imagery
metadata: catalog historical imagery
analysis: add river proximity workflow
analysis: add settlement change workflow
docs: update methodology
docs: record research decision
```

Avoid meaningless messages such as:

```text
update
changes
test
new
final
stuff
```

---

# 23. DEPENDENCIES

Do not add packages unnecessarily.

Before adding a dependency:

1. Check whether an existing dependency already provides the required functionality.
2. Add only necessary packages.
3. Keep `requirements.txt` and `environment.yml` consistent.
4. Avoid unnecessary heavyweight frameworks.

---

# 24. FILE NAMING

Use clear, descriptive names.

Prefer:

```text
settlement_inventory.csv
imagery_catalog.csv
observation_log.csv
river_proximity_analysis.py
historical_settlement_change.ipynb
```

Avoid:

```text
final2.py
new.py
test123.py
map_latest_final.png
stuff.csv
```

Do not rename existing files merely to satisfy this rule if doing so could break provenance or references.

---

# 25. RAW DATA SAFETY

Never commit:

* Passwords
* API keys
* Access tokens
* Credentials
* Sensitive personal information
* Restricted imagery
* Unauthorized copyrighted datasets

Use `.gitignore` appropriately.

Do not commit huge datasets unless there is a clear reason.

---

# 26. WHEN ASKED TO RESTRUCTURE

If I ask you to restructure the repository:

1. Inspect first.
2. Show what currently exists.
3. Identify what is missing.
4. Add missing structure.
5. Preserve existing material.
6. Avoid unnecessary movement.
7. Avoid destructive operations.
8. Report what changed.

Do not perform a complete destructive rebuild unless I explicitly request one.

---

# 27. WHEN ASKED TO "CLEAN" THE REPOSITORY

"Clean" means:

* Improve organization
* Remove obvious temporary files only when safe
* Improve naming where explicitly requested
* Improve documentation
* Improve metadata
* Improve reproducibility

It does NOT automatically mean:

* Delete old data
* Delete images
* Delete notebooks
* Delete research notes
* Rename everything
* Rewrite historical records

Ask before destructive cleanup.

---

# 28. WHEN INFORMATION IS MISSING

Do not guess.

Use:

```text
unknown
```

or:

```text
NA
```

or leave the field empty when appropriate.

Clearly identify information that requires researcher input.

---

# 29. EXTERNAL DATA

Do not download external datasets unless explicitly instructed.

If an external dataset is needed:

1. Identify the required dataset.
2. Document the source.
3. Record the expected metadata.
4. Tell me what is needed.
5. Wait for explicit permission if downloading is required.

---

# 30. RESEARCH NEUTRALITY

Do not write conclusions that go beyond the evidence.

For example, do not automatically write:

"Settlement expansion caused increased flood risk."

Instead, use evidence-based language such as:

"Settlement expansion was observed within the mapped river-proximity zone."

Any causal relationship must be supported by an appropriate analysis.

---

# 31. BEFORE EVERY MAJOR CHANGE

Before making a major repository change, check:

* Does this already exist?
* Will this overwrite anything?
* Is the source documented?
* Is the metadata available?
* Is the distinction between raw and processed data maintained?
* Is the change reproducible?
* Is the change necessary?
* Could another researcher understand it later?

---

# 32. FINAL CHECK AFTER CHANGES

After completing a task:

1. Check the repository structure.
2. Check for accidental duplicate files.
3. Check for accidental deletions.
4. Check for broken paths.
5. Check metadata templates.
6. Check documentation.
7. Check `.gitignore`.
8. Check that no fabricated research information was introduced.
9. Summarize all changes.

Always report:

```text
Created:
Modified:
Preserved:
Moved:
Deleted:
Assumptions:
Needs researcher input:
```

---

# CORE PRINCIPLE

The repository is a long-term scientific research record.

Before creating or modifying anything, ask:

> "Would another researcher be able to understand what this file is, where it came from, why it exists, how it was produced, and how it relates to the research?"

If not, improve the organization or metadata before proceeding.

Scientific integrity and reproducibility are more important than adding code.
