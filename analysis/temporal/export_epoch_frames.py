"""Export one image frame + spectral indicators per settlement-epoch for the dashboard.

Inputs : data/metadata/imagery_catalog.csv (KAR-SET-* rows; exact scene IDs)
         data/processed/karnali_79/karnali_79_settlements.geojson
Outputs: outputs/figures/karnali_79/epoch_frames/KAR-SET-xxx/<epoch>.jpg   (400 x 400 px)
         outputs/tables/karnali_79_epoch_indicators.csv

Run:  PYTHONPATH=src python analysis/temporal/export_epoch_frames.py   (resumable)
"""
from __future__ import annotations

import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from remote_sensing.epoch_frames import frame_and_indicators  # noqa: E402
from remote_sensing.imagery_timeseries import open_catalog  # noqa: E402

CFG = yaml.safe_load(open(ROOT / "configs/analysis_parameters.yaml"))["karnali_79_screening"]
CRS = CFG["metric_crs"]
FRAMES = ROOT / "outputs/figures/karnali_79/epoch_frames"
TABLE = ROOT / "outputs/tables/karnali_79_epoch_indicators.csv"


def main(workers: int = 8):
    cat = pd.read_csv(ROOT / "data/metadata/imagery_catalog.csv")
    cat = cat[cat["imagery_id"].astype(str).str.startswith("KAR-SET-")].copy()
    cat["settlement_id"] = cat["imagery_id"].str[:11]
    cat["epoch"] = cat["imagery_id"].str[12:]
    cat["collection"] = cat["sensor_or_product"].str.split("Planetary Computer ").str[1]
    pts = gpd.read_file(ROOT / "data/processed/karnali_79/karnali_79_settlements.geojson").to_crs(CRS)
    xy = {r.settlement_id: (r.geometry.x, r.geometry.y) for r in pts.itertuples()}
    half = CFG["analysis_window_m"] / 2

    done = pd.read_csv(TABLE) if TABLE.exists() else pd.DataFrame(columns=["imagery_id"])
    todo = cat[~cat["imagery_id"].isin(done["imagery_id"])]
    print(f"{len(todo)} frames to export", flush=True)
    catalog = open_catalog()

    def run(r):
        x, y = xy[r.settlement_id]
        out = FRAMES / r.settlement_id / f"{r.epoch}.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        ind = frame_and_indicators(catalog, r.collection, r.source_name,
                                   (x - half, y - half, x + half, y + half), CRS, out)
        return dict(imagery_id=r.imagery_id, settlement_id=r.settlement_id, epoch=r.epoch,
                    scene_id=r.source_name, collection=r.collection,
                    platform=r.sensor_or_product.split(" / ")[0],
                    frame_path=str(out.relative_to(ROOT)), **ind)

    rows = []
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(run, r): r.imagery_id for r in todo.itertuples()}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                rows.append(f.result())
            except Exception:
                print("FAILED", futs[f], traceback.format_exc().splitlines()[-1], flush=True)
            if i % 50 == 0 or i == len(futs):
                out = pd.concat([done, pd.DataFrame(rows)], ignore_index=True)
                out.sort_values("imagery_id").to_csv(TABLE, index=False)
                print(f"{i}/{len(futs)}", flush=True)


if __name__ == "__main__":
    main()
