"""Province-wide first-pass screening of the primary settlement in each of Karnali's 79 local levels.

For every settlement this produces
  * a 5-year satellite image time series, 1972 -> latest dry season (Landsat MSS/TM/OLI, Sentinel-2)
  * terrain-based water-level scenarios (2/5/10 m above nearest mapped channel) and
    building counts inside them
  * GHSL built-up surface 1975-2020 for the window and inside the 10 m scenario zone

Inputs (prepared by src/data/fetch_karnali_inputs.py into $KARNALI_CACHE):
  admin/karnali_adm3.parquet, overture_localities.parquet, overture_water.parquet,
  overture_buildings.parquet, ghsl/karnali_built_s_E<year>.tif

Run:  KARNALI_CACHE=/path/to/cache PYTHONPATH=src python analysis/hazard_exposure/run_karnali_79.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj
import yaml
from rasterio.enums import Resampling
from rasterio.features import shapes as raster_shapes
from rasterio.transform import from_bounds
from shapely.geometry import box, shape

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from geospatial.select_settlements import (densest_building_cluster,  # noqa: E402
                                           resolve_primary_settlements,
                                           select_primary_settlements)
from hazard.flood_scenarios import channel_mask, hand, read_dem, scenario_zone  # noqa: E402
from remote_sensing.imagery_timeseries import Epoch, best_chip, open_catalog, read_band  # noqa: E402
from visualization.settlement_panels import scenario_figure, timeseries_figure  # noqa: E402

CACHE = Path(os.environ.get("KARNALI_CACHE", "/tmp/karnali_cache"))
CFG = yaml.safe_load(open(ROOT / "configs/analysis_parameters.yaml"))["karnali_79_screening"]
CRS = CFG["metric_crs"]
OUT_TS = ROOT / "outputs/figures/karnali_79/imagery_timeseries"
OUT_SC = ROOT / "outputs/figures/karnali_79/water_level_scenarios"
OUT_TAB = ROOT / "outputs/tables"
OUT_GEO = ROOT / "data/processed/karnali_79"
STATE = CACHE / "site_results"

# Official urban municipalities (Nagarpalika) of Karnali Province: 25 of 79 local levels.
# Source: Wikipedia "Administration in Karnali Province" (citing MoFALD local-level register),
# accessed 2026-10-02, matched to COD-AB adm3 names. All others are rural municipalities.
URBAN = {"Aathabisakot", "Aathbis", "Bagachour", "Banagad Kupinde", "Bheri Malika",
         "Bheriganga", "Birendranagar", "Chamunda Bindrasaini", "Chandannath", "Chaurjahari",
         "Chhayanath Rara", "Chhedagad", "Dullu", "Gurbhakot", "Khandachakra", "Lekabeshi",
         "Musikot", "Nalgad", "Narayan", "Panchapuri", "Raskot", "Sharada", "Thulibheri",
         "Tilagupha", "Tripurasundari"}


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def load_inputs():
    pal = gpd.read_parquet(CACHE / "admin/karnali_adm3.parquet")
    assert len(pal) == 79, len(pal)
    pal["local_level_type"] = np.where(pal["adm3_name"].isin(URBAN), "urban municipality",
                                       "rural municipality")
    assert (pal["local_level_type"] == "urban municipality").sum() == 25
    loc = gpd.read_parquet(CACHE / "overture_localities.parquet")
    water = gpd.read_parquet(CACHE / "overture_water.parquet")
    water = water[water["subtype"].isin(CFG["water_level_scenarios"]["channel_subtypes"])].to_crs(CRS)
    b = pd.read_parquet(CACHE / "overture_buildings.parquet")
    x, y = pyproj.Transformer.from_crs(4326, CRS, always_xy=True).transform(b.lon.values, b.lat.values)
    return pal, loc, water, np.column_stack([x, y]), b["src"].values


def build_settlements(pal, loc, bxy):
    sel = CFG["settlement_selection"]
    named = select_primary_settlements(pal, loc, bxy, sel["building_count_radius_m"], CRS)
    cl = densest_building_cluster(pal, bxy, sel["building_count_radius_m"], CRS)
    s = resolve_primary_settlements(named, cl, loc, sel["min_share_of_densest_cluster"], CRS)
    s = s.merge(pal[["adm3_pcode", "adm3_name", "adm2_name", "local_level_type"]], on="adm3_pcode")
    s = s.sort_values("adm3_pcode").reset_index(drop=True)
    s["settlement_id"] = [f"KAR-SET-{i + 1:03d}" for i in range(len(s))]
    ll = s.to_crs(4326)
    s["lon"], s["lat"] = ll.geometry.x.round(6), ll.geometry.y.round(6)
    # Display name: Overture English name where available, else the primary name; cluster
    # selections more than 1 km from their label are shown as "area near <name>".
    base = s["name_en"].where(s["name_en"].notna(), s["name"])
    far = (s["selection_method"] == "densest_building_cluster_nearest_name") & (s["label_distance_m"] > 1000)
    s["display_name"] = np.where(far, "area near " + base, base)
    return s


def ghsl_series(bounds, res, zone):
    """Built-up m^2 per epoch in the window and inside `zone` (bool grid)."""
    lat = (bounds[1] + bounds[3]) / 2  # metric; convert centre to lat for GHSL cell area
    _, lat = pyproj.Transformer.from_crs(CRS, 4326, always_xy=True).transform(
        (bounds[0] + bounds[2]) / 2, lat)
    cell_m2 = (111320 * np.cos(np.radians(lat)) / 1200) * (110574 / 1200)
    tot, inz = {}, {}
    for y in CFG["ghsl_epochs"]:
        v = read_band(str(CACHE / f"ghsl/karnali_built_s_E{y}.tif"), bounds, CRS, res,
                      Resampling.bilinear).astype(np.float64)
        built = np.clip(v, 0, None) / cell_m2 * res * res
        tot[y], inz[y] = float(built.sum()), float(built[zone].sum())
    return tot, inz


def process_site(row, water, bxy, bsrc, catalog):
    sid, name = row["settlement_id"], row["display_name"]
    label = f"{sid} {name} ({row['adm3_name']} {row['local_level_type']}, {row['adm2_name']})"
    fslug = f"{sid}_{slug(row['adm3_name'])}"
    half = CFG["analysis_window_m"] / 2
    cx, cy = row.geometry.x, row.geometry.y
    win = (cx - half, cy - half, cx + half, cy + half)
    buf = CFG["hazard_context_buffer_m"]
    ctx = (win[0] - buf, win[1] - buf, win[2] + buf, win[3] + buf)
    res = CFG["water_level_scenarios"]["resolution_m"]
    levels = CFG["water_level_scenarios"]["levels_m"]
    im = CFG["imagery"]

    # --- imagery time series -------------------------------------------------------
    chips, cat_rows = [], []
    for e in im["epochs"]:
        chip = None
        for coll in [e["collection"]] + ([e["fallback"]] if e.get("fallback") else []):
            ep = Epoch(e["label"], e["target_year"], coll, e["start"], e["end"])
            chip = best_chip(catalog, ep, (row["lon"], row["lat"]), win, CRS,
                             im["dry_season_months"], im["max_candidates_per_epoch"],
                             im["max_chip_cloud_fraction"], im["max_chip_nodata_fraction"])
            if chip is not None:
                break
        chips.append((e["label"], chip))
        if chip is not None:
            cat_rows.append(dict(
                imagery_id=f"{sid}_{e['label']}", source_name=chip.item_id,
                provider="USGS Landsat Collection 2" if chip.collection.startswith("landsat")
                else "ESA Copernicus Sentinel-2",
                license="Public domain (USGS)" if chip.collection.startswith("landsat")
                else "Copernicus Sentinel data terms (free, attribution)",
                acquisition_date=chip.acquired, year=chip.acquired[:4],
                sensor_or_product=f"{chip.platform} / Planetary Computer {chip.collection}",
                resolution=f"{chip.resolution_m} m",
                extent=f"{CFG['analysis_window_m'] / 1000:g} km window centred {row['lon']},{row['lat']}",
                crs=CRS, relative_path="NA (streamed; not stored)",
                checksum="NA",
                cloud_or_quality_notes=(f"chip cloud/shadow fraction {chip.chip_cloud_fraction}; "
                                        f"chip no-data fraction {chip.chip_nodata_fraction}; "
                                        f"scene cloud cover {chip.scene_cloud_cover}; "
                                        f"sun elevation {chip.sun_elevation}"),
                processing_status="displayed in figure",
                notes=f"epoch {e['label']}; {chip.display}; figure "
                      f"outputs/figures/karnali_79/imagery_timeseries/{fslug}_timeseries_1972_2026.png"))
    first = next((c for _, c in chips if c is not None), None)
    timeseries_figure(OUT_TS / f"{fslug}_timeseries_1972_2026.png",
                      f"{label}: satellite time series 1972-2026",
                      f"{CFG['analysis_window_m'] / 1000:g} x {CFG['analysis_window_m'] / 1000:g} km window; "
                      f"dry-season (Oct-Apr) scenes; one frame per 5-year epoch "
                      f"(first usable scene: {first.acquired if first else 'none'})",
                      chips, CFG["analysis_window_m"])

    # --- water-level scenarios -------------------------------------------------------
    dem, dem_ids = read_dem(ctx, CRS, res)
    tctx = from_bounds(*ctx, int((ctx[2] - ctx[0]) / res), int((ctx[3] - ctx[1]) / res))
    w = water.iloc[water.sindex.query(box(*ctx))]
    lines = w[w.geom_type.isin(["LineString", "MultiLineString"])].geometry
    polys = w[w.geom_type.isin(["Polygon", "MultiPolygon"])].geometry
    ch = channel_mask(lines, polys, tctx, dem.shape)
    nb = int(buf / res)
    sl = (slice(nb, dem.shape[0] - nb), slice(nb, dem.shape[1] - nb))
    if ch.any():
        hand_m, dist = hand(dem, ch, tctx, CRS, CFG["water_level_scenarios"]["channel_burn_m"])
        zones_ctx = {h: scenario_zone(hand_m, h) for h in levels}
    else:
        hand_m, dist = np.full(dem.shape, np.nan), np.full(dem.shape, np.inf)
        zones_ctx = {h: np.zeros(dem.shape, bool) for h in levels}
    zones = {h: z[sl] for h, z in zones_ctx.items()}
    hand_w, dist_w = hand_m[sl], dist[sl]

    inside = ((bxy[:, 0] >= win[0]) & (bxy[:, 0] < win[2]) & (bxy[:, 1] >= win[1]) & (bxy[:, 1] < win[3]))
    pts = bxy[inside]
    src = bsrc[inside]
    px = np.column_stack([(pts[:, 0] - win[0]) / res, (win[3] - pts[:, 1]) / res])
    ix = np.clip(px.astype(int), 0, hand_w.shape[1] - 1)
    in_zone = {h: zones[h][ix[:, 1], ix[:, 0]] for h in levels}
    b_hand = hand_w[ix[:, 1], ix[:, 0]]
    b_dist = dist_w[ix[:, 1], ix[:, 0]] * res

    # nearest mapped channel to the settlement point
    named = w[w["name"].notna()]
    pt = gpd.points_from_xy([cx], [cy], crs=CRS)[0]
    near_name, near_d = "unknown", np.nan
    if len(named):
        d = named.distance(pt)
        near_name, near_d = named.loc[d.idxmin(), "name"], float(d.min())
    rivers = w[w["subtype"] == "river"]
    river_d = float(rivers.distance(pt).min()) if len(rivers) else np.nan

    ghsl_tot, ghsl_zone = ghsl_series(win, res, zones[max(levels)])
    base = next((c for _, c in reversed(chips) if c is not None), None)
    scenario_figure(OUT_SC / f"{fslug}_water_level_scenarios.png", label, base, zones, px,
                    in_zone, hand_w, ghsl_tot, ghsl_zone, levels)

    # scenario zone polygons for the GeoJSON layer
    twin = from_bounds(*win, zones[levels[0]].shape[1], zones[levels[0]].shape[0])
    zone_feats = []
    for h in levels:
        for geom, v in raster_shapes(zones[h].astype("uint8"), mask=zones[h], transform=twin):
            zone_feats.append({"settlement_id": sid, "water_level_m": h, "geometry": shape(geom)})

    n = len(pts)
    rec = dict(
        settlement_id=sid, settlement_name=name, name_primary=row["name"], local_level=row["adm3_name"],
        local_level_pcode=row["adm3_pcode"], local_level_type=row["local_level_type"],
        district=row["adm2_name"], lon=row["lon"], lat=row["lat"],
        selection_method=row["selection_method"],
        locality_class=row["class"] if isinstance(row["class"], str) else "unknown",
        overture_locality_id=row["id"], osm_record=row["src_id"],
        buildings_in_window=n,
        buildings_osm=int((src == "OpenStreetMap").sum()),
        buildings_google=int((src == "Google Open Buildings").sum()),
        buildings_microsoft=int((src == "Microsoft ML Buildings").sum()),
        nearest_named_water=near_name, nearest_named_water_m=round(near_d, 0),
        nearest_river_line_m=round(river_d, 0),
        channels_mapped_in_context=bool(ch.any()),
        buildings_within_100m_of_channel=int((b_dist <= 100).sum()),
        median_building_hand_m=round(float(np.nanmedian(b_hand)), 1) if n else np.nan,
        dem_tiles=";".join(dem_ids),
        first_scene_date=first.acquired if first else "NA",
        latest_scene_date=base.acquired if base else "NA",
        epochs_with_imagery=sum(c is not None for _, c in chips),
    )
    for h in levels:
        rec[f"buildings_le_{h}m"] = int(in_zone[h].sum())
        rec[f"share_le_{h}m"] = round(float(in_zone[h].mean()), 3) if n else 0.0
        rec[f"zone_area_le_{h}m_ha"] = round(float(zones[h].sum()) * res * res / 1e4, 1)
    for y in CFG["ghsl_epochs"]:
        rec[f"ghsl_built_ha_{y}"] = round(ghsl_tot[y] / 1e4, 2)
        rec[f"ghsl_built_in_{max(levels)}m_zone_ha_{y}"] = round(ghsl_zone[y] / 1e4, 2)
    return rec, cat_rows, zone_feats


def main(only=None, workers=6):
    for p in (OUT_TS, OUT_SC, OUT_TAB, OUT_GEO, STATE):
        p.mkdir(parents=True, exist_ok=True)
    pal, loc, water, bxy, bsrc = load_inputs()
    s = build_settlements(pal, loc, bxy)
    s.to_crs(4326)[["settlement_id", "display_name", "name", "name_en", "adm3_name", "adm3_pcode",
                    "local_level_type", "adm2_name",
                    "class", "selection_method", "label_distance_m", "buildings_within_radius",
                    "candidates_in_palika",
                    "id", "src_id", "geometry"]].to_file(OUT_GEO / "karnali_79_settlements.geojson",
                                                          driver="GeoJSON")
    pal.to_crs(4326).assign(geometry=lambda d: d.geometry.simplify(0.0005))[
        ["adm3_pcode", "adm3_name", "adm2_name", "local_level_type", "geometry"]].to_file(
        OUT_GEO / "karnali_79_local_levels.geojson", driver="GeoJSON")
    _ = water.sindex
    catalog = open_catalog()
    todo = [r for _, r in s.iterrows() if (only is None or r["settlement_id"] in only)
            and not (STATE / f"{r['settlement_id']}.json").exists()]
    print(f"{len(todo)} settlements to process", flush=True)

    def run(r):
        rec, cat_rows, zf = process_site(r, water, bxy, bsrc, catalog)
        json.dump({"rec": rec, "catalog": cat_rows}, open(STATE / f"{r['settlement_id']}.json", "w"),
                  default=float)
        gpd.GeoDataFrame(zf, crs=CRS).to_parquet(STATE / f"{r['settlement_id']}_zones.parquet") if zf else None
        return r["settlement_id"]

    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(run, r): r["settlement_id"] for r in todo}
        for f in as_completed(futs):
            try:
                print("done", f.result(), flush=True)
            except Exception:
                print("FAILED", futs[f], traceback.format_exc(), flush=True)


if __name__ == "__main__":
    only = set(sys.argv[1:]) or None
    main(only)
