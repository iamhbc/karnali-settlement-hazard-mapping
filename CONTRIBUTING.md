# Contributing

This is a single-researcher workspace. Contributions, suggestions, and issue reports should preserve data provenance, avoid fabricated values, and clearly distinguish observations, interpretations, hypotheses, and conclusions.

Before adding data, document its source, license, date, CRS, processing status, and redistribution constraints. Do not commit credentials, restricted imagery, or large unreviewed datasets.

## Tests

Run the offline unit tests from the repository root with `python -m pytest`. They use small
synthetic arrays; they do not download imagery or other research data. Create the
environment in `environment.yml` first, and install `pytest` if it is not already available.
