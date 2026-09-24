# Karnali Settlement & Water-Related Hazard Mapping

Reproducible research workspace for investigating historical settlement transformation, river and water-body proximity, and potential water-related hazard exposure across Karnali Province, Nepal, using remote sensing, GIS, satellite imagery, historical imagery, open geospatial data, and selected GeoAI/machine-learning methods.

> **Status: Research in progress**

---

## Overview

This repository supports an individual research project examining how human settlements in Karnali Province have developed and transformed in relation to rivers, streams, floodplains, drainage systems, and other water bodies.

The research combines historical and contemporary geospatial information to investigate:

- Settlement expansion and contraction
- Settlement densification
- Building and infrastructure development
- Settlement development near river corridors
- Changes in river and channel environments
- Agricultural-land conversion
- Road-oriented settlement development
- Riverbank and floodplain context
- Potential exposure to water-related hazards
- Historical landscape transformation
- Remote-sensing and GeoAI-based approaches to settlement mapping and change detection

The project is designed as a **long-term scientific research workspace**, with emphasis on data provenance, reproducibility, transparent methodology, uncertainty, and scientific integrity.

---

## Research Framework

The project distinguishes between:

**Hazard → Exposure → Vulnerability → Risk**

These concepts are not treated as interchangeable.

For example, proximity to a river may provide information about geographic context or potential exposure, but river proximity alone is **not considered equivalent to disaster risk**.

The research also distinguishes between:

**Observed change → Interpretation → Hypothesis → Conclusion**

Observations derived from imagery or geospatial data should not automatically be interpreted as causal conclusions.

---

## Research Questions

The repository is designed to support investigation of the following questions:

### RQ1 — Settlement and Water Systems

What are the major human settlements in Karnali Province located near rivers, streams, or significant water bodies?

### RQ2 — Historical Transformation

How have these settlements changed spatially and temporally over multiple decades?

### RQ3 — Settlement–River Relationship

How has the spatial relationship between settlements and nearby rivers or water bodies changed over time?

### RQ4 — Hazard Characteristics

Which settlements show development within areas that may have relevant water-related hazard characteristics?

### RQ5 — Built Environment

How have settlement footprints, building density, roads, and other infrastructure changed over time?

### RQ6 — Remote Sensing

Can remote sensing and geospatial analysis identify systematic patterns of settlement transformation?

### RQ7 — GeoAI

Can machine-learning or deep-learning approaches improve settlement mapping, change detection, land-cover classification, or hazard/exposure analysis?

### RQ8 — Uncertainty

What uncertainties and limitations are associated with historical satellite and imagery-based interpretation?

Not every research question will necessarily be applied to every settlement or case study. The methodology is intended to evolve as evidence and data become available.

---

## Study Region

### Primary Study Region

**Karnali Province, Nepal**

The repository is designed to support province-wide analysis while allowing individual river basins and settlements to be investigated as detailed case studies.

Relevant geographic levels may include:

- Karnali Province
- Districts
- Local governments / municipalities
- Wards
- River basins
- Settlements
- River and drainage networks

Administrative information should be supported by documented geospatial sources rather than hard-coded assumptions.

---

## Research Approach

The project integrates several complementary approaches:

### Remote Sensing

Potential applications include:

- Built-up area extraction
- Settlement mapping
- Land-cover classification
- Vegetation indices
- Water indices
- Historical change detection
- Building and settlement segmentation
- Flood extent mapping
- River-channel analysis

### GIS and Spatial Analysis

Potential analyses include:

- Settlement–river proximity
- Settlement expansion
- Building density
- River-buffer analysis
- Floodplain context
- River-channel change
- Infrastructure development
- Spatial relationships between settlements and environmental features

### Historical Imagery

Historical and contemporary imagery may be compared to document observable landscape changes over time.

Potential observations include:

- Settlement footprint
- Building density
- Roads
- River channels
- Riverbanks
- Agricultural land
- Vegetation
- Water bodies
- Infrastructure

Differences caused by image resolution, seasonality, sensor characteristics, viewing angle, georeferencing, cloud/shadow, or image quality must be considered before interpreting apparent changes.

### GeoAI / Machine Learning

Machine-learning methods may be investigated for:

- Building detection
- Settlement segmentation
- Land-cover classification
- Change detection
- Flood extent detection
- Geospatial feature extraction

Machine learning will be used only where it addresses a meaningful research question.

---

## Hazard and Exposure Framework

The project separates physical hazard processes from the elements potentially exposed to those processes.

### Potential Hazards

- Flood
- Flash flood
- River overflow
- Riverbank erosion
- Debris flow
- Landslide-related water processes
- Drainage concentration

### Potentially Exposed Elements

- Buildings
- Settlements
- Population
- Roads
- Bridges
- Schools
- Health facilities
- Other infrastructure

### Vulnerability

Vulnerability analysis will only be included where appropriate and sufficiently documented data are available.

### Risk

Risk will not be inferred from simple river proximity.

A risk assessment requires an explicit methodological framework combining appropriate hazard, exposure, and vulnerability information.

---

## Repository Structure

```text
karnali-settlement-hazard-mapping/
│
├── README.md
├── CITATION.cff
├── LICENSE
├── CONTRIBUTING.md
├── .gitignore
├── environment.yml
├── requirements.txt
│
├── configs/
│   ├── project.yaml
│   ├── study_area.yaml
│   └── analysis_parameters.yaml
│
├── data/
│   ├── README.md
│   ├── raw/
│   ├── processed/
│   └── metadata/
│
├── settlements/
│   ├── README.md
│   ├── settlement_inventory.csv
│   ├── settlement_profiles/
│   └── settlement_boundaries/
│
├── case_studies/
│   ├── README.md
│   └── jubrakhola_river_basin/
│
├── analysis/
│   ├── exploratory/
│   ├── spatial/
│   ├── temporal/
│   ├── change_detection/
│   ├── hazard_exposure/
│   └── machine_learning/
│
├── notebooks/
│   ├── 01_data_inventory.ipynb
│   ├── 02_settlement_inventory.ipynb
│   ├── 03_river_proximity_analysis.ipynb
│   ├── 04_historical_settlement_change.ipynb
│   ├── 05_remote_sensing_analysis.ipynb
│   ├── 06_hazard_exposure_analysis.ipynb
│   └── 07_change_detection_models.ipynb
│
├── src/
│   ├── data/
│   ├── geospatial/
│   ├── remote_sensing/
│   ├── change_detection/
│   ├── hazard/
│   ├── machine_learning/
│   └── visualization/
│
├── outputs/
│   ├── figures/
│   ├── maps/
│   ├── tables/
│   ├── statistics/
│   └── model_outputs/
│
├── field_notes/
│   ├── observations/
│   └── validation/
│
├── docs/
│   ├── research_questions.md
│   ├── methodology.md
│   ├── data_sources.md
│   ├── terminology.md
│   ├── quality_control.md
│   ├── reproducibility.md
│   ├── limitations.md
│   └── research_log.md
│
└── references/
    ├── papers/
    ├── reports/
    └── bibliography.bib
