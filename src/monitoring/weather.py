"""Modelled rainfall (Open-Meteo forecast API) and river discharge (GloFAS via Open-Meteo).

Both APIs accept many coordinates per request, so all 79 settlements are fetched in one call.
Values are model output, not gauge observations. Open-Meteo data: CC BY 4.0.
"""
from __future__ import annotations

import datetime as dt
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from monitoring.store import now

UA = {"User-Agent": "karnali-settlement-hazard-mapping research dashboard"}


def _get(url: str, params: dict) -> list[dict]:
    with urlopen(Request(f"{url}?{urlencode(params)}", headers=UA), timeout=120) as r:
        d = json.load(r)
    if isinstance(d, dict) and d.get("error"):
        raise RuntimeError(d.get("reason", "Open-Meteo error"))
    return d if isinstance(d, list) else [d]


def _coords(settlements):
    return (",".join(f"{s['lat']:.5f}" for s in settlements),
            ",".join(f"{s['lon']:.5f}" for s in settlements))


def update_weather(con, settlements: list[dict], cfg: dict, tz: str) -> int:
    lat, lon = _coords(settlements)
    res = _get(cfg["url"], dict(latitude=lat, longitude=lon, hourly="precipitation", timezone=tz,
                                past_days=cfg["past_days"], forecast_days=cfg["forecast_days"]))
    cutoff = dt.datetime.now(ZoneInfo(tz)).strftime("%Y-%m-%dT%H:%M")
    fetched, n = now(), 0
    for s, r in zip(settlements, res):
        for t, v in zip(r["hourly"]["time"], r["hourly"]["precipitation"]):
            con.execute("INSERT OR REPLACE INTO weather_hourly VALUES (?,?,?,?,?)",
                        (s["settlement_id"], t, v, "past" if t <= cutoff else "forecast", fetched))
            n += 1
    con.commit()
    return n


def update_discharge(con, settlements: list[dict], cfg: dict) -> int:
    lat, lon = _coords(settlements)
    res = _get(cfg["url"], dict(latitude=lat, longitude=lon,
                                daily="river_discharge,river_discharge_median,river_discharge_max",
                                past_days=cfg["past_days"], forecast_days=cfg["forecast_days"]))
    today = dt.date.today().isoformat()
    fetched, n = now(), 0
    for s, r in zip(settlements, res):
        d = r["daily"]
        for i, day in enumerate(d["time"]):
            con.execute("INSERT OR REPLACE INTO discharge_daily VALUES (?,?,?,?,?,?,?,?,?)", (
                s["settlement_id"], day, d["river_discharge"][i], d["river_discharge_median"][i],
                d["river_discharge_max"][i], "past" if day < today else "forecast",
                r.get("latitude"), r.get("longitude"), fetched))
            n += 1
    con.commit()
    return n
