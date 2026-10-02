"""Detect and process new Sentinel-2 (optical) and Sentinel-1 RTC (radar) scenes per settlement.

For every new scene over a settlement's 4 x 4 km window:
  * Sentinel-2 L2A: clear-pixel share (SCL), open water = MNDWI > 0, vegetation = NDVI > 0.3
  * Sentinel-1 RTC: open water = VV backscatter below a dB threshold (sees through cloud)
Water is measured only inside the HAND <= 10 m low-ground zone, where flood water would sit
and where radar shadow on steep slopes (a false-water source) is rare. A preview JPEG is kept.

Indicators are screening values, not validated flood maps.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import numpy as np
import planetary_computer as pc
import pyproj
from PIL import Image
from rasterio.enums import Resampling
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from shapely.geometry import shape
from shapely.ops import transform as shp_transform

from monitoring.store import now
from remote_sensing.imagery_timeseries import open_catalog, read_band, to_reflectance

RES = 10


def window(lon, lat, crs, half_m):
    x, y = pyproj.Transformer.from_crs(4326, crs, always_xy=True).transform(lon, lat)
    return (x - half_m, y - half_m, x + half_m, y + half_m)


def zone_mask(zone_geojson: dict, bounds, crs) -> np.ndarray:
    to_m = pyproj.Transformer.from_crs(4326, crs, always_xy=True).transform
    shp = [shp_transform(to_m, shape(f["geometry"])) for f in zone_geojson.get("features", [])]
    n = int(round((bounds[2] - bounds[0]) / RES))
    if not shp:
        return np.zeros((n, n), bool)
    return rasterize([(g, 1) for g in shp], out_shape=(n, n), transform=from_bounds(*bounds, n, n),
                     fill=0, dtype="uint8").astype(bool)


def _save(img: np.ndarray, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img).save(path, quality=85)


def process_s2(item, bounds, crs, zone, frame: Path) -> dict:
    a = lambda k, r=Resampling.bilinear: read_band(item.assets[k].href, bounds, crs, RES, r)  # noqa: E731
    d = item.datetime.date()
    scl = a("SCL", Resampling.nearest)
    nodata = scl == 0
    clear = ~nodata & ~np.isin(scl, [3, 8, 9, 10, 11])
    refl = {k: to_reflectance("sentinel-2-l2a", a(k).astype(np.float32)[None], d)[0]
            for k in ("B02", "B03", "B04", "B08", "B11")}
    with np.errstate(invalid="ignore", divide="ignore"):
        mndwi = (refl["B03"] - refl["B11"]) / (refl["B03"] + refl["B11"])
        ndvi = (refl["B08"] - refl["B04"]) / (refl["B08"] + refl["B04"])
    water = clear & (mndwi > 0)
    rgb = np.stack([refl["B04"], refl["B03"], refl["B02"]], -1)
    _save((np.clip(np.nan_to_num(rgb) / 0.25, 0, 1) ** (1 / 1.3) * 255).astype(np.uint8), frame)
    zc = zone & clear
    return dict(clear_fraction=float(clear.mean()),
                zone_water_ha=float((water & zone).sum() * RES * RES / 1e4),
                zone_area_ha=float(zone.sum() * RES * RES / 1e4),
                veg_fraction=float((ndvi[clear] > 0.3).mean()) if clear.any() else None,
                note=f"zone clear share {zc.sum() / max(zone.sum(), 1):.2f}; water counted on clear pixels only")


def process_s1(item, bounds, crs, zone, frame: Path, thr_db: float) -> dict:
    vv = read_band(item.assets["vv"].href, bounds, crs, RES).astype(np.float32)
    valid = np.isfinite(vv) & (vv > 0)
    db = np.full(vv.shape, np.nan, np.float32)
    db[valid] = 10 * np.log10(vv[valid])
    water = valid & (db < thr_db)
    g = (np.clip((np.nan_to_num(db, nan=-30) + 25) / 25, 0, 1) * 255).astype(np.uint8)
    img = np.stack([g, g, g], -1)
    img[water & zone] = (42, 120, 214)
    _save(img, frame)
    return dict(clear_fraction=float(valid.mean()),
                zone_water_ha=float((water & zone).sum() * RES * RES / 1e4),
                zone_area_ha=float(zone.sum() * RES * RES / 1e4), veg_fraction=None,
                note=f"VV < {thr_db} dB inside HAND <= 10 m zone; {item.properties.get('sat:orbit_state', '')} orbit")


def update_satellite(con, settlements: list[dict], zones: dict, cfg: dict, crs: str, half_m: float,
                     frames_dir: Path, workers: int = 6) -> int:
    from concurrent.futures import ThreadPoolExecutor

    cat = open_catalog()
    s2c, s1c = cfg["sentinel2"]["collection"], cfg["sentinel1"]["collection"]
    floor = (dt.date.today() - dt.timedelta(days=cfg["lookback_days"])).isoformat()

    # Read processing state up front: worker threads never touch the SQLite connection.
    last_seen = {(r[0], r[1]): r[2] for r in con.execute(
        "SELECT settlement_id, collection, MAX(acquired) FROM scenes GROUP BY 1, 2")}
    done_keys = {(r[0], r[1]) for r in con.execute("SELECT scene_id, settlement_id FROM scenes")}

    def last(sid, coll):
        r = last_seen.get((sid, coll))
        return max(r, floor) if r else floor

    def one(s):
        sid = s["settlement_id"]
        b = window(s["lon"], s["lat"], crs, half_m)
        zone = zone_mask(zones[sid], b, crs)
        out = []
        for coll in (s2c, s1c):
            q = dict(collections=[coll], intersects={"type": "Point", "coordinates": [s["lon"], s["lat"]]},
                     datetime=f"{last(sid, coll)}/{dt.date.today() + dt.timedelta(days=1)}")
            if coll == s2c:
                q["query"] = {"eo:cloud_cover": {"lt": cfg["sentinel2"]["max_scene_cloud"]}}
            for item in sorted(cat.search(**q).items(), key=lambda i: i.datetime):
                acq = item.datetime.date().isoformat()
                key = (item.id, sid)
                if key in done_keys:
                    continue
                item = pc.sign(item)
                frame = frames_dir / sid / f"{acq}_{'s2' if coll == s2c else 's1'}_{item.id[-12:]}.jpg"
                try:
                    m = (process_s2(item, b, crs, zone, frame) if coll == s2c
                         else process_s1(item, b, crs, zone, frame, cfg["sentinel1"]["water_vv_db"]))
                except Exception as e:  # unreadable asset or partial coverage
                    m = dict(clear_fraction=None, zone_water_ha=None, zone_area_ha=None, veg_fraction=None,
                             note=f"not processed: {type(e).__name__}")
                    frame = None
                out.append((item.id, sid, coll, acq, item.properties.get("sat:orbit_state"),
                            m["clear_fraction"], m["zone_water_ha"], m["zone_area_ha"], m["veg_fraction"],
                            str(frame.relative_to(frames_dir)) if frame else None, now(), m["note"]))
        return sid, out

    n = 0
    with ThreadPoolExecutor(workers) as ex:
        for sid, rows in ex.map(one, settlements):
            con.executemany("INSERT OR REPLACE INTO scenes VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", rows)
            n += len(rows)
            for coll in (s2c, s1c):   # retention: keep only the latest N per sensor
                old = con.execute("""SELECT scene_id, frame_path FROM scenes WHERE settlement_id=? AND collection=?
                                     ORDER BY acquired DESC LIMIT -1 OFFSET ?""",
                                  (sid, coll, cfg["keep_latest_per_sensor"])).fetchall()
                for scene_id, fp in old:
                    if fp:
                        (frames_dir / fp).unlink(missing_ok=True)
                    con.execute("DELETE FROM scenes WHERE scene_id=? AND settlement_id=?", (scene_id, sid))
            con.commit()
    return n


def zones_from_static_db(static_db: Path, level: int) -> dict:
    import sqlite3
    with sqlite3.connect(static_db) as c:
        return {sid: json.loads(g) for sid, g in
                c.execute("SELECT settlement_id, geojson FROM scenarios WHERE level_m=?", (level,))}
