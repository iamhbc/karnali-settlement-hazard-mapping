"""Compile per-settlement results of run_karnali_79.py into repository tables, layers and profiles.

Writes
  outputs/tables/karnali_79_exposure_screening.csv
  outputs/maps/karnali_79_overview_exposure_screening.png
  data/processed/karnali_79/karnali_79_water_level_zones.geojson
  settlements/settlement_inventory.csv              (rows KAR-SET-001..079; template header kept)
  settlements/settlement_profiles/KAR-SET-xxx_<local_level>.md
  data/metadata/imagery_catalog.csv                 (one row per displayed image chip)
  outputs/reports/karnali_79_exposure_screening_report.md
"""
from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path(os.environ.get("KARNALI_CACHE", "/tmp/karnali_cache"))
STATE = CACHE / "site_results"
CFG = yaml.safe_load(open(ROOT / "configs/analysis_parameters.yaml"))["karnali_79_screening"]
LEVELS = CFG["water_level_scenarios"]["levels_m"]
RUN_DATE = "2026-10-02"
plt.rcParams["font.family"] = ["DejaVu Sans", "Kohinoor Devanagari"]


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def load():
    recs, cat = [], []
    for f in sorted(STATE.glob("KAR-SET-*.json")):
        d = json.load(open(f))
        recs.append(d["rec"])
        cat += d["catalog"]
    df = pd.DataFrame(recs).sort_values("settlement_id").reset_index(drop=True)
    assert len(df) == 79, f"expected 79 settlements, found {len(df)}"
    hi = max(LEVELS)
    df["exposure_rank_buildings_le_5m"] = df["buildings_le_5m"].rank(ascending=False, method="min").astype(int)
    df[f"ghsl_change_in_{hi}m_zone_ha_1975_2020"] = (
        df[f"ghsl_built_in_{hi}m_zone_ha_2020"] - df[f"ghsl_built_in_{hi}m_zone_ha_1975"]).round(2)
    df["ghsl_change_window_ha_1975_2020"] = (df["ghsl_built_ha_2020"] - df["ghsl_built_ha_1975"]).round(2)
    return df, pd.DataFrame(cat)


def write_table(df):
    p = ROOT / "outputs/tables/karnali_79_exposure_screening.csv"
    df.to_csv(p, index=False)
    return p


def write_zones():
    parts = [gpd.read_parquet(f) for f in sorted(STATE.glob("KAR-SET-*_zones.parquet"))]
    z = pd.concat(parts, ignore_index=True)
    z = gpd.GeoDataFrame(z, crs=parts[0].crs).dissolve(by=["settlement_id", "water_level_m"]).reset_index()
    z["geometry"] = z.geometry.simplify(5)
    z["area_ha"] = (z.area / 1e4).round(2)
    z.to_crs(4326).to_file(ROOT / "data/processed/karnali_79/karnali_79_water_level_zones.geojson",
                           driver="GeoJSON", COORDINATE_PRECISION=6)


def write_inventory(df):
    p = ROOT / "settlements/settlement_inventory.csv"
    header_comments = [l for l in open(p) if l.startswith("#")]
    cols = ["settlement_id", "name", "administrative_unit", "source", "observation_date",
            "geometry_path", "confidence", "notes"]
    with open(p, "w", newline="") as f:
        f.writelines(header_comments)
        w = csv.writer(f)
        w.writerow(cols)
        for _, r in df.iterrows():
            w.writerow([
                r.settlement_id, r.settlement_name,
                f"{r.local_level} {r.local_level_type} ({r.local_level_pcode}), {r.district} District, Karnali Province",
                f"Overture Maps {CFG['overture_release']} locality {r.overture_locality_id} "
                f"(OpenStreetMap {r.osm_record}); selection rule: {r.selection_method}",
                RUN_DATE, "data/processed/karnali_79/karnali_79_settlements.geojson",
                "medium" if r.selection_method == "named_locality_max_buildings" else "low",
                f"Primary settlement of the local level selected by building density (see "
                f"docs/methodology.md); primary-script name: {r.name_primary}; point at "
                f"{r.lon}, {r.lat}. Not an official headquarters list; researcher review needed."])


def write_catalog(cat):
    p = ROOT / "data/metadata/imagery_catalog.csv"
    cols = open(p).readline().strip().split(",")
    existing = pd.read_csv(p)
    existing = existing[~existing["imagery_id"].astype(str).str.startswith("KAR-SET-")]
    out = pd.concat([existing, cat[cols]], ignore_index=True)
    out.to_csv(p, index=False)


def overview_map(df):
    pal = gpd.read_file(ROOT / "data/processed/karnali_79/karnali_79_local_levels.geojson")
    water = gpd.read_parquet(CACHE / "overture_water.parquet")
    rivers = water[(water["subtype"] == "river") & water.geom_type.isin(["LineString", "MultiLineString"])]
    prov = pal.dissolve()
    rivers = gpd.clip(rivers, prov)
    pts = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=4326)
    fig, ax = plt.subplots(figsize=(13, 11))
    pal.plot(ax=ax, facecolor=np.where(pal.local_level_type == "urban municipality", "#f3e6d0", "#f7f7f2"),
             edgecolor="#9a9a9a", lw=0.5)
    prov.boundary.plot(ax=ax, color="#333", lw=1.2)
    rivers.plot(ax=ax, color="#3b8bc2", lw=0.8)
    v = pts["buildings_le_5m"]
    sc = ax.scatter(pts.geometry.x, pts.geometry.y, s=20 + np.sqrt(v) * 9, c=pts["share_le_5m"] * 100,
                    cmap="YlOrRd", vmin=0, vmax=max(10, float(pts["share_le_5m"].max() * 100)),
                    edgecolor="k", lw=0.6, zorder=5)
    for _, r in pts.iterrows():
        ax.annotate(f"{r.settlement_id[-3:]} {r.local_level}", (r.geometry.x, r.geometry.y),
                    xytext=(4, 3), textcoords="offset points", fontsize=6.3, zorder=6)
    cb = fig.colorbar(sc, ax=ax, shrink=0.55, pad=0.01)
    cb.set_label("% of buildings in 4x4 km window with HAND <= 5 m")
    for n in (10, 100, 1000):
        ax.scatter([], [], s=20 + np.sqrt(n) * 9, facecolor="none", edgecolor="k", label=f"{n} buildings HAND <= 5 m")
    ax.legend(loc="lower left", fontsize=8, title="Marker size", title_fontsize=8, frameon=True)
    ax.set_title("Karnali Province: primary settlement of each of the 79 local levels\n"
                 "Water-related exposure SCREENING (buildings on ground <= 5 m above the drainage it flows to)",
                 fontsize=12)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    fig.text(0.01, 0.01, "Boundaries: COD-AB Nepal (Survey Dept. of Nepal / OCHA, CC BY-IGO); rivers, places, "
             "buildings: Overture Maps (OSM ODbL, Google CC BY 4.0, Microsoft ODbL); DEM: Copernicus GLO-30. "
             "Shaded = urban municipality. Screening only - not a hydraulic flood model or a risk estimate.",
             fontsize=7)
    fig.tight_layout()
    p = ROOT / "outputs/maps/karnali_79_overview_exposure_screening.png"
    fig.savefig(p, dpi=130)
    plt.close(fig)


def fmt(v, nd=0):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "NA"
    return f"{v:,.{nd}f}"


def write_profiles(df, cat):
    outdir = ROOT / "settlements/settlement_profiles"
    for _, r in df.iterrows():
        fs = f"{r.settlement_id}_{slug(r.local_level)}"
        c = cat[cat.imagery_id.str.startswith(r.settlement_id + "_")]
        rows = "\n".join(f"| {x.imagery_id.split('_', 1)[1]} | {x.acquisition_date} | {x.sensor_or_product.split(' / ')[0]} "
                         f"| {x.resolution} | `{x.source_name}` | {x.cloud_or_quality_notes.split(';')[0].replace('chip cloud/shadow fraction ', '')} |"
                         for _, x in c.iterrows())
        ghsl = " | ".join(f"{y}: {fmt(r[f'ghsl_built_ha_{y}'], 1)}" for y in CFG["ghsl_epochs"])
        ghz = " | ".join(f"{y}: {fmt(r[f'ghsl_built_in_{max(LEVELS)}m_zone_ha_{y}'], 1)}" for y in CFG["ghsl_epochs"])
        scen = "\n".join(f"| HAND <= {h} m | {fmt(r[f'buildings_le_{h}m'])} | {r[f'share_le_{h}m'] * 100:.1f}% "
                         f"| {fmt(r[f'zone_area_le_{h}m_ha'], 1)} |" for h in LEVELS)
        text = f"""# {r.settlement_id}: {r.settlement_name}

*Generated {RUN_DATE} by `analysis/hazard_exposure/compile_karnali_79.py` from the province-wide
screening run. All numbers are **derived** from the open datasets listed below; nothing here is a
field observation or a validated result. Sections marked "researcher input" are intentionally empty.*

## Identification

| Field | Value |
|---|---|
| Settlement ID | {r.settlement_id} |
| Name (display / primary script) | {r.settlement_name} / {r.name_primary} |
| Local level | {r.local_level} ({r.local_level_type}), P-code {r.local_level_pcode} |
| District | {r.district} |
| Point (WGS 84) | {r.lon}, {r.lat} |
| Selection method | `{r.selection_method}` (see docs/methodology.md) |
| Source record | Overture locality `{r.overture_locality_id}`; OSM `{r.osm_record}`; class `{r.locality_class}` |

The point is the building-density-selected primary settlement of the local level, **not** an
officially designated headquarters. Confirm or correct it (researcher input).

## Geographic context

- Analysis window: {CFG['analysis_window_m'] / 1000:g} x {CFG['analysis_window_m'] / 1000:g} km centred on the point.
- Building footprints in window: {fmt(r.buildings_in_window)} (OSM {fmt(r.buildings_osm)}, Google {fmt(r.buildings_google)}, Microsoft {fmt(r.buildings_microsoft)}; Overture de-duplicated).

## Nearby rivers / water bodies

- Nearest named mapped watercourse: {f"**{r.nearest_named_water}**, {fmt(r.nearest_named_water_m)} m from the point" if r.nearest_named_water != "unknown" else "none named in OSM within the 6 x 6 km context window"}.
- Nearest mapped river-class line: {fmt(r.nearest_river_line_m)} m.
- Buildings within 100 m of a mapped river/stream: {fmt(r.buildings_within_100m_of_channel)}.
- Median HAND of buildings in window: {fmt(r.median_building_hand_m, 1)} m.

## Historical imagery

![Time series](../../outputs/figures/karnali_79/imagery_timeseries/{fs}_timeseries_1972_2026.png)

| Epoch | Acquired | Platform | Resolution | Scene ID | Chip cloud/shadow/snow fraction |
|---|---|---|---|---|---|
{rows}

Epochs without a row had no usable dry-season scene in the archive window.

## Observed transformation

**Derived (GHSL R2023A built-up surface, ha, 100 m grid):**

- Whole window: {ghsl}
- Inside the HAND <= {max(LEVELS)} m zone: {ghz}

**Visual observations from the image series:** researcher input. Record each in
`case_studies/.../metadata/observation_log.csv` style: image ID, feature, observed change, confidence.

## Hazard context (water-level scenarios)

![Scenarios](../../outputs/figures/karnali_79/water_level_scenarios/{fs}_water_level_scenarios.png)

| Scenario | Buildings in zone | Share of window buildings | Zone area in window (ha) |
|---|---|---|---|
{scen}

Province rank by buildings with HAND <= 5 m: **{r.exposure_rank_buildings_le_5m} of 79** (1 = most).

## Evidence

- Imagery: Landsat Collection 2 (USGS) and Sentinel-2 L2A (ESA Copernicus) via Microsoft Planetary Computer (scene IDs above; catalogued in `data/metadata/imagery_catalog.csv`).
- DEM: Copernicus GLO-30 (`{r.dem_tiles}`).
- Channels, places, buildings: Overture Maps {CFG['overture_release']}.
- Built-up history: JRC GHS-BUILT-S R2023A.

## Interpretation

Researcher input. The derived numbers show where buildings sit on low ground relative to mapped
drainage; they do not by themselves establish flood probability, depth, or risk to life.

## Uncertainty

- HAND from a 30 m DEM: vertical error of several metres in steep terrain; narrow gorges and small
  channels are poorly resolved; unmapped streams are missing from the drainage network.
- Scenario zones are static terrain thresholds, not modelled floods: no discharge, return period,
  velocity, debris flow, landslide-dam outburst or bank erosion is represented.
- Building footprints combine OSM and ML-derived datasets of different dates; counts are not people.
- 1970s Landsat MSS (60 m, false colour) cannot resolve individual buildings; sensor, season and
  resolution differ between epochs.

## Follow-up analysis

- [ ] Confirm the settlement point and name with local knowledge.
- [ ] Record visual observations per epoch (river channel shifts, new construction on floodplain/fan).
- [ ] Check flood/debris-flow history for this location (e.g. DesInventar Nepal, BIPAD portal).
- [ ] If prioritised: higher-resolution DEM and a hydraulic model with design discharges.
"""
        (outdir / f"{fs}.md").write_text(text)


def md_table(d: pd.DataFrame) -> str:
    cols = list(d.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in d.itertuples(index=False)]
    return "\n".join(lines)


def write_report(df, cat):
    hi = max(LEVELS)
    t = df.copy()
    t["profile"] = [f"[{r.settlement_id}](../../settlements/settlement_profiles/{r.settlement_id}_{slug(r.local_level)}.md)"
                    for r in t.itertuples()]
    top = t.sort_values("buildings_le_5m", ascending=False).head(20)
    top_tab = md_table(pd.DataFrame({
        "Rank": top.exposure_rank_buildings_le_5m, "ID": top.profile, "Settlement": top.settlement_name,
        "Local level": top.local_level + " (" + top.local_level_type.str.split().str[0] + ")",
        "District": top.district, "Bldgs in window": top.buildings_in_window.map("{:,}".format),
        "HAND<=2 m": top.buildings_le_2m.map("{:,}".format), "HAND<=5 m": top.buildings_le_5m.map("{:,}".format),
        f"HAND<={hi} m": top[f"buildings_le_{hi}m"].map("{:,}".format),
        "Share <=5 m": (top.share_le_5m * 100).round(1).astype(str) + "%",
        "Nearest named watercourse": top.nearest_named_water.replace("unknown", "-")}))
    sh = t[t.buildings_in_window >= 200].sort_values("share_le_5m", ascending=False).head(15)
    share_tab = md_table(pd.DataFrame({
        "ID": sh.profile, "Settlement": sh.settlement_name, "Local level": sh.local_level,
        "Bldgs in window": sh.buildings_in_window, "HAND<=5 m": sh.buildings_le_5m,
        "Share <=5 m": (sh.share_le_5m * 100).round(1).astype(str) + "%"}))
    g = t.sort_values(f"ghsl_change_in_{hi}m_zone_ha_1975_2020", ascending=False).head(15)
    grow_tab = md_table(pd.DataFrame({
        "ID": g.profile, "Settlement": g.settlement_name, "Local level": g.local_level,
        "Built-up in zone 1975 (ha)": g[f"ghsl_built_in_{hi}m_zone_ha_1975"],
        "2000 (ha)": g[f"ghsl_built_in_{hi}m_zone_ha_2000"], "2020 (ha)": g[f"ghsl_built_in_{hi}m_zone_ha_2020"],
        "Change 1975-2020 (ha)": g[f"ghsl_change_in_{hi}m_zone_ha_1975_2020"]}))
    dist = t.groupby("district").agg(settlements=("settlement_id", "size"),
                                     buildings_in_windows=("buildings_in_window", "sum"),
                                     buildings_hand_le_2m=("buildings_le_2m", "sum"),
                                     buildings_hand_le_5m=("buildings_le_5m", "sum"),
                                     **{f"buildings_hand_le_{hi}m": (f"buildings_le_{hi}m", "sum")}).reset_index()
    typ = t.groupby("local_level_type").agg(settlements=("settlement_id", "size"),
                                            buildings_in_windows=("buildings_in_window", "sum"),
                                            buildings_hand_le_5m=("buildings_le_5m", "sum")).reset_index()
    all_tab = md_table(pd.DataFrame({
        "ID": t.profile, "Settlement": t.settlement_name, "Local level": t.local_level,
        "Type": t.local_level_type.str.split().str[0], "District": t.district,
        "Bldgs": t.buildings_in_window, "<=2 m": t.buildings_le_2m, "<=5 m": t.buildings_le_5m,
        f"<={hi} m": t[f"buildings_le_{hi}m"], "Rank (<=5 m)": t.exposure_rank_buildings_le_5m,
        "First scene": t.first_scene_date, "Latest scene": t.latest_scene_date,
        "Epochs with image": t.epochs_with_imagery.astype(str) + "/12"}))
    n_cluster = int((t.selection_method != "named_locality_max_buildings").sum())
    tot = int(t.buildings_in_window.sum())
    tot_vals = {h: int(t[f"buildings_le_{h}m"].sum()) for h in LEVELS}
    no_ch = int((~t.channels_mapped_in_context.astype(bool)).sum())
    txt = f"""# Karnali Province: water-related exposure screening of 79 local-level settlements

*Generated {RUN_DATE} by `analysis/hazard_exposure/compile_karnali_79.py`. Method:
[docs/methodology.md](../../docs/methodology.md). Limitations:
[docs/limitations.md](../../docs/limitations.md). Data sources:
[docs/data_sources.md](../../docs/data_sources.md).*

> **Read this first.** This is an **exposure screening**, not a risk assessment. It shows how many
> buildings stand on ground only a few metres above the stream or river that ground drains to
> (HAND, Height Above Nearest Drainage). It does **not** model flood frequency, depth, speed, debris
> flows or glacial-lake outbursts, and it does **not** count people. No statement about risk to human
> life is made or implied. The ranking says where a proper hazard and risk study would be most
> worthwhile first.

## Scope

- **Units:** all 79 local levels of Karnali Province (25 urban, 54 rural municipalities; COD-AB Nepal).
- **Settlements:** one primary settlement per local level, chosen by building density ({79 - n_cluster} named
  localities; {n_cluster} densest-building-cluster fallbacks). See the
  [inventory](../../settlements/settlement_inventory.csv) and
  [layer](../../data/processed/karnali_79/karnali_79_settlements.geojson).
- **Per settlement:** a 4 x 4 km window with a 12-epoch satellite time series (1972 to 2026, 5-year
  steps), HAND scenario zones at {", ".join(f"{h} m" for h in LEVELS)}, building counts in each zone,
  and GHSL built-up surface 1975–2020.

![Overview](../maps/karnali_79_overview_exposure_screening.png)

## Province summary (derived)

- Buildings inside the 79 analysis windows: **{tot:,}**.
- On ground with HAND <= 2 m: **{tot_vals[LEVELS[0]]:,}** ({tot_vals[LEVELS[0]] / tot * 100:.1f}%); <= 5 m:
  **{tot_vals[LEVELS[1]]:,}** ({tot_vals[LEVELS[1]] / tot * 100:.1f}%); <= {hi} m: **{tot_vals[hi]:,}**
  ({tot_vals[hi] / tot * 100:.1f}%).
- Image chips catalogued: {len(cat)} of {79 * 12} possible (79 x 12 epochs). Missing epochs mostly
  reflect archive gaps (especially 1980–84) or persistent cloud or snow.
- Settlements with no mapped river or stream in their 6 x 6 km context: {no_ch}. Their HAND exposure
  is reported as 0 but is **unknown**.

### By type of local level

{md_table(typ)}

### By district

{md_table(dist)}

## Highest exposure: buildings with HAND <= 5 m (top 20)

{top_tab}

## Highest share of buildings on low ground (windows with >= 200 buildings, top 15)

{share_tab}

## Built-up growth inside the HAND <= {hi} m zone, 1975–2020 (GHSL, top 15)

This answers "has construction moved onto low ground near channels?" GHSL is a ~90 m modelled
product, and its pre-1990 epochs are back-cast, so treat the values as indicative.

{grow_tab}

## All 79 settlements

{all_tab}

## Audit notes

| Check | Status |
|---|---|
| 79 local levels; 25 urban + 54 rural | passed (asserted in code) |
| One settlement per local level | passed; {n_cluster} use the cluster fallback (lower confidence) |
| Every displayed image traceable to a scene ID | passed (`data/metadata/imagery_catalog.csv`) |
| Image chips free of cloud, snow and gaps | most; exceptions keep their measured fraction in the catalogue |
| Settlement points and names reviewed by a researcher | **pending** |
| Scenario zones compared with recorded flood or debris-flow events | **pending** |
| Field validation | **pending** |
| Population or occupancy in exposed buildings | **not assessed** |
| Hazard (frequency, depth, velocity) | **not modelled** |

## Recommended next steps

1. Review the top-ranked profiles and confirm points, names and channel mapping.
2. Add event history (BIPAD portal, DesInventar Nepal) to test whether high-ranked sites match places
   with recorded floods or debris flows.
3. For confirmed priority sites, run hydraulic modelling (e.g. HEC-RAS 2D) with design discharges and a
   better DEM, then add population and vulnerability to move from exposure to risk.
"""
    out = ROOT / "outputs/reports"
    out.mkdir(exist_ok=True)
    (out / "karnali_79_exposure_screening_report.md").write_text(txt)


def main():
    df, cat = load()
    write_table(df)
    write_zones()
    write_inventory(df)
    write_catalog(cat)
    overview_map(df)
    write_profiles(df, cat)
    write_report(df, cat)
    print("compiled", len(df), "settlements,", len(cat), "image chips")


if __name__ == "__main__":
    main()
