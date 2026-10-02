"""Near-real-time updater for the dashboard's Live layer.

    python dashboard/live_update.py                 # run every job once
    python dashboard/live_update.py weather incidents
    python dashboard/live_update.py --loop          # keep running on the configured schedule

Jobs: weather (Open-Meteo hourly rain), discharge (GloFAS via Open-Meteo), incidents (BIPAD),
satellite (new Sentinel-2 + Sentinel-1 RTC scenes per settlement). Results go to the git-ignored
dashboard/data/live.sqlite and dashboard/data/live_frames/.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import threading
import time
import traceback
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from monitoring import incidents, satellite, weather  # noqa: E402
from monitoring.store import connect, log_run, now  # noqa: E402

CFG = yaml.safe_load(open(ROOT / "configs/monitoring.yaml"))["monitoring"]
SCREEN = yaml.safe_load(open(ROOT / "configs/analysis_parameters.yaml"))["karnali_79_screening"]
STATIC_DB = ROOT / "dashboard/data/karnali_dashboard.sqlite"
LIVE_DB = ROOT / CFG["database"]
FRAMES = ROOT / CFG["frames_dir"]
JOBS = ["weather", "discharge", "incidents", "satellite"]
_lock = threading.Lock()


def static_inputs():
    with sqlite3.connect(STATIC_DB) as c:
        c.row_factory = sqlite3.Row
        s = [dict(r) for r in c.execute("SELECT settlement_id, name, lat, lon FROM settlements ORDER BY settlement_id")]
        ll = [{"pcode": r["pcode"], "name": r["name"], "geometry": json.loads(r["geojson"])}
              for r in c.execute("SELECT * FROM local_levels")]
    return s, ll


def run_job(job: str) -> str:
    with _lock:   # one job at a time keeps SQLite writes simple
        settlements, levels = static_inputs()
        con = connect(LIVE_DB)
        started = now()
        try:
            if job == "weather":
                n = weather.update_weather(con, settlements, CFG["weather"], CFG["timezone"])
            elif job == "discharge":
                n = weather.update_discharge(con, settlements, CFG["discharge"])
            elif job == "incidents":
                n = incidents.update_incidents(con, settlements, levels, CFG["incidents"])
            elif job == "satellite":
                zones = satellite.zones_from_static_db(STATIC_DB, CFG["satellite"]["analysis_zone_hand_m"])
                n = satellite.update_satellite(con, settlements, zones, CFG["satellite"], SCREEN["metric_crs"],
                                               SCREEN["analysis_window_m"] / 2, FRAMES)
            else:
                raise ValueError(job)
            msg = f"{n} rows"
            log_run(con, job, started, "ok", msg)
        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            log_run(con, job, started, "error", msg + "\n" + traceback.format_exc(limit=3))
        finally:
            con.close()
        return msg


def loop(jobs=JOBS, stop: threading.Event | None = None):
    """Run each job on its own interval (configs/monitoring.yaml: schedule_minutes)."""
    next_due = {j: 0.0 for j in jobs}
    while not (stop and stop.is_set()):
        for j in jobs:
            if time.time() >= next_due[j]:
                print(f"[live] {j}: {run_job(j)}", flush=True)
                next_due[j] = time.time() + CFG["schedule_minutes"][j] * 60
        (stop.wait(30) if stop else time.sleep(30))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    jobs = args or JOBS
    if "--loop" in sys.argv:
        loop(jobs)
    else:
        for j in jobs:
            print(f"{j}: {run_job(j)}", flush=True)
