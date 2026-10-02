"""Karnali Settlement Explorer: web dashboard backend (FastAPI + SQLite).

Serves the read-only dashboard database built by dashboard/build_db.py, the repository's
figures/frames, and the single-page frontend in dashboard/static/.

    python dashboard/app.py            # http://127.0.0.1:8050
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "dashboard/data/karnali_dashboard.sqlite"
STATIC = ROOT / "dashboard/static"
GHSL_FIRST, GHSL_LAST = 1975, 2020

SORTS = {"rank": "exposure_rank", "name": "name", "district": "district, name",
         "buildings": "buildings_in_window DESC", "le5": "buildings_le_5m DESC",
         "share5": "share_le_5m DESC", "id": "settlement_id"}

app = FastAPI(title="Karnali Settlement Explorer", docs_url="/api/docs")


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


# --- files ----------------------------------------------------------------------------------

app.mount("/outputs", StaticFiles(directory=ROOT / "outputs"), name="outputs")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/favicon.ico", include_in_schema=False)
@app.get("/apple-touch-icon.png", include_in_schema=False)
@app.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
def icon():
    return FileResponse(STATIC / "favicon.svg", media_type="image/svg+xml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 8050)))
