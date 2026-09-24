# Metadata and provenance

The CSV files in this directory are the authoritative inventories for this case study.

## Conventions

- Use stable IDs: `JUB_IMG_###` for imagery, `JUB_DS_###` for datasets, and `JUB_OBS_###` for observations.
- Use ISO dates (`YYYY-MM-DD`) where known; use a four-digit year when only the year is known.
- Use `unknown` when information has not been determined and `NA` when a field does not apply.
- Preserve original filenames in `original_filename`; `relative_path` records the repository path.
- Record checksums for files when practical, especially before and after processing.
- Do not replace an original record when processing a file; add or update a derived record and describe the transformation.
- Keep visible observations separate from interpretation. Confidence describes the reliability of the recorded observation, not the probability of a hazard.

The starter rows are placeholders and must be replaced or extended during source ingestion.
