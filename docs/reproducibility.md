# Reproducibility

Record the environment, configuration files, code or notebook versions, input identifiers, processing parameters, outputs, and known limitations for each analysis. Prefer relative paths and documented transformations.

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
