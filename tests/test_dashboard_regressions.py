import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard"))
import app as dashboard
import live_ondemand as live


def test_read_query_closes_connection(monkeypatch):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    monkeypatch.setattr(dashboard, "db", lambda: connection)
    assert dashboard.rows("SELECT 1 AS value") == [{"value": 1}]
    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")


def test_read_query_closes_connection_on_error(monkeypatch):
    connection = sqlite3.connect(":memory:")
    monkeypatch.setattr(dashboard, "db", lambda: connection)
    with pytest.raises(sqlite3.OperationalError):
        dashboard.rows("SELECT * FROM missing")
    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")


def test_scene_cache_distinguishes_geometry_threshold_and_collection(monkeypatch):
    live._cache.clear()
    calls = []

    def stats(item, zone, params):
        calls.append((item, zone, params))
        return {"histogram": [[len(calls), 10], [0, 1, 2]], "valid_pixels": 10}

    monkeypatch.setattr(live, "_stats", stats)
    item = {"id": "same-scene", "collection": "sentinel-1-rtc"}
    zone_a = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}
    zone_b = {"type": "Polygon", "coordinates": [[[2, 0], [3, 0], [3, 1], [2, 0]]]}
    first = live.scene_metrics(item, zone_a, 100, -15)
    assert live.scene_metrics(item, zone_a, 100, -15) == first
    assert len(calls) == 1
    second = live.scene_metrics(item, zone_b, 100, -15)
    third = live.scene_metrics(item, zone_a, 100, -20)
    fourth = live.scene_metrics({**item, "collection": "sentinel-1-other"}, zone_a, 100, -15)
    assert [r["zone_water_ha"] for r in (first, second, third, fourth)] == [10, 20, 30, 40]
    assert len(calls) == 4
    live._cache.clear()


def test_live_settlement_includes_incidents_at_zero_distance(monkeypatch):
    from fastapi import Response

    incidents = [
        {"id": name, "pcode": "elsewhere", "nearest_settlement_id": "s1", "distance_km": distance}
        for name, distance in [("at-site", 0), ("boundary", 10), ("outside", 10.1), ("unknown", None)]
    ]
    incidents.append({"id": "same-region", "pcode": "region", "nearest_settlement_id": "s2", "distance_km": None})
    monkeypatch.setattr(dashboard, "settlement", lambda sid: {"pcode": "region"})
    monkeypatch.setattr(dashboard, "live_mode", lambda: "store")
    monkeypatch.setattr(dashboard, "_summary", lambda *args: {})
    monkeypatch.setattr(dashboard, "_live_data", lambda sid: {
        "base": [{}], "scenes": {sid: []}, "rain": {sid: []}, "q": {sid: []}, "incidents": incidents,
    })
    result = dashboard.live_settlement("s1", Response())
    assert [row["id"] for row in result["incidents"]] == ["at-site", "boundary", "same-region"]


@pytest.mark.parametrize("values", [[None] * 24, [1.0] * 23, [1.0] * 23 + [None], [float("nan")] * 24, [float("inf")] * 24])
def test_incomplete_rainfall_is_unknown(values):
    rain = [{"kind": kind, "precip_mm": value} for kind in ("past", "forecast") for value in values]
    result = dashboard._summary({"settlement_id": "s1", "pcode": "region"}, rain, [], [], [])
    for key in ("rain_past24_mm", "rain_past24_category", "rain_fc_max24_mm", "rain_fc_max24_category"):
        assert result[key] is None


def test_complete_rainfall_retains_zero_and_rolling_totals():
    assert dashboard._rolling_max([0.0] * 24) == 0
    assert dashboard._rolling_max([1.0] * 24 + [2.0] * 24) == 48
    rain = [{"kind": "past", "precip_mm": value} for value in [None] + [0.0] * 24]
    result = dashboard._summary({"settlement_id": "s1", "pcode": "region"}, rain, [], [], [])
    assert result["rain_past24_mm"] == 0
    assert result["rain_fc_max24_mm"] is None


def test_sparse_ghsl_clamps_to_first_available_epoch():
    series = [{"year": 1990, "built": 10}, {"year": 2020, "built": 40}]
    assert dashboard.ghsl_at(series, 1975, "built") == (10, "clamped to GHSL 1990")


def test_ghsl_interpolation_is_independent_of_row_order():
    series = [{"year": 2020, "built": 40}, {"year": 1990, "built": 10}]
    assert dashboard.ghsl_at(series, 2005, "built") == (25, "")


def test_ghsl_missing_and_single_epoch_values():
    assert dashboard.ghsl_at([{ "year": 1975, "built": None}], 2000, "built") == (None, "no GHSL data")
    assert dashboard.ghsl_at([{ "year": 2000, "built": 12}], 2020, "built") == (12, "clamped to GHSL 2000")


def test_ghsl_complete_epoch_range_is_preserved():
    series = [{"year": 1975, "built": 0}, {"year": 2020, "built": 45}]
    assert dashboard.ghsl_at(series, 2000, "built") == (25, "")
    assert dashboard.ghsl_at(series, 2025, "built") == (45, "clamped to GHSL 2020")
