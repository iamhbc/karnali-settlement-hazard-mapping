"""Karnali Settlement Explorer: web dashboard backend (FastAPI + SQLite).

Serves the read-only research database built by dashboard/build_db.py, the near-real-time
monitoring database filled by dashboard/live_update.py, the repository's figures/frames, and
the single-page frontend in dashboard/static/.

    python dashboard/app.py                    # http://127.0.0.1:8050
    LIVE_UPDATES=1 python dashboard/app.py     # also run the live updater in the background
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sqlite3
import statistics
import threading
import time
import xml.etree.ElementTree as ET
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.request import Request, urlopen

import yaml

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "dashboard/data/karnali_dashboard.sqlite"
STATIC = ROOT / "dashboard/static"
GHSL_FIRST, GHSL_LAST = 1975, 2020
MON = yaml.safe_load(open(ROOT / "configs/monitoring.yaml"))["monitoring"]
LIVE_DB = ROOT / MON["database"]
LIVE_FRAMES = ROOT / MON["frames_dir"]

SORTS = {"rank": "exposure_rank", "name": "name", "district": "district, name",
         "buildings": "buildings_in_window DESC", "le5": "buildings_le_5m DESC",
         "share5": "share_le_5m DESC", "id": "settlement_id"}



@asynccontextmanager
async def lifespan(_app):
    stop = threading.Event()
    if os.environ.get("LIVE_UPDATES") == "1":
        import live_update  # dashboard/live_update.py
        threading.Thread(target=live_update.loop, kwargs={"stop": stop}, daemon=True).start()
    yield
    stop.set()


app = FastAPI(title="Karnali Settlement Explorer", docs_url="/api/docs", lifespan=lifespan)


def db() -> sqlite3.Connection:
    if not DB.exists():
        raise HTTPException(503, "Database missing: run python dashboard/build_db.py")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def rows(sql: str, args=()) -> list[dict]:
    with db() as con:
        return [dict(r) for r in con.execute(sql, args)]


# --- settlements ---------------------------------------------------------------------------

@app.get("/api/meta")
def meta():
    m = {r["key"]: r["value"] for r in rows("SELECT * FROM metadata")}
    m["districts"] = [r["district"] for r in rows("SELECT DISTINCT district FROM settlements ORDER BY 1")]
    m["epochs"] = [r["epoch"] for r in rows("SELECT DISTINCT epoch FROM images ORDER BY 1")]
    return m


@app.get("/api/settlements")
def settlements(q: str = "", district: str = "", type: str = "", sort: str = "rank"):
    where, args = ["1=1"], []
    if q:
        where.append("(name LIKE ? OR name_primary LIKE ? OR local_level LIKE ? OR district LIKE ? "
                     "OR settlement_id LIKE ? OR nearest_named_water LIKE ?)")
        args += [f"%{q}%"] * 6
    if district:
        where.append("district = ?")
        args.append(district)
    if type:
        where.append("local_level_type = ?")
        args.append(type)
    order = SORTS.get(sort, "exposure_rank")
    return rows(f"""SELECT settlement_id, name, name_primary, local_level, local_level_type, district,
                lon, lat, buildings_in_window, buildings_le_2m, buildings_le_5m, buildings_le_10m,
                share_le_5m, exposure_rank, confidence, nearest_named_water, epochs_with_imagery
                FROM settlements WHERE {' AND '.join(where)} ORDER BY {order}""", args)


@app.get("/api/settlements/{sid}")
def settlement(sid: str):
    s = rows("SELECT * FROM settlements WHERE settlement_id = ?", (sid,))
    if not s:
        raise HTTPException(404, f"Unknown settlement {sid}")
    s = s[0]
    s["scenarios"] = rows("SELECT level_m, buildings, share, zone_area_ha FROM scenarios "
                          "WHERE settlement_id = ? ORDER BY level_m", (sid,))
    s["ghsl"] = rows("SELECT year, built_ha_window, built_ha_zone10 FROM ghsl WHERE settlement_id = ? "
                     "ORDER BY year", (sid,))
    return s


@app.get("/api/settlements/{sid}/images")
def images(sid: str):
    return rows("SELECT * FROM images WHERE settlement_id = ? ORDER BY epoch", (sid,))


@app.get("/api/settlements/{sid}/zones")
def zones(sid: str):
    return {r["level_m"]: json.loads(r["geojson"]) for r in
            rows("SELECT level_m, geojson FROM scenarios WHERE settlement_id = ?", (sid,))}


@app.get("/api/settlements/{sid}/profile", response_class=PlainTextResponse)
def profile(sid: str):
    s = rows("SELECT profile_path FROM settlements WHERE settlement_id = ?", (sid,))
    if not s:
        raise HTTPException(404, f"Unknown settlement {sid}")
    return (ROOT / s[0]["profile_path"]).read_text()


@app.get("/api/local_levels")
def local_levels():
    feats = [{"type": "Feature", "geometry": json.loads(r.pop("geojson")), "properties": r}
             for r in rows("SELECT * FROM local_levels")]
    return {"type": "FeatureCollection", "features": feats}


# --- comparison ----------------------------------------------------------------------------

def ghsl_at(series: list[dict], year: float, col: str) -> tuple[float | None, str]:
    """Linear interpolation of GHSL built-up at `year`, clamped to the 1975-2020 epochs."""
    pts = [(r["year"], r[col]) for r in series if r[col] is not None]
    if not pts:
        return None, "no GHSL data"
    y = min(max(year, GHSL_FIRST), GHSL_LAST)
    note = "" if GHSL_FIRST <= year <= GHSL_LAST else f"clamped to GHSL {int(y)}"
    for (y0, v0), (y1, v1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return v0 + (v1 - v0) * (y - y0) / (y1 - y0), note
    return pts[-1][1], note


def pct(a, b):
    return None if a in (None, 0) or b is None else (b - a) / a * 100


def change_summary(s: dict, a: dict, b: dict) -> dict:
    ya = dt.date.fromisoformat(a["acquired"])
    yb = dt.date.fromisoformat(b["acquired"])
    years = (yb - ya).days / 365.25
    fy = lambda d: d.year + (d.timetuple().tm_yday - 1) / 365.25  # noqa: E731
    built_a, na = ghsl_at(s["ghsl"], fy(ya), "built_ha_window")
    built_b, nb = ghsl_at(s["ghsl"], fy(yb), "built_ha_window")
    zone_a, _ = ghsl_at(s["ghsl"], fy(ya), "built_ha_zone10")
    zone_b, _ = ghsl_at(s["ghsl"], fy(yb), "built_ha_zone10")
    ghsl_note = "; ".join(dict.fromkeys(n for n in (na, nb) if n))
    if min(max(fy(ya), GHSL_FIRST), GHSL_LAST) == min(max(fy(yb), GHSL_FIRST), GHSL_LAST):
        # both dates fall outside 1975-2020 on the same side: GHSL says nothing about this interval
        built_a = built_b = zone_a = zone_b = None
        ghsl_note = "GHSL built-up covers 1975-2020 only; no built-up estimate for this interval"
    comparable = bool(a["comparable"] and b["comparable"])

    def delta(k, scale=100):
        if not comparable or a[k] is None or b[k] is None:
            return None
        return round((b[k] - a[k]) * scale, 2)

    metrics = {
        "built_up_ha": {"a": built_a, "b": built_b, "delta": None if built_a is None else built_b - built_a,
                        "pct": pct(built_a, built_b), "source": "GHSL R2023A (derived, ~90 m)",
                        "note": ghsl_note},
        "built_up_in_hand10_zone_ha": {"a": zone_a, "b": zone_b,
                                       "delta": None if zone_a is None else zone_b - zone_a,
                                       "pct": pct(zone_a, zone_b), "source": "GHSL x HAND <= 10 m"},
        "vegetation_cover_pct": {"a": a["veg_fraction"], "b": b["veg_fraction"], "delta_pp": delta("veg_fraction"),
                                 "source": "NDVI > 0.3 share of clear pixels"},
        "surface_water_pct": {"a": a["water_fraction"], "b": b["water_fraction"], "delta_pp": delta("water_fraction"),
                              "source": "MNDWI > 0 share of clear pixels"},
        "mean_ndvi": {"a": a["ndvi_mean"], "b": b["ndvi_mean"], "delta": delta("ndvi_mean", 1)},
        "mean_visible_reflectance": {"a": a["brightness_mean"], "b": b["brightness_mean"],
                                     "delta": delta("brightness_mean", 1)},
    }

    lines = []
    if built_a is not None:
        p = metrics["built_up_ha"]["pct"]
        lines.append(f"Modelled built-up surface in the 4x4 km window went from {built_a:.1f} ha to "
                     f"{built_b:.1f} ha ({'+' if built_b >= built_a else ''}{built_b - built_a:.1f} ha"
                     + (f", {p:+.0f}%" if p is not None else "") + ").")
        if zone_a is not None:
            lines.append(f"Inside the HAND <= 10 m zone (low ground near drainage) it went from {zone_a:.1f} ha "
                         f"to {zone_b:.1f} ha ({zone_b - zone_a:+.1f} ha).")
    if comparable:
        for key, label in (("vegetation_cover_pct", "Vegetation cover"), ("surface_water_pct", "Surface water")):
            m = metrics[key]
            if m["delta_pp"] is not None:
                lines.append(f"{label} changed from {m['a'] * 100:.1f}% to {m['b'] * 100:.1f}% of clear "
                             f"pixels ({m['delta_pp']:+.1f} percentage points).")
    else:
        lines.append("Spectral indicators are not compared: at least one image is 1970s Landsat MSS "
                     "(uncalibrated). Use the images for visual comparison only.")

    cautions = []
    if a["collection"] != b["collection"] or a["resolution_m"] != b["resolution_m"]:
        cautions.append(f"Different sensors/resolution ({a['platform']} {a['resolution_m']} m vs "
                        f"{b['platform']} {b['resolution_m']} m): apparent detail differences are partly "
                        "sensor effects, not real change.")
    if abs(ya.month - yb.month) >= 3 and abs(ya.month - yb.month) <= 9:
        cautions.append(f"Different seasons ({ya:%b} vs {yb:%b}): vegetation, snow and shadow differ "
                        "seasonally.")
    for img in (a, b):
        if img["valid_fraction"] is not None and img["valid_fraction"] < 0.95:
            cautions.append(f"{img['acquired']}: only {img['valid_fraction'] * 100:.0f}% of the chip is clear "
                            "(cloud, shadow, snow or gaps).")
    if ghsl_note.startswith("GHSL built-up covers"):
        cautions.append(ghsl_note + "; compare the images visually.")
    elif ghsl_note:
        cautions.append(f"Built-up values for dates outside 1975-2020 are {ghsl_note}.")

    return {"settlement_id": s["settlement_id"], "settlement": s["name"],
            "a": a, "b": b, "years_between": round(years, 1), "metrics": metrics,
            "summary": lines, "cautions": cautions, "comparable_indicators": comparable,
            "evidence": "Images: observed. Indicators and built-up: derived. No change here is "
                        "validated on the ground."}


@app.get("/api/compare")
def compare(settlement_id: str, epoch_a: int, epoch_b: int):
    s = settlement(settlement_id)
    imgs = {i["epoch"]: i for i in images(settlement_id)}
    if epoch_a not in imgs or epoch_b not in imgs:
        raise HTTPException(404, "No image for one of the requested epochs; available: "
                                 + ", ".join(map(str, sorted(imgs))))
    a, b = sorted([imgs[epoch_a], imgs[epoch_b]], key=lambda i: i["acquired"])
    return change_summary(s, a, b)


@app.get("/api/timeline")
def timeline(settlement_id: str, step: int = Query(5, ge=5, le=50)):
    """Consecutive comparisons at roughly `step`-year spacing (e.g. every 5 or 10 years)."""
    s = settlement(settlement_id)
    imgs = images(settlement_id)
    chosen = []
    for img in imgs:
        if not chosen or img["epoch"] - chosen[-1]["epoch"] >= step:
            chosen.append(img)
    if imgs and chosen[-1] is not imgs[-1]:
        chosen.append(imgs[-1])
    return {"step": step, "epochs": [c["epoch"] for c in chosen],
            "pairs": [change_summary(s, x, y) for x, y in zip(chosen, chosen[1:])]}


@app.get("/api/province")
def province():
    return {
        "by_district": rows("""SELECT district, COUNT(*) settlements, SUM(buildings_in_window) buildings,
            SUM(buildings_le_2m) le2, SUM(buildings_le_5m) le5, SUM(buildings_le_10m) le10
            FROM settlements GROUP BY district ORDER BY le5 DESC"""),
        "by_type": rows("""SELECT local_level_type, COUNT(*) settlements, SUM(buildings_in_window) buildings,
            SUM(buildings_le_5m) le5 FROM settlements GROUP BY local_level_type"""),
        "ghsl": rows("""SELECT year, SUM(built_ha_window) built_ha_window, SUM(built_ha_zone10) built_ha_zone10
            FROM ghsl GROUP BY year ORDER BY year"""),
        "image_coverage": rows("""SELECT epoch, COUNT(*) images, AVG(valid_fraction) mean_clear
            FROM images GROUP BY epoch ORDER BY epoch"""),
    }


# --- live monitoring ---------------------------------------------------------------------------
# Two providers behind one API:
#   store    : dashboard/data/live.sqlite filled by live_update.py (local / always-on host)
#   ondemand : live_ondemand.py fetches and caches per request (serverless, e.g. Vercel)

import sys  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_ondemand as od  # noqa: E402

CDN_CACHE = {"Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600"}


def live_mode() -> str:
    forced = os.environ.get("LIVE_MODE")          # "store" | "ondemand"; default: store if the DB exists
    return forced if forced in ("store", "ondemand") else ("store" if LIVE_DB.exists() else "ondemand")


def live_rows(sql: str, args=()) -> list[dict]:
    if not LIVE_DB.exists():
        return []
    con = sqlite3.connect(f"file:{LIVE_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql, args)]
    finally:
        con.close()


def rain_category(mm: float | None) -> str | None:
    if mm is None:
        return None
    label = None
    for c in MON["rain_24h_categories_mm"]:
        if mm >= c["min"]:
            label = c["label"]
    return label


def _rolling_max(vals: list[float], n: int = 24) -> float | None:
    v = [x or 0 for x in vals]
    if not v:
        return None
    return max(sum(v[i:i + n]) for i in range(max(1, len(v) - n + 1)))


def _base_settlements() -> list[dict]:
    return rows("SELECT settlement_id, name, local_level, district, local_level_type, lat, lon, pcode, "
                "buildings_le_5m, exposure_rank FROM settlements ORDER BY settlement_id")


def _levels() -> list[dict]:
    return [{"pcode": r["pcode"], "name": r["name"], "geometry": json.loads(r["geojson"])}
            for r in rows("SELECT pcode, name, geojson FROM local_levels")]


def _live_data(sid: str | None = None) -> dict:
    """Raw live series for all settlements (or one), from whichever provider is active."""
    base = _base_settlements()
    if sid:
        base = [b for b in base if b["settlement_id"] == sid]
    ids = [b["settlement_id"] for b in base]
    if live_mode() == "store":
        ph = ",".join("?" * len(ids))
        group = lambda rs: {i: [r for r in rs if r["settlement_id"] == i] for i in ids}  # noqa: E731
        return dict(
            base=base,
            rain=group(live_rows(f"SELECT * FROM weather_hourly WHERE settlement_id IN ({ph}) ORDER BY time", ids)),
            q=group(live_rows(f"SELECT * FROM discharge_daily WHERE settlement_id IN ({ph}) ORDER BY date", ids)),
            scenes=group(live_rows(f"SELECT * FROM scenes WHERE settlement_id IN ({ph}) ORDER BY acquired", ids)),
            incidents=live_rows("SELECT * FROM incidents ORDER BY incident_on DESC"))
    allb = _base_settlements()
    with od.ThreadPoolExecutor(4) as ex:
        f_r = ex.submit(od.weather, allb, MON["weather"], MON["timezone"])
        f_q = ex.submit(od.discharge, allb, MON["discharge"])
        f_i = ex.submit(od.incidents, allb, _levels(), MON["incidents"])
        f_s = ex.submit(od.recent_items, MON["satellite"])
        rain, q, inc, items = f_r.result(), f_q.result(), f_i.result(), f_s.result()
    scenes = {}
    for b in base:
        scenes[b["settlement_id"]] = [
            dict(scene_id=i["id"], settlement_id=b["settlement_id"], collection=i["collection"],
                 acquired=i["datetime"][:10], orbit=i["orbit"], clear_fraction=None, zone_water_ha=None,
                 _item=i) for i in reversed(od.scenes_for(b, items))]
    return dict(base=base, rain={i: rain.get(i, []) for i in ids}, q={i: q.get(i, []) for i in ids},
                scenes=scenes, incidents=inc)


def _summary(b: dict, rain: list, q: list, scenes: list, incidents: list) -> dict:
    past = [r["precip_mm"] for r in rain if r["kind"] == "past"]
    fc = [r["precip_mm"] for r in rain if r["kind"] == "forecast"]
    rain24 = round(sum(x or 0 for x in past[-24:]), 1) if past else None
    fc24 = round(_rolling_max(fc), 1) if fc else None
    qp = [r["discharge"] for r in q if r["kind"] == "past" and r["discharge"] is not None]
    qf = [r["discharge"] for r in q if r["kind"] == "forecast" and r["discharge"] is not None]
    q_med = statistics.median(qp) if qp else None
    q_fmax = max(qf) if qf else None
    s1_all = [r for r in scenes if r["collection"] == "sentinel-1-rtc"]
    s1 = [r for r in s1_all if r.get("zone_water_ha") is not None]
    s2 = [r for r in scenes if r["collection"] == "sentinel-2-l2a" and (r.get("clear_fraction") or 0) >= 0.5]
    s1_ratio = None
    if len(s1) >= 3:
        base_w = statistics.median(r["zone_water_ha"] for r in s1[:-1])
        s1_ratio = round(s1[-1]["zone_water_ha"] / base_w, 2) if base_w else None
    since = (dt.date.today() - dt.timedelta(days=30)).isoformat()
    inc = [i for i in incidents if i["pcode"] == b["pcode"] and i["incident_on"] >= since]
    return {
        "settlement_id": b["settlement_id"],
        "rain_past24_mm": rain24, "rain_past24_category": rain_category(rain24),
        "rain_fc_max24_mm": fc24, "rain_fc_max24_category": rain_category(fc24),
        "discharge_past30_median": None if q_med is None else round(q_med, 2),
        "discharge_fc_max": None if q_fmax is None else round(q_fmax, 2),
        "discharge_fc_ratio": round(q_fmax / q_med, 2) if q_med and q_fmax is not None else None,
        "s1_latest": (s1[-1] if s1 else s1_all[-1])["acquired"] if s1_all else None,
        "s1_zone_water_ha": round(s1[-1]["zone_water_ha"], 2) if s1 else None,
        "s1_water_ratio": s1_ratio,
        "s2_latest_clear": s2[-1]["acquired"] if s2 else None,
        "incidents_30d": len(inc), "incident_last": inc[0]["incident_on"] if inc else None,
    }


@app.get("/api/live/status")
def live_status(response: Response):
    mode = live_mode()
    if mode == "ondemand":
        response.headers.update(CDN_CACHE)
    jobs = live_rows("SELECT job, MAX(finished) finished FROM runs WHERE status='ok' GROUP BY job")
    errors = live_rows("SELECT job, finished, message FROM runs WHERE status='error' ORDER BY finished DESC LIMIT 5")
    return {"available": True, "mode": mode, "last_ok": {j["job"]: j["finished"] for j in jobs},
            "recent_errors": errors, "schedule_minutes": MON["schedule_minutes"],
            "auto_update": os.environ.get("LIVE_UPDATES") == "1", "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "rain_categories": MON["rain_24h_categories_mm"]}


@app.get("/api/live/overview")
def live_overview(response: Response):
    if live_mode() == "ondemand":
        response.headers.update(CDN_CACHE)
    d = _live_data()
    out = []
    for b in d["base"]:
        i = b["settlement_id"]
        out.append({**b, **_summary(b, d["rain"][i], d["q"][i], d["scenes"][i], d["incidents"])})
    return out


@app.get("/api/live/settlements/{sid}")
def live_settlement(sid: str, response: Response):
    s = settlement(sid)
    d = _live_data(sid)
    scenes = d["scenes"][sid]
    if live_mode() == "ondemand":
        response.headers.update(CDN_CACHE)
        zone = json.loads(rows("SELECT geojson FROM scenarios WHERE settlement_id=? AND level_m=?",
                               (sid, MON["satellite"]["analysis_zone_hand_m"]))[0]["geojson"])
        polys = [f["geometry"] for f in zone["features"]]
        coords = [c for g in polys for c in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"])]
        feature = {"type": "Feature", "properties": {}, "geometry": {"type": "MultiPolygon", "coordinates": coords}}
        area = next(x["zone_area_ha"] for x in s["scenarios"] if x["level_m"] == MON["satellite"]["analysis_zone_hand_m"])
        bbox = od.window_bbox(s["lat"], s["lon"])
        latest = scenes[-MON["satellite"]["keep_latest_per_sensor"]:]
        with od.ThreadPoolExecutor(8) as ex:
            mets = list(ex.map(lambda sc: od.scene_metrics(sc["_item"], feature, area, MON["satellite"]["sentinel1"]["water_vv_db"])
                               if coords else {}, latest))
        for sc, m in zip(latest, mets):
            sc.update(m, preview_url=od.preview_url(sc["_item"], bbox), zone_area_ha=area)
        scenes = latest
    for sc in scenes:
        sc.pop("_item", None)
    return {
        "mode": live_mode(),
        "summary": _summary(d["base"][0], d["rain"][sid], d["q"][sid], scenes, d["incidents"]),
        "rain_hourly": d["rain"][sid], "discharge_daily": d["q"][sid],
        "scenes": list(reversed(scenes)),
        "incidents": [i for i in d["incidents"] if i["pcode"] == s["pcode"]
                      or (i["nearest_settlement_id"] == sid and (i["distance_km"] or 99) <= 10)][:50],
    }


@app.get("/api/live/incidents")
def live_incidents(response: Response, days: int = Query(30, ge=1, le=365)):
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    if live_mode() == "store":
        return live_rows("SELECT * FROM incidents WHERE incident_on>=? ORDER BY incident_on DESC", (since,))
    response.headers.update(CDN_CACHE)
    return [i for i in od.incidents(_base_settlements(), _levels(), MON["incidents"]) if i["incident_on"] >= since]


# --- external map layers ---------------------------------------------------------------------

_tilejson_cache: dict = {}


@app.get("/api/tilejson")
def tilejson(collection: str, item: str):
    """Planetary Computer tile endpoint for one scene at full resolution (its default rendering)."""
    key = (collection, item)
    if key not in _tilejson_cache:
        url = f"https://planetarycomputer.microsoft.com/api/stac/v1/collections/{collection}/items/{item}"
        with urlopen(Request(url, headers={"User-Agent": "karnali-dashboard"}), timeout=60) as r:
            it = json.load(r)
        tj = it.get("assets", {}).get("tilejson", {}).get("href")
        if not tj:
            raise HTTPException(404, "No tile rendering published for this scene")
        with urlopen(Request(tj, headers={"User-Agent": "karnali-dashboard"}), timeout=60) as r:
            _tilejson_cache[key] = json.load(r)
    return _tilejson_cache[key]


GIBS_LAYERS = ["VIIRS_NOAA20_CorrectedReflectance_TrueColor", "VIIRS_NOAA21_CorrectedReflectance_TrueColor",
               "MODIS_Terra_CorrectedReflectance_TrueColor", "HLS_S30_Nadir_BRDF_Adjusted_Reflectance",
               "HLS_L30_Nadir_BRDF_Adjusted_Reflectance", "OPERA_L3_Dynamic_Surface_Water_Extent-Sentinel-1",
               "OPERA_L3_Dynamic_Surface_Water_Extent-HLS", "MODIS_Combined_Flood_3-Day",
               "IMERG_Precipitation_Rate_30min", "OPERA_L3_DIST-ALERT-HLS_Color_Index"]
_gibs = {"t": 0.0, "data": {}}


@app.get("/api/gibs/latest")
def gibs_latest():
    """Latest available time, format and zoom for the NASA GIBS layers the map offers (cached 1 h)."""
    if time.time() - _gibs["t"] > 3600:
        url = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/1.0.0/WMTSCapabilities.xml"
        with urlopen(Request(url, headers={"User-Agent": "karnali-dashboard"}), timeout=90) as r:
            root = ET.parse(r).getroot()
        ns = {"w": "http://www.opengis.net/wmts/1.0", "ows": "http://www.opengis.net/ows/1.1"}
        out = {}
        for lyr in root.iter("{http://www.opengis.net/wmts/1.0}Layer"):
            i = lyr.find("ows:Identifier", ns).text
            if i not in GIBS_LAYERS:
                continue
            dim = lyr.find("w:Dimension", ns)
            tms = lyr.find("w:TileMatrixSetLink/w:TileMatrixSet", ns).text
            out[i] = {"default": dim.find("w:Default", ns).text if dim is not None else None,
                      "format": lyr.find("w:Format", ns).text, "matrix_set": tms,
                      "max_zoom": int(tms.rsplit("Level", 1)[1])}
        _gibs.update(t=time.time(), data=out)
    return _gibs["data"]


# --- files ----------------------------------------------------------------------------------

# On Vercel these are served by the CDN (vercel.json) and left out of the function bundle.
if (ROOT / "outputs").is_dir():
    app.mount("/outputs", StaticFiles(directory=ROOT / "outputs"), name="outputs")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
if LIVE_FRAMES.is_dir():   # only where the local updater runs; absent on Vercel
    app.mount("/live_frames", StaticFiles(directory=LIVE_FRAMES), name="live_frames")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/favicon.ico", include_in_schema=False)
@app.get("/apple-touch-icon.png", include_in_schema=False)
@app.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
def icon():
    return FileResponse(STATIC / "favicon.svg", media_type="image/svg+xml")


if __name__ == "__main__":
    import sys

    import uvicorn

    sys.path.insert(0, str(Path(__file__).parent))

    uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 8050)))
