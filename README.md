# Karnali Settlement & Water-Related Hazard Mapping

> A reproducible research framework for investigating settlement transformation, settlement–river relationships, landscape change, and potential water-related hazard exposure across Karnali Province, Nepal, using remote sensing, GIS, historical imagery, open geospatial datasets, and selected GeoAI and machine-learning methods.

## Project Overview

This repository is a research workspace for the systematic investigation of settlement distribution and transformation, settlement–river relationships, historical landscape change, built-environment expansion, and potential water-related hazard exposure in Karnali Province, Nepal. The project integrates remote sensing, geospatial analysis, historical imagery interpretation, and selected machine-learning approaches to support transparent, evidence-based inquiry.

The repository is designed as a long-term scientific research environment rather than a generic software project. It emphasizes reproducible methods, provenance, metadata, uncertainty documentation, and methodological transparency. Research questions, datasets, and analytical workflows are expected to evolve as additional evidence is acquired and validated.

## Research Purpose

The project investigates how settlements in Karnali Province have developed and transformed in relation to river systems, streams, and other water-related landscape features, and how geospatial evidence can be used to characterize potential exposure to water-related hazards.

The research distinguishes clearly between:

- Observed evidence
- Derived measurements
- Interpretation
- Hypothesis
- Validation
- Conclusion

These categories are not interchangeable. Visual interpretation alone does not establish causal explanation or risk without appropriate supporting evidence and structured methods.

## Study Region

### Primary Study Region

The primary geographic scope is Karnali Province, Nepal. The province provides the broader regional context for examining settlement patterns, river proximity, land use and cover change, and potential water-related hazard exposure.

The repository is organized to support province-wide investigation while enabling detailed analyses through selected case studies. Geographic boundaries, source datasets, and study-area definitions are documented as they are identified and verified.

## JhupraKhola Case Study

The first detailed case study focuses on the JhupraKhola area / river system in Karnali Province, Nepal. The canonical case-study directory is:

```text
case_studies/JhupraKhola/
```

The JhupraKhola case study is intended to investigate, where supported by available evidence:

- settlement transformation
- river–settlement relationships
- historical landscape change
- settlement expansion
- proximity to river channels and water-related landforms
- built-environment characteristics
- potential hazard exposure
- historical imagery and satellite observations
- geospatial layers and processing outputs
- uncertainty and evidence quality

No analysis is described as complete unless the repository contains clear supporting evidence for that status.

## Research Questions

### RQ1 — Settlement and Water Systems

How are settlements spatially distributed in relation to rivers, streams, water bodies, and other relevant landscape features?

### RQ2 — Historical Settlement Transformation

How have settlements changed spatially through time, based on available historical and contemporary evidence?

### RQ3 — Settlement–River Relationships

What spatial relationships exist between settlement expansion and river channels or flood-prone / water-related landscape settings?

### RQ4 — Hazard Characteristics

What water-related hazards may affect settlement areas, and what evidence supports their characterization?

### RQ5 — Built Environment

How has the built environment expanded or transformed within areas potentially exposed to water-related hazards?

### RQ6 — Remote Sensing

How can satellite imagery, historical imagery, and other remote-sensing observations support detection and interpretation of settlement and landscape change?

### RQ7 — GeoAI and Machine Learning

Where appropriate, how can machine-learning or GeoAI methods support settlement extraction, change detection, classification, or hazard-related spatial analysis?

### RQ8 — Uncertainty

What are the major sources of uncertainty associated with imagery, spatial data, historical interpretation, classification, hazard characterization, and derived results?

## Conceptual Framework

The project uses a structured conceptual framework for hazard-related analysis:

```text
Hazard
   ↓
Exposure
   ↓
Vulnerability
   ↓
Risk
```

These concepts are distinct and are not treated as interchangeable. In particular:

- Hazard refers to a potentially damaging physical process or condition.
- Exposure refers to people, settlements, buildings, infrastructure, or other elements located within potentially affected areas.
- Vulnerability refers to characteristics that influence susceptibility to harm.
- Risk refers to the potential for adverse consequences considering hazard, exposure, and vulnerability.

The repository also distinguishes the evidence chain:

```text
Observed Change
      ↓
Interpretation
      ↓
Hypothesis
      ↓
Validation
      ↓
Conclusion
```

Visual interpretation alone is not treated as proof of causal explanation or risk without a documented methodology and supporting evidence.

## Methodological Approach

The research workflow is organized at a high level as follows:

1. Define research questions and study areas.
2. Identify and document relevant datasets.
3. Establish data provenance and metadata.
4. Acquire or organize historical and contemporary imagery.
5. Prepare and validate geospatial datasets.
6. Map settlements and relevant physical features.
7. Conduct temporal and change analysis.
8. Examine settlement–river and settlement–hazard relationships.
9. Apply statistical, spatial, remote-sensing, or machine-learning methods where justified.
10. Validate derived results where possible.
11. Quantify or document uncertainty.
12. Produce maps, figures, tables, and reproducible outputs.
13. Record assumptions, limitations, and methodological decisions.

The precise implemented methods should be determined from the repository contents and associated metadata.

## Data and Evidence

### Raw Data

Original downloaded, acquired, or collected datasets.

### Processed Data

Datasets generated through documented processing workflows.

### Derived Data

Measurements, classifications, spatial indicators, or other products derived from source data.

### Metadata

Information describing source, date, spatial reference, processing, provenance, licensing, and limitations.

### Analysis Outputs

Figures, maps, tables, statistics, and model outputs generated from documented workflows.

Data provenance is a core research requirement. The project prioritizes transparent methods and traceable evidence rather than assumptions or undocumented processing.

## Imagery and Historical Evidence

Historical imagery may be used to investigate landscape and settlement change. When imagery is incorporated, the relevant source, acquisition or observation date, spatial extent, resolution, reference system, processing, interpretation method, licensing/access conditions, and uncertainty should be documented where available.

Historical imagery interpretation must distinguish direct observation from inference. Differences in sensor characteristics, viewing geometry, acquisition date, seasonality, cloud cover, georeferencing, and coverage must be considered before interpreting apparent change as a real-world transformation.

If Google Earth imagery or screenshots are used, they should be identified and used according to applicable terms and permissions. This repository does not assume that third-party imagery can be redistributed without restrictions.

## Settlement Inventory

Settlements may be represented using structured identifiers and metadata. Where a settlement inventory is implemented, stable identifiers are used so that records remain traceable.

Example identifier format:

```text
KAR-SET-001
KAR-SET-002
KAR-SET-003
```

Potential inventory fields may include:

- settlement_id
- settlement_name
- administrative_area
- latitude
- longitude
- source
- observation_date
- imagery_source
- settlement_type
- evidence_status
- notes
- uncertainty

Actual fields implemented in the repository should be determined from the inventory files and metadata.

## Reproducibility

The project is designed around reproducible research principles. Where applicable, the workflow should document:

- software environment
- dependencies
- processing scripts
- configuration files
- notebooks
- input datasets
- processing steps
- parameters
- output locations
- metadata
- version information
- random seeds for machine-learning experiments
- model configuration
- validation procedures

Outputs should be traceable back to their source data and processing workflow whenever technically possible.

## Scientific Integrity

The repository operates under a strict scientific integrity standard:

- No fabricated data
- No fabricated citations
- No fabricated coordinates
- No fabricated imagery dates
- No unsupported hazard classifications
- No unsupported causal claims
- No unreported processing steps
- No undocumented model results
- No presentation of hypotheses as established findings
- No presentation of visual interpretation as quantitative measurement unless supported by a defined method

When information is genuinely unavailable, the project uses `unknown`, `NA`, or blank values rather than inventing values.

## Uncertainty and Limitations

Uncertainty is an explicit component of the research design. It may arise from:

- imagery resolution
- historical imagery availability
- temporal inconsistencies
- georeferencing
- cloud cover
- classification errors
- incomplete datasets
- positional uncertainty
- settlement-definition ambiguity
- river-channel variability
- hazard-model assumptions
- limited field validation
- machine-learning model uncertainty

Limitations are documented as the work develops and should be treated as part of the scientific record rather than as an afterthought.

## Repository Structure

The repository currently includes the following major areas, where present or planned:

```text
configs/          Research and analysis configuration
data/             Raw, processed, and metadata datasets
settlements/      Settlement inventory and related products
case_studies/     Detailed geographic case studies
imagery/          Project-level imagery organization
analysis/         Analytical workflows
notebooks/        Exploratory and reproducible notebooks
src/              Reusable research code
outputs/          Generated figures, maps, tables, and statistics
field_notes/      Field observations and validation records
docs/             Research documentation
references/       Papers, reports, and bibliography
```

The actual directory structure should be read from the repository contents and not assumed to be complete or fixed.

## Case Study Structure

The canonical case-study directory is:

```text
case_studies/
└── JhupraKhola/
    ├── imagery/
    ├── geospatial_data/
    ├── settlement_observations/
    ├── analysis/
    ├── outputs/
    └── metadata/
```

This structure separates source evidence, geospatial datasets, observations, analyses, outputs, and metadata. The actual repository contents should be read directly when implementing or updating project documentation.

## Research Status

> Status: Research in progress

The repository is under active development. Datasets, methods, analyses, validation, and documentation may evolve as new evidence becomes available. The project is not described as completed unless a clear supporting record exists in the repository.

## Quality Control

Research outputs should undergo appropriate checks including:

- spatial-reference verification
- geometry validation
- duplicate detection
- temporal consistency checks
- metadata completeness
- source verification
- reproducibility checks
- visual quality control
- validation against independent evidence where available

These checks should be performed and documented as appropriate to the data and analysis method.

## Research Workflow

The project is organized around a disciplined workflow:

```text
Research Question
       ↓
Data Acquisition
       ↓
Metadata & Provenance
       ↓
Processing
       ↓
Analysis
       ↓
Validation
       ↓
Uncertainty Assessment
       ↓
Output
       ↓
Documentation
```

Significant methodological decisions should be documented rather than hidden inside notebooks or manual analyses.

## Citation

Citation information is maintained in `CITATION.cff` when available. The repository should not invent author names, affiliations, DOI numbers, or publication metadata that are not documented.

If full citation metadata is not yet available, the project may state that citation details will be added as the project reaches a citable research release.

## License and Data Use

Licensing for repository code, research data, and third-party datasets should be reviewed explicitly. This repository does not assume unrestricted rights to all downloaded or acquired datasets, imagery, or geospatial layers. Licensing constraints should be documented and respected.

## Acknowledgements

Any acknowledgements, institutional, agency, or funding information should reflect only what is actually documented in the repository.

## Writing Style Expectations

The README is written as a serious scientific research repository for a PI-led research program. It is concise but substantive, avoids marketing language, and distinguishes evidence from interpretation. It emphasizes reproducibility, data provenance, uncertainty, and methodological clarity.

## Summary

This repository supports a long-term, transparent, and evidence-based research effort investigating settlement transformation and water-related hazard exposure in Karnali Province, Nepal. The project is organized to support rigorous geospatial and remote-sensing analysis while preserving a clear distinction between observation, interpretation, and conclusion.
