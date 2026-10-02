"""SQLite store for near-real-time monitoring data (dashboard "Live").

Separate from the static research database so live updates never touch committed outputs.
"""
from __future__ import annotations

import datetime as dt
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS weather_hourly (
  settlement_id TEXT, time TEXT, precip_mm REAL, kind TEXT,      -- kind: past | forecast
  fetched_at TEXT, PRIMARY KEY (settlement_id, time));
CREATE TABLE IF NOT EXISTS discharge_daily (
  settlement_id TEXT, date TEXT, discharge REAL, discharge_median REAL, discharge_max REAL,
  kind TEXT, cell_lat REAL, cell_lon REAL, fetched_at TEXT, PRIMARY KEY (settlement_id, date));
CREATE TABLE IF NOT EXISTS scenes (
  scene_id TEXT, settlement_id TEXT, collection TEXT, acquired TEXT, orbit TEXT,
  clear_fraction REAL, zone_water_ha REAL, zone_area_ha REAL, veg_fraction REAL,
  frame_path TEXT, processed_at TEXT, note TEXT, PRIMARY KEY (scene_id, settlement_id));
CREATE TABLE IF NOT EXISTS incidents (
  incident_id INTEGER PRIMARY KEY, hazard_id INTEGER, hazard TEXT, title TEXT, incident_on TEXT,
  lon REAL, lat REAL, pcode TEXT, local_level TEXT, nearest_settlement_id TEXT, distance_km REAL,
  deaths INTEGER, missing INTEGER, injured INTEGER, families_affected INTEGER,
  houses_destroyed INTEGER, houses_affected INTEGER, verified INTEGER, fetched_at TEXT);
CREATE TABLE IF NOT EXISTS runs (
  job TEXT, started TEXT, finished TEXT, status TEXT, message TEXT);
CREATE INDEX IF NOT EXISTS scenes_by_settlement ON scenes (settlement_id, acquired);
CREATE INDEX IF NOT EXISTS incidents_by_date ON incidents (incident_on);
"""


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=30)
    con.execute("PRAGMA journal_mode=WAL")   # readers (the web app) never block the updater
    con.executescript(SCHEMA)
    con.row_factory = sqlite3.Row
    return con


def log_run(con, job: str, started: str, status: str, message: str = ""):
    con.execute("INSERT INTO runs VALUES (?,?,?,?,?)", (job, started, now(), status, message[:2000]))
    con.commit()
