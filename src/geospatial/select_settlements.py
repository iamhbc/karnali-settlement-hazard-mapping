"""Select one primary settlement per local level (palika) in Karnali Province.

Rule (documented in docs/methodology.md):
  For each of the 79 local levels, take every named Overture/OSM locality point
  inside its boundary and count building footprints (Overture buildings theme:
  OSM + Google Open Buildings + Microsoft ML Buildings) within
  ``settlement_selection.building_count_radius_m`` of the point. The locality
  with the highest count is the primary settlement. Ties -> larger locality
  class (city > town > village > hamlet), then name.

This is a reproducible, data-driven proxy for "main settlement"; it is not the
official municipal headquarters list and must be reviewed by the researcher.
"""
from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

CLASS_RANK = {"city": 4, "town": 3, "village": 2, "hamlet": 1}


def select_primary_settlements(palikas: gpd.GeoDataFrame,
                               localities: gpd.GeoDataFrame,
                               buildings_xy: np.ndarray,
                               radius_m: float,
                               metric_crs: str) -> gpd.GeoDataFrame:
    """Return one row per palika with the selected locality and its building count.

    buildings_xy: (n, 2) building centroids already projected to metric_crs.
    """
    pal = palikas.to_crs(metric_crs)
    loc = localities.to_crs(metric_crs)
    loc = loc[loc["name"].notna()].copy()
    loc = gpd.sjoin(loc, pal[["adm3_pcode", "geometry"]], predicate="within", how="inner")
    tree = cKDTree(buildings_xy)
    xy = np.column_stack([loc.geometry.x, loc.geometry.y])
    loc["buildings_within_radius"] = [len(i) for i in tree.query_ball_point(xy, r=radius_m)]
    loc["class_rank"] = loc["class"].map(CLASS_RANK).fillna(0)
    loc = loc.sort_values(["adm3_pcode", "buildings_within_radius", "class_rank", "name"],
                          ascending=[True, False, False, True])
    loc["candidates_in_palika"] = loc.groupby("adm3_pcode")["name"].transform("size")
    best = loc.groupby("adm3_pcode").head(1).drop(columns=["index_right", "class_rank"])
    missing = set(pal["adm3_pcode"]) - set(best["adm3_pcode"])
    if missing:
        raise ValueError(f"No named locality found in palikas: {sorted(missing)}")
    return best


def densest_building_cluster(palikas: gpd.GeoDataFrame,
                             buildings_xy: np.ndarray,
                             radius_m: float,
                             metric_crs: str) -> pd.DataFrame:
    """For each palika, the building whose radius_m neighbourhood holds the most buildings.

    Returns adm3_pcode, cluster_x, cluster_y (mean of the neighbourhood, metric_crs)
    and cluster_buildings.
    """
    pal = palikas.to_crs(metric_crs)
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(buildings_xy[:, 0], buildings_xy[:, 1]),
                           crs=metric_crs)
    pts = gpd.sjoin(pts, pal[["adm3_pcode", "geometry"]], predicate="within", how="inner")
    tree = cKDTree(buildings_xy)
    rows = []
    for code, grp in pts.groupby("adm3_pcode"):
        xy = np.column_stack([grp.geometry.x, grp.geometry.y])
        counts = tree.query_ball_point(xy, r=radius_m, return_length=True)
        i = int(np.argmax(counts))
        nb = buildings_xy[tree.query_ball_point(xy[i], r=radius_m)]
        rows.append({"adm3_pcode": code, "cluster_x": nb[:, 0].mean(), "cluster_y": nb[:, 1].mean(),
                     "cluster_buildings": int(counts[i])})
    return pd.DataFrame(rows)


def resolve_primary_settlements(named: gpd.GeoDataFrame,
                                clusters: pd.DataFrame,
                                localities: gpd.GeoDataFrame,
                                min_share: float,
                                metric_crs: str) -> gpd.GeoDataFrame:
    """Keep the named locality unless it holds < min_share of the densest cluster's buildings;
    then use the cluster centre, labelled with the nearest named locality (method recorded)."""
    named = named.to_crs(metric_crs).merge(clusters, on="adm3_pcode")
    loc = localities.to_crs(metric_crs)
    loc = loc[loc["name"].notna()].reset_index(drop=True)
    tree = cKDTree(np.column_stack([loc.geometry.x, loc.geometry.y]))
    out = []
    for _, r in named.iterrows():
        r = r.copy()
        if r["buildings_within_radius"] >= min_share * r["cluster_buildings"]:
            r["selection_method"] = "named_locality_max_buildings"
        else:
            d, j = tree.query([r["cluster_x"], r["cluster_y"]])
            r["geometry"] = gpd.points_from_xy([r["cluster_x"]], [r["cluster_y"]])[0]
            r["name"] = loc.loc[j, "name"]
            r["name_en"] = loc.loc[j, "name_en"] if "name_en" in loc else None
            r["class"] = loc.loc[j, "class"]
            r["id"] = loc.loc[j, "id"]
            r["src_id"] = loc.loc[j, "src_id"]
            r["label_distance_m"] = round(float(d))
            r["buildings_within_radius"] = r["cluster_buildings"]
            r["selection_method"] = "densest_building_cluster_nearest_name"
        out.append(r)
    return gpd.GeoDataFrame(out, crs=metric_crs)
