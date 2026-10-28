"""On-demand live data for serverless hosting (Vercel), standard library only.

Used by app.py when there is no local live database (dashboard/data/live.sqlite), e.g. on Vercel,
where nothing can run in the background and the filesystem is read-only. Each source is fetched
when requested and kept in an in-process cache; app.py also sets CDN cache headers.

  rain + discharge   Open-Meteo forecast and GloFAS flood APIs (all 79 points in one call each)
  incidents          BIPAD API, assigned to local levels with a pure-Python point-in-polygon test
  scenes             STAC search over Karnali (Sentinel-1 RTC, Sentinel-2 L2A); previews are
                     full-resolution crops rendered by the Planetary Computer data API, and water
                     in the HAND <= 10 m zone is computed server-side by its /statistics endpoint
                     (histogram of VV below the threshold; MNDWI > 0 on SCL-clear Sentinel-2 pixels)
"""
from __future__ import annotations

import datetime as dt
import json
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

UA = {"User-Agent": "karnali-settlement-hazard-mapping dashboard", "Content-Type": "application/json"}
PC = "https://planetarycomputer.microsoft.com/api"
KARNALI_BBOX = [80.98, 28.16, 83.69, 30.45]
HAZARDS = {11: "Flood", 14: "Heavy Rainfall", 17: "Landslide", 19: "Rainfall",
           26: "Glacial lake outburst", 28: "Inundation", 29: "Soil Erosion"}

_cache: dict = {}
_lock = threading.Lock()


def cached(key, ttl_s, fn):
    with _lock:
        hit = _cache.get(key)
        if hit and time.time() - hit[0] < ttl_s:
            return hit[1]
    val = fn()
    with _lock:
        _cache[key] = (time.time(), val)
    return val


def get_json(url, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    with urlopen(Request(url, data=data, headers=UA), timeout=timeout) as r:
        return json.load(r)


# --- geometry helpers (no shapely on Vercel) ---------------------------------------------------

def _in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][:2]
        xj, yj = ring[j][:2]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi:
            inside = not inside
        j = i
    return inside


def point_in_geom(x, y, geom) -> bool:
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom.get("coordinates", [])
    for poly in polys:
        if poly and _in_ring(x, y, poly[0]) and not any(_in_ring(x, y, h) for h in poly[1:]):
            return True
    return False


def km(lat1, lon1, lat2, lon2):
    r = math.radians
    a = math.sin(r(lat2 - lat1) / 2) ** 2 + math.cos(r(lat1)) * math.cos(r(lat2)) * math.sin(r(lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def window_bbox(lat, lon, half_m=2000):
    dlat = half_m / 111320
    dlon = half_m / (111320 * math.cos(math.radians(lat)))
    return [lon - dlon, lat - dlat, lon + dlon, lat + dlat]


# --- rain and discharge ------------------------------------------------------------------------

def weather(settlements, cfg, tz):
    def fetch():
        q = dict(latitude=",".join(f"{s['lat']:.5f}" for s in settlements),
                 longitude=",".join(f"{s['lon']:.5f}" for s in settlements),
                 hourly="precipitation", timezone=tz, past_days=cfg["past_days"], forecast_days=cfg["forecast_days"])
        res = get_json(f"{cfg['url']}?{urlencode(q)}", timeout=90)
        res = res if isinstance(res, list) else [res]
        cutoff = dt.datetime.now(ZoneInfo(tz)).strftime("%Y-%m-%dT%H:%M")
        return {s["settlement_id"]: [{"time": t, "precip_mm": v, "kind": "past" if t <= cutoff else "forecast"}
                                     for t, v in zip(r["hourly"]["time"], r["hourly"]["precipitation"])]
                for s, r in zip(settlements, res)}
    return cached("weather", 1800, fetch)


def discharge(settlements, cfg):
    def fetch():
        q = dict(latitude=",".join(f"{s['lat']:.5f}" for s in settlements),
                 longitude=",".join(f"{s['lon']:.5f}" for s in settlements),
                 daily="river_discharge,river_discharge_median,river_discharge_max",
                 past_days=cfg["past_days"], forecast_days=cfg["forecast_days"])
        res = get_json(f"{cfg['url']}?{urlencode(q)}", timeout=90)
        res = res if isinstance(res, list) else [res]
        today = dt.date.today().isoformat()
        out = {}
        for s, r in zip(settlements, res):
            d = r["daily"]
            out[s["settlement_id"]] = [dict(date=day, discharge=d["river_discharge"][i],
                                            discharge_median=d["river_discharge_median"][i],
                                            discharge_max=d["river_discharge_max"][i],
                                            kind="past" if day < today else "forecast",
                                            cell_lat=r.get("latitude"), cell_lon=r.get("longitude"))
                                       for i, day in enumerate(d["time"])]
        return out
    return cached("discharge", 3 * 3600, fetch)


# --- incidents ---------------------------------------------------------------------------------

def incidents(settlements, levels, cfg):
    def fetch_hazard(hid):
        since = (dt.date.today() - dt.timedelta(days=cfg["lookback_days"])).isoformat()
        url = cfg["url"] + "?" + urlencode(dict(format="json", province=cfg["province_id"], hazard=hid,
                                                incident_on__gt=since, expand="loss", limit=200))
        rows = []
        while url:
            page = get_json(url, timeout=90)
            for x in page["results"]:
                lon, lat = ((x.get("point") or {}).get("coordinates") or (None, None))
                pcode = lname = sid = dist = None
                if lon is not None:
                    hit = next((ll for ll in levels if point_in_geom(lon, lat, ll["geometry"])), None)
                    if hit:
                        pcode, lname = hit["pcode"], hit["name"]
                    near = min(settlements, key=lambda s: km(lat, lon, s["lat"], s["lon"]))
                    sid, dist = near["settlement_id"], round(km(lat, lon, near["lat"], near["lon"]), 1)
                loss = x.get("loss") or {}
                rows.append(dict(incident_id=x["id"], hazard_id=hid, hazard=HAZARDS.get(hid, str(hid)),
                                 title=x.get("title"), incident_on=(x.get("incidentOn") or "")[:10],
                                 lon=lon, lat=lat, pcode=pcode, local_level=lname, nearest_settlement_id=sid,
                                 distance_km=dist, deaths=loss.get("peopleDeathCount"),
                                 missing=loss.get("peopleMissingCount"), injured=loss.get("peopleInjuredCount"),
                                 families_affected=loss.get("familyAffectedCount"),
                                 houses_destroyed=loss.get("infrastructureDestroyedHouseCount"),
                                 houses_affected=loss.get("infrastructureAffectedHouseCount"),
                                 verified=int(bool(x.get("verified")))))
            url = page.get("next") if page["results"] else None
        return rows

    def fetch():
        with ThreadPoolExecutor(len(cfg["hazard_ids"])) as ex:
            rows = [r for part in ex.map(fetch_hazard, cfg["hazard_ids"]) for r in part]
        return sorted(rows, key=lambda r: r["incident_on"], reverse=True)
    return cached("incidents", 3600, fetch)


# --- satellite scenes --------------------------------------------------------------------------

def recent_items(cfg, days=21):
    """Recent Sentinel-1 RTC and Sentinel-2 L2A items over Karnali (one STAC search each)."""
    def fetch():
        since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        out = []
        for coll, extra in ((cfg["sentinel1"]["collection"], {}),
                            (cfg["sentinel2"]["collection"],
                             {"query": {"eo:cloud_cover": {"lt": cfg["sentinel2"]["max_scene_cloud"]}}})):
            body = {"collections": [coll], "bbox": KARNALI_BBOX, "datetime": f"{since}/..", "limit": 250, **extra}
            url = f"{PC}/stac/v1/search"
            while url:
                page = get_json(url, body, timeout=90)
                for f in page["features"]:
                    out.append({"id": f["id"], "collection": coll, "geometry": f["geometry"],
                                "datetime": f["properties"]["datetime"],
                                "orbit": f["properties"].get("sat:orbit_state"),
                                "tilejson": f["assets"].get("tilejson", {}).get("href")})
                nxt = next((ln for ln in page.get("links", []) if ln.get("rel") == "next"), None)
                url, body = (nxt["href"], nxt.get("body", body)) if nxt else (None, None)
        return out
    return cached(("items", days), 3 * 3600, fetch)


def _render_qs(item):
    return item["tilejson"].split("?", 1)[1] if item.get("tilejson") else \
        urlencode({"collection": item["collection"], "item": item["id"]})


def preview_url(item, bbox, size=400):
    b = ",".join(f"{v:.5f}" for v in bbox)
    return f"{PC}/data/v1/item/bbox/{b}/{size}x{size}.png?{_render_qs(item)}"


def _stats(item, feature, params):
    q = urlencode({"collection": item["collection"], "item": item["id"], "max_size": 1024, **params}, doseq=True)
    res = get_json(f"{PC}/data/v1/item/statistics?{q}", feature, timeout=60)
    return next(iter(res["properties"]["statistics"].values()))


def scene_metrics(item, zone_feature, zone_area_ha, thr_db):
    """Water area (ha) inside the low-ground zone, computed by the Planetary Computer service."""
    def fetch():
        try:
            if "sentinel-1" in item["collection"]:
                thr = 10 ** (thr_db / 10)
                st = _stats(item, zone_feature, {"assets": "vv", "histogram_bins": f"0,{thr},1e6"})
                below = st["histogram"][0][0]
                n = st["valid_pixels"] or 1
                return dict(clear_fraction=None, zone_water_ha=below / n * zone_area_ha,
                            note=f"VV < {thr_db} dB inside HAND <= 10 m zone (server-side)")
            # one call: MNDWI on clear pixels (SCL 4-7); cloud/shadow/snow/no-data mapped to -2
            st = _stats(item, zone_feature, {"expression": "where((SCL>=4)&(SCL<=7),(B03-B11)/(B03+B11),-2)",
                                             "asset_as_band": "true", "histogram_bins": "-3,-1.5,0,1.01"})
            masked, dry, wet = st["histogram"][0]
            total = (masked + dry + wet) or 1
            return dict(clear_fraction=(dry + wet) / total, zone_water_ha=wet / total * zone_area_ha,
                        note="MNDWI > 0 on clear pixels inside HAND <= 10 m zone (server-side)")
        except Exception as e:
            return dict(clear_fraction=None, zone_water_ha=None, note=f"metrics unavailable: {type(e).__name__}")
    return cached(("metrics", item["id"], zone_area_ha), 12 * 3600, fetch)


def scenes_for(settlement, items):
    return sorted((i for i in items if point_in_geom(settlement["lon"], settlement["lat"], i["geometry"])),
                  key=lambda i: i["datetime"], reverse=True)
