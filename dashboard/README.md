# Karnali Settlement Explorer (web dashboard)

A local web portal for browsing, searching and comparing the 79-settlement screening results
over time. It is backed by a SQLite database built from the repository's research outputs.

![Explorer](../outputs/figures/karnali_79/epoch_frames/KAR-SET-019/2026.jpg)

## Run it

```bash
mamba env create -f environment.yml -n karnali   # once
mamba activate karnali
python dashboard/build_db.py                       # only after outputs change
python dashboard/app.py                            # open http://127.0.0.1:8050
```

Set `HOST=0.0.0.0` to reach it from other devices on your network. Set `PORT` to change the port.

### Deploy to Vercel

Import the repo in Vercel with the defaults (Framework Preset: **Other**, Root Directory: repo root,
no build command). `vercel.json` routes `/api/*` to the FastAPI app via `api/index.py`, which installs
only `api/requirements.txt`. `dashboard/static/` and `outputs/` are served from Vercel's CDN.
Commit `dashboard/data/karnali_dashboard.sqlite` after rebuilding it.

## What you can do

| View | Use it to |
|---|---|
| **Explorer › list and map** | Search by settlement, municipality, district or river. Filter by district or urban/rural, and sort by exposure. Click a marker or list item to zoom to its 4×4 km window and low-ground zones. Basemaps: light map, OpenStreetMap, or Esri satellite. |
| **Timeline** | Step through the 1972–2026 images every 5 or 10 years. Clicking an image shows a change summary since the previous image shown. |
| **Compare** | Pick any two epochs, or use the 5-year, 10-year or first→latest presets. View them side by side, as a swipe, or as a difference image, with a change summary. |
| **Trends** | GHSL built-up 1975–2020 (whole window vs low ground), plus vegetation and surface-water share per calibrated image. A table view is included. |
| **Low-ground scenarios** | Building counts at HAND ≤ 2, 5 and 10 m, map toggles for each zone, and the scenario figure. |
| **Profile** | The settlement's profile page (`settlements/settlement_profiles/`). |
| **Province overview** | Province totals, a district chart, province built-up growth, and a sortable table of all 79. Click a row to open that settlement. |

Deep links work: `http://127.0.0.1:8050/#KAR-SET-019` opens Birendranagar.

## How change summaries are computed

`GET /api/compare?settlement_id=…&epoch_a=…&epoch_b=…` (see `app.py`, `change_summary`):

- **Built-up (derived):** GHSL R2023A built-up surface, interpolated linearly to each image date.
  - It is computed for the whole window and for the HAND ≤ 10 m zone.
  - Dates outside 1975–2020 are clamped. If both dates fall outside on the same side, no built-up
    change is reported.
- **Vegetation / water / NDVI (derived):** measured on each image's clear pixels.
  - Vegetation is the share with NDVI > 0.3. Water is the share with MNDWI > 0 (green/SWIR1).
  - These are compared only when both images are calibrated surface reflectance (Landsat TM/ETM+/OLI
    L2 or Sentinel-2 L2A). 1970s MSS is visual only.
- **Cautions:** added automatically for different sensors or resolution, different seasons, and
  images that are less than 95% clear.
- **Difference view:** computed in the browser from the two display images (brightness change per
  pixel). It is a visual aid, not a change map.

Nothing in the dashboard is a flood model or a risk-to-life estimate. See `docs/methodology.md` and
`docs/limitations.md`.

## Architecture

```text
dashboard/
├── build_db.py          repo outputs → data/karnali_dashboard.sqlite (derived, read-only index)
├── data/karnali_dashboard.sqlite
├── app.py               FastAPI: /api/* JSON + static files (outputs/, static/)
└── static/              index.html, app.js, style.css (Leaflet, Chart.js, marked from cdnjs)
```

| Table | Contents |
|---|---|
| `settlements` | 79 rows: identity, location, exposure counts, rank, figure and profile paths |
| `images` | one row per settlement × epoch: scene ID, date, sensor, frame path, clear share, indicators |
| `ghsl` | built-up hectares per settlement × GHSL epoch (window and HAND ≤ 10 m zone) |
| `scenarios` | buildings, share and area per HAND level, with the zone GeoJSON |
| `local_levels` | 79 local-level boundaries (simplified) |
| `metadata` | build time, framing, sources |

API docs: `http://127.0.0.1:8050/api/docs`.

## Updating

1. Re-run the screening (`analysis/hazard_exposure/run_karnali_79.py` and `compile_karnali_79.py`).
2. Export the epoch frames: `PYTHONPATH=src python analysis/temporal/export_epoch_frames.py`.
3. Rebuild the database: `python dashboard/build_db.py`.
