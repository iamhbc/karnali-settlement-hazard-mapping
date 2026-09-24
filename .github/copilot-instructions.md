# GitHub Copilot Instructions for Karnali Settlement & Water-Related Hazard Mapping

## Repository purpose
This repository is a reproducible research workspace for historical settlement transformation and water-related hazard exposure in Karnali Province, Nepal, using remote sensing, GIS, and GeoAI.

## Core operating rules
- Preserve all existing files and folders unless the user explicitly requests a change.
- Do not delete, rename, or overwrite existing research materials without explicit instruction.
- Treat the existing `README.md`, `.gitignore`, and `case_studies/jubrakhola_river_basin/` content as important and preserve them.
- Do not fabricate data, coordinates, dates, imagery, metadata, results, citations, classifications, or population numbers.
- Do not invent hazard conclusions or risk claims from simple proximity alone.
- Use `unknown`, `NA`, or blank values when data are unavailable or not yet verified.
- Prefer documented evidence, reproducible workflows, and traceable provenance over assumptions.
- Keep raw/source data separate from processed data and generated outputs.
- Use relative paths and configuration files instead of hard-coded local paths.

## Research integrity rules
- Distinguish clearly between observation, interpretation, hypothesis, and conclusion.
- Do not treat visible change in imagery as causal proof of hazard or risk.
- If a method or result is uncertain, document the uncertainty and limitations explicitly.
- Preserve source provenance and licensing constraints for imagery, geospatial layers, and datasets.
- Keep metadata files useful and auditable; prefer explicit inventory records over hidden assumptions.
- When adding templates, use placeholders and examples rather than fake values.

## Repository structure expectations
- Maintain a clean research structure with separate directories for:
  - `configs/`
  - `data/` with `raw/`, `processed/`, and `metadata/`
  - `settlements/`
  - `case_studies/`
  - `imagery/`
  - `analysis/`
  - `notebooks/`
  - `src/`
  - `outputs/`
  - `field_notes/`
  - `docs/`
  - `references/`
- For empty directories that must exist in Git, use `.gitkeep` files rather than leaving directories empty.
- Add README files to major research directories when useful, but do not replace existing quality content with generic text.

## Geospatial and data work
- Prefer GIS and remote sensing workflows that are transparent and reproducible.
- Keep CRS, source, date, scale, and processing steps documented when creating or updating files.
- Support historical imagery analysis without assuming comparability across sensors or seasons.
- Do not commit credentials, private keys, restricted data, or large undocumented datasets.
- For case studies, keep inputs, metadata, analysis, outputs, and limitations separate and clearly organized.

## Documentation and metadata standards
- Prefer concise but precise documentation.
- Add short explanatory comments at the top of configuration and metadata files.
- Use CSV templates with appropriate columns and placeholder values.
- For project configuration files, document purpose and default/example values only.
- Preserve the existing project narrative and avoid overwriting useful current content.

## Code and file creation guidance
- When creating new files, prefer minimal, research-appropriate templates.
- Do not generate fake notebooks or fake analysis outputs.
- Do not create results, charts, or statistics that are not based on real project data.
- Keep scripts and notebooks focused on reproducible analysis and not on app deployment or unrelated tooling.
- Avoid unnecessary frameworks, microservices, or CI/CD infrastructure for this repository.

## Task-specific guardrails for Copilot
When assisting in this repository, Copilot should:
- inspect the repo and current files before changing anything
- maintain existing case-study materials and research context
- prefer additive changes over broad rewrites
- add missing directories and templates only when they are clearly needed
- keep the repository simple enough for a single researcher to maintain
- ask for clarification when a request conflicts with existing research integrity requirements or with the user’s stated preservation constraints

## Example repository-safe actions
- Add missing README files for new sections
- Add `.gitkeep` files to empty directories
- Add project YAML/config templates with no invented coordinates
- Add metadata CSV headers for future dataset inventory work
- Update documentation to explain methodology, provenance, and limitations

## Example actions to avoid
- Deleting the existing case-study folders
- Replacing the existing README with a generic template
- Inventing geographic extents, hazard classes, or study-area parameters
- Creating fake imagery metadata or fake settlement counts
- Overwriting source data or derived outputs without explicit direction
