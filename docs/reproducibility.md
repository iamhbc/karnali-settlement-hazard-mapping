# Reproducibility

Record the environment, configuration files, code or notebook versions, input identifiers, processing parameters, outputs, and known limitations for each analysis. Prefer relative paths and documented transformations.

## Local environment

Use the Conda-forge environment in `environment.yml` (Python 3.12):

```bash
conda env create -f environment.yml
conda activate karnali-settlement-hazard-mapping
make check
```

The optional `KARNALI_CACHE` variable controls the local cache for downloaded inputs and resumable intermediate results. `.env.example` is a non-secret template; copy it to the ignored `.env`, set the cache path outside the repository, and source it in the shell before running the Make targets. The scripts default to `/tmp/karnali_cache` when the variable is unset. `make fetch-inputs` requires network access. `make screen` and `make compile-screen` write analysis products into repository output/data locations; review the affected paths and preserve research outputs as appropriate before rerunning.

`make check` compiles Python files under `src/` and `analysis/` and parses the environment, configuration, and workflow YAML files. It is a syntax/configuration check, not a scientific validation or a test suite.

## 79-settlement screening (2026-10-02)

Environment: conda-forge, Python 3.12. The run used geopandas 1.x, rasterio (GDAL 3.13), pystac-client,
planetary-computer, python-duckdb, pyarrow, pysheds 0.5 (with a numpy 2 `in1d` shim in
`src/hazard/flood_scenarios.py`), scipy and matplotlib. See `environment.yml`.

```bash
mamba env create -f environment.yml -n karnali && mamba activate karnali
export KARNALI_CACHE=/path/outside/repo/karnali_cache          # ~170 MB; disposable
python src/data/fetch_karnali_inputs.py                        # admin, overture, ghsl
PYTHONPATH=src python analysis/hazard_exposure/run_karnali_79.py   # resumable; optional KAR-SET-xxx args
python analysis/hazard_exposure/compile_karnali_79.py
```

- Imagery is streamed from Microsoft Planetary Computer (anonymous SAS tokens) and is not stored.
  Re-running chooses the same scenes unless the archive or the config changes.
- Overture is pinned to release `2026-09-23.1`. OSM-derived content changes between releases.
- Per-settlement intermediate results are written to `$KARNALI_CACHE/site_results/`, so the run
  resumes where it stopped.
