"""Water-related disaster incidents in Karnali from the BIPAD portal (Government of Nepal).

Each incident is assigned to the local level containing its point and to the nearest of the
79 screened settlements (with distance), so it can be shown next to that settlement.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from shapely.geometry import Point, shape

from monitoring.store import now

UA = {"User-Agent": "karnali-settlement-hazard-mapping research dashboard"}
HAZARDS = {11: "Flood", 14: "Heavy Rainfall", 17: "Landslide", 19: "Rainfall",
           26: "Glacial lake outburst", 28: "Inundation", 29: "Soil Erosion"}


def _km(lat1, lon1, lat2, lon2):
    r = math.radians
    a = (math.sin(r(lat2 - lat1) / 2) ** 2
         + math.cos(r(lat1)) * math.cos(r(lat2)) * math.sin(r(lon2 - lon1) / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(a))


def update_incidents(con, settlements: list[dict], local_levels: list[dict], cfg: dict) -> int:
    since = (dt.date.today() - dt.timedelta(days=cfg["lookback_days"])).isoformat()
    polys = [(ll["pcode"], ll["name"], shape(ll["geometry"])) for ll in local_levels]
    fetched, n = now(), 0
    for hid in cfg["hazard_ids"]:
        url = cfg["url"] + "?" + urlencode(dict(format="json", province=cfg["province_id"], hazard=hid,
                                                incident_on__gt=since, expand="loss", limit=200))
        while url:
            with urlopen(Request(url, headers=UA), timeout=120) as r:
                page = json.load(r)
            for x in page["results"]:
                pt = (x.get("point") or {}).get("coordinates")
                lon, lat = (pt or (None, None))
                pcode = lname = sid = None
                dist = None
                if lon is not None:
                    p = Point(lon, lat)
                    hit = next((c for c in polys if c[2].contains(p)), None)
                    if hit:
                        pcode, lname = hit[0], hit[1]
                    near = min(settlements, key=lambda s: _km(lat, lon, s["lat"], s["lon"]))
                    sid, dist = near["settlement_id"], round(_km(lat, lon, near["lat"], near["lon"]), 1)
                loss = x.get("loss") or {}
                con.execute("INSERT OR REPLACE INTO incidents VALUES (" + ",".join("?" * 19) + ")", (
                    x["id"], hid, HAZARDS.get(hid, str(hid)), x.get("title"), (x.get("incidentOn") or "")[:10],
                    lon, lat, pcode, lname, sid, dist,
                    loss.get("peopleDeathCount"), loss.get("peopleMissingCount"), loss.get("peopleInjuredCount"),
                    loss.get("familyAffectedCount"), loss.get("infrastructureDestroyedHouseCount"),
                    loss.get("infrastructureAffectedHouseCount"), int(bool(x.get("verified"))), fetched))
                n += 1
            url = page.get("next") if page["results"] else None
    con.commit()
    return n
