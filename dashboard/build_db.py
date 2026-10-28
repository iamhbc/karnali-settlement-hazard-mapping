"""Build the dashboard's SQLite database from the repository's research outputs.

The database is a derived, read-only index of files already in the repository; it adds no
new research information. Rebuild it whenever those outputs change:

    python dashboard/build_db.py

Sources
  outputs/tables/karnali_79_exposure_screening.csv      settlements, scenarios, GHSL series
  outputs/tables/karnali_79_epoch_indicators.csv        per-epoch frames and spectral indicators
  data/metadata/imagery_catalog.csv                     scene provenance and chip quality
  data/processed/karnali_79/*.geojson                   points, local levels, HAND zones
  settlements/settlement_inventory.csv                  confidence
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "dashboard/data/karnali_dashboard.sqlite"
LEVELS = [2, 5, 10]
GHSL_YEARS = [1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020]

SCHEMA = """
CREATE TABLE settlements (
  settlement_id TEXT PRIMARY KEY, name TEXT, name_primary TEXT, local_level TEXT, pcode TEXT,
  local_level_type TEXT, district TEXT, lon REAL, lat REAL, selection_method TEXT, confidence TEXT,
  buildings_in_window INTEGER, buildings_osm INTEGER, buildings_google INTEGER, buildings_microsoft INTEGER,
  nearest_named_water TEXT, nearest_named_water_m REAL, nearest_river_line_m REAL,
  buildings_within_100m_of_channel INTEGER, median_building_hand_m REAL,
  buildings_le_2m INTEGER, buildings_le_5m INTEGER, buildings_le_10m INTEGER,
  share_le_2m REAL, share_le_5m REAL, share_le_10m REAL, exposure_rank INTEGER,
  first_scene_date TEXT, latest_scene_date TEXT, epochs_with_imagery INTEGER,
  profile_path TEXT, timeseries_figure TEXT, scenario_figure TEXT
);
CREATE TABLE images (
  imagery_id TEXT PRIMARY KEY, settlement_id TEXT REFERENCES settlements, epoch INTEGER,
  acquired TEXT, platform TEXT, collection TEXT, scene_id TEXT, resolution_m INTEGER,
  frame_path TEXT, valid_fraction REAL, ndvi_mean REAL, veg_fraction REAL, water_fraction REAL,
  brightness_mean REAL, comparable INTEGER, quality_notes TEXT, licence TEXT
);
CREATE TABLE ghsl (
  settlement_id TEXT REFERENCES settlements, year INTEGER, built_ha_window REAL, built_ha_zone10 REAL,
  PRIMARY KEY (settlement_id, year)
);
CREATE TABLE scenarios (
  settlement_id TEXT REFERENCES settlements, level_m INTEGER, buildings INTEGER, share REAL,
  zone_area_ha REAL, geojson TEXT, PRIMARY KEY (settlement_id, level_m)
);
CREATE TABLE local_levels (pcode TEXT PRIMARY KEY, name TEXT, district TEXT, local_level_type TEXT,
  geojson TEXT);
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT);
CREATE INDEX images_by_settlement ON images (settlement_id, epoch);
CREATE INDEX settlements_by_district ON settlements (district);
"""


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def main():
    t = pd.read_csv(ROOT / "outputs/tables/karnali_79_exposure_screening.csv")
    ind_path = ROOT / "outputs/tables/karnali_79_epoch_indicators.csv"
    ind = pd.read_csv(ind_path) if ind_path.exists() else pd.DataFrame()
    cat = pd.read_csv(ROOT / "data/metadata/imagery_catalog.csv")
    cat = cat[cat["imagery_id"].astype(str).str.startswith("KAR-SET-")].set_index("imagery_id")
    inv = pd.read_csv(ROOT / "settlements/settlement_inventory.csv", comment="#").set_index("settlement_id")
    zones = json.load(open(ROOT / "data/processed/karnali_79/karnali_79_water_level_zones.geojson"))
    pal = json.load(open(ROOT / "data/processed/karnali_79/karnali_79_local_levels.geojson"))

    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)

    for r in t.itertuples():
        fs = f"{r.settlement_id}_{slug(r.local_level)}"
        con.execute("INSERT INTO settlements VALUES (" + ",".join("?" * 33) + ")", (
            r.settlement_id, r.settlement_name, r.name_primary, r.local_level, r.local_level_pcode,
            r.local_level_type, r.district, r.lon, r.lat, r.selection_method,
            inv.loc[r.settlement_id, "confidence"], r.buildings_in_window, r.buildings_osm,
            r.buildings_google, r.buildings_microsoft,
            None if r.nearest_named_water == "unknown" else r.nearest_named_water,
            None if pd.isna(r.nearest_named_water_m) else r.nearest_named_water_m,
            None if pd.isna(r.nearest_river_line_m) else r.nearest_river_line_m,
            r.buildings_within_100m_of_channel, r.median_building_hand_m,
            r.buildings_le_2m, r.buildings_le_5m, r.buildings_le_10m,
            r.share_le_2m, r.share_le_5m, r.share_le_10m, r.exposure_rank_buildings_le_5m,
            r.first_scene_date, r.latest_scene_date, r.epochs_with_imagery,
            f"settlements/settlement_profiles/{fs}.md",
            f"outputs/figures/karnali_79/imagery_timeseries/{fs}_timeseries_1972_2026.png",
            f"outputs/figures/karnali_79/water_level_scenarios/{fs}_water_level_scenarios.png"))
        rd = r._asdict()
        for y in GHSL_YEARS:
            con.execute("INSERT INTO ghsl VALUES (?,?,?,?)", (
                r.settlement_id, y, rd[f"ghsl_built_ha_{y}"], rd[f"ghsl_built_in_10m_zone_ha_{y}"]))
        for h in LEVELS:
            feats = [f for f in zones["features"] if f["properties"]["settlement_id"] == r.settlement_id
                     and f["properties"]["water_level_m"] == h]
            con.execute("INSERT INTO scenarios VALUES (?,?,?,?,?,?)", (
                r.settlement_id, h, rd[f"buildings_le_{h}m"], rd[f"share_le_{h}m"],
                rd[f"zone_area_le_{h}m_ha"],
                json.dumps({"type": "FeatureCollection", "features": feats})))

    for r in ind.itertuples():
        c = cat.loc[r.imagery_id]
        con.execute("INSERT INTO images VALUES (" + ",".join("?" * 17) + ")", (
            r.imagery_id, r.settlement_id, int(r.epoch), r.acquired, r.platform, r.collection,
            r.scene_id, int(r.resolution_m), r.frame_path, r.valid_fraction,
            None if pd.isna(r.ndvi_mean) else r.ndvi_mean,
            None if pd.isna(r.veg_fraction) else r.veg_fraction,
            None if pd.isna(r.water_fraction) else r.water_fraction,
            None if pd.isna(r.brightness_mean) else r.brightness_mean,
            int(bool(r.comparable)), c["cloud_or_quality_notes"], c["license"]))

    for f in pal["features"]:
        p = f["properties"]
        con.execute("INSERT INTO local_levels VALUES (?,?,?,?,?)", (
            p["adm3_pcode"], p["adm3_name"], p["adm2_name"], p["local_level_type"],
            json.dumps(f["geometry"])))

    meta = {
        "built": dt.datetime.now().isoformat(timespec="seconds"),
        "screening_run": "2026-10-02",
        "framing": "Exposure screening, not a flood model or a risk-to-life estimate.",
        "sources": "COD-AB Nepal (CC BY-IGO); Overture Maps 2026-09-23.1 (ODbL, CC BY 4.0); "
                   "Copernicus GLO-30; Landsat C2 (USGS, public domain); Sentinel-2 L2A "
                   "(Copernicus); GHS-BUILT-S R2023A (CC BY 4.0)",
        "method": "docs/methodology.md",
        "limitations": "docs/limitations.md",
    }
    con.executemany("INSERT INTO metadata VALUES (?,?)", meta.items())
    con.commit()
    n = {k: con.execute(f"SELECT COUNT(*) FROM {k}").fetchone()[0]
         for k in ["settlements", "images", "ghsl", "scenarios", "local_levels"]}
    con.execute("VACUUM")
    con.close()
    print(f"built {DB.relative_to(ROOT)}: {n}")


if __name__ == "__main__":
    main()
