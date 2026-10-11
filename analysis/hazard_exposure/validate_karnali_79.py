"""Validate structural consistency of committed Karnali 79 screening outputs."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import yaml
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_COUNT = 79
LEVELS = (2, 5, 10)


def _csv(path: Path, root: Path, errors: list[str], required: set[str],
         comment: str | None = None) -> pd.DataFrame:
    try:
        frame = pd.read_csv(path, comment=comment)
    except (OSError, pd.errors.ParserError, UnicodeError) as exc:
        errors.append(f"Cannot read {path.relative_to(root)}: {exc}")
        return pd.DataFrame()
    missing = required - set(frame.columns)
    if missing:
        errors.append(f"{path.relative_to(root)} missing columns: {sorted(missing)}")
    return frame


def _geojson(path: Path, root: Path, errors: list[str]) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        errors.append(f"Cannot read {path.relative_to(root)}: {exc}")
        return []
    if data.get("type") != "FeatureCollection":
        errors.append(f"{path.relative_to(root)} is not a FeatureCollection")
    crs = data.get("crs", {}).get("properties", {}).get("name")
    if crs not in ("urn:ogc:def:crs:OGC:1.3:CRS84", "OGC:CRS84"):
        errors.append(f"{path.relative_to(root)} has missing/unexpected CRS: {crs!r}")
    features = data.get("features")
    if not isinstance(features, list):
        errors.append(f"{path.relative_to(root)} has no features list")
        return []
    return features


def _ids(features: list[dict], field: str, path: Path, root: Path,
         errors: list[str]) -> list[str]:
    found = []
    for i, feature in enumerate(features):
        value = feature.get("properties", {}).get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{path.relative_to(root)} feature {i} has no {field}")
            continue
        found.append(value)
        try:
            geom = shape(feature["geometry"])
            if geom.is_empty or not geom.is_valid:
                errors.append(f"{path.relative_to(root)} feature {value} has empty/invalid geometry")
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{path.relative_to(root)} feature {value} has invalid geometry: {exc}")
    if len(found) != len(set(found)):
        errors.append(f"{path.relative_to(root)} has duplicate {field} values")
    return found


def _raster_check(cache: Path, epochs: list[int], errors: list[str], warnings: list[str]) -> int:
    folder = cache / "ghsl"
    if not folder.is_dir():
        warnings.append(f"Raster alignment skipped: GHSL cache not found at {folder}")
        return 0
    import rasterio

    grids = []
    for year in epochs:
        path = folder / f"karnali_built_s_E{year}.tif"
        if not path.is_file():
            errors.append(f"Missing GHSL raster for {year}: {path}")
            continue
        try:
            with rasterio.open(path) as src:
                grids.append((year, (src.crs, src.transform, src.width, src.height, src.bounds)))
        except rasterio.errors.RasterioError as exc:
            errors.append(f"Cannot read GHSL raster {path}: {exc}")
    if grids:
        reference_year, reference = grids[0]
        for year, grid in grids[1:]:
            if grid != reference:
                errors.append(f"GHSL raster grid for {year} differs from epoch {reference_year}")
    if len(grids) != len(epochs):
        warnings.append(f"Raster alignment checked {len(grids)} of {len(epochs)} GHSL rasters")
    return len(grids)


def validate(root: Path = ROOT, cache_dir: Path | None = None) -> tuple[list[str], list[str], dict]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    summary: dict[str, int] = {}
    try:
        config = yaml.safe_load((root / "configs/analysis_parameters.yaml").read_text())[
            "karnali_79_screening"]
    except (OSError, yaml.YAMLError, KeyError, TypeError) as exc:
        return [f"Cannot load screening configuration: {exc}"], warnings, summary

    table_path = root / "outputs/tables/karnali_79_exposure_screening.csv"
    table = _csv(table_path, root, errors, {
        "settlement_id", "local_level_pcode", "lon", "lat", "buildings_in_window",
        "epochs_with_imagery", "first_scene_date", "latest_scene_date",
        *(f"buildings_le_{h}m" for h in LEVELS), *(f"share_le_{h}m" for h in LEVELS),
    })
    expected_ids = {f"KAR-SET-{i:03d}" for i in range(1, EXPECTED_COUNT + 1)}
    table_ids: set[str] = set()
    if not table.empty and "settlement_id" in table:
        table_ids = set(table["settlement_id"].dropna().astype(str))
        if len(table) != EXPECTED_COUNT or table_ids != expected_ids:
            errors.append("Screening table must contain exactly KAR-SET-001..079 once")
        if table["settlement_id"].duplicated().any():
            errors.append("Screening table contains duplicate settlement identifiers")
        summary["settlements"] = len(table)

        count_cols = [f"buildings_le_{h}m" for h in LEVELS]
        if all(c in table for c in count_cols + ["buildings_in_window"]):
            vals = table[count_cols + ["buildings_in_window"]].apply(pd.to_numeric, errors="coerce")
            if vals.isna().any().any() or (vals < 0).any().any():
                errors.append("Building counts contain missing or negative values")
            if not ((vals[count_cols[0]] <= vals[count_cols[1]]) &
                    (vals[count_cols[1]] <= vals[count_cols[2]]) &
                    (vals[count_cols[2]] <= vals["buildings_in_window"])).all():
                errors.append("HAND building counts are not nested or exceed window totals")
        share_cols = [f"share_le_{h}m" for h in LEVELS]
        if all(c in table for c in share_cols):
            vals = table[share_cols].apply(pd.to_numeric, errors="coerce")
            if vals.isna().any().any() or ((vals < 0) | (vals > 1)).any().any():
                errors.append("HAND shares contain missing values or values outside [0, 1]")
            if not ((vals[share_cols[0]] <= vals[share_cols[1]]) &
                    (vals[share_cols[1]] <= vals[share_cols[2]])).all():
                errors.append("HAND shares are not nested")
        for col in ("first_scene_date", "latest_scene_date"):
            if col in table:
                for sid, value in zip(table["settlement_id"], table[col]):
                    if pd.isna(value) or str(value) in ("NA", "unknown", ""):
                        continue
                    try:
                        date.fromisoformat(str(value))
                    except ValueError:
                        errors.append(f"{sid} has invalid {col}: {value!r}")
        lon, lat = pd.to_numeric(table["lon"], errors="coerce"), pd.to_numeric(table["lat"], errors="coerce")
        if (lon.isna().any() or lat.isna().any() or not lon.between(-180, 180).all()
                or not lat.between(-90, 90).all()):
            errors.append("Settlement coordinates are missing or outside longitude/latitude ranges")

    settlement_path = root / "data/processed/karnali_79/karnali_79_settlements.geojson"
    settlement_features = _geojson(settlement_path, root, errors)
    settlement_ids = set(_ids(settlement_features, "settlement_id", settlement_path, root, errors))
    if len(settlement_features) != EXPECTED_COUNT or settlement_ids != table_ids:
        errors.append("Settlement GeoJSON identifiers/count do not match the screening table")
    if settlement_features and not table.empty:
        coords = {r.settlement_id: (r.lon, r.lat) for r in table.itertuples()}
        for feature in settlement_features:
            props = feature.get("properties", {})
            sid = props.get("settlement_id")
            point = feature.get("geometry") or {}
            xy = point.get("coordinates", [])
            if (sid not in coords or point.get("type") != "Point" or len(xy) < 2
                    or abs(xy[0] - coords[sid][0]) > 1e-5 or abs(xy[1] - coords[sid][1]) > 1e-5):
                errors.append(f"{sid} settlement geometry/coordinates do not match table")
    summary["settlement_geometries"] = len(settlement_features)

    admin_path = root / "data/processed/karnali_79/karnali_79_local_levels.geojson"
    admin_features = _geojson(admin_path, root, errors)
    admin_codes = _ids(admin_features, "adm3_pcode", admin_path, root, errors)
    if len(admin_features) != EXPECTED_COUNT or len(set(admin_codes)) != EXPECTED_COUNT:
        errors.append("Local-level GeoJSON must contain 79 unique valid administrative geometries")
    if not table.empty and "local_level_pcode" in table and set(table["local_level_pcode"]) != set(admin_codes):
        errors.append("Local-level GeoJSON P-codes do not match the screening table")
    summary["local_levels"] = len(admin_features)

    zones_path = root / "data/processed/karnali_79/karnali_79_water_level_zones.geojson"
    zones = _geojson(zones_path, root, errors)
    zone_keys = []
    for i, feature in enumerate(zones):
        props = feature.get("properties", {})
        sid, level = props.get("settlement_id"), props.get("water_level_m")
        if sid is None or level not in LEVELS:
            errors.append(f"Water-zone feature {i} has unknown settlement/threshold")
            continue
        zone_keys.append((str(sid), int(level)))
        try:
            geom = shape(feature["geometry"])
            if geom.is_empty or not geom.is_valid or geom.geom_type not in ("Polygon", "MultiPolygon"):
                errors.append(f"Water zone {sid} HAND {level} has invalid polygon geometry")
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"Water zone {sid} HAND {level} has unreadable geometry: {exc}")
        area = pd.to_numeric(props.get("area_ha"), errors="coerce")
        if pd.isna(area) or area <= 0:
            errors.append(f"Water zone {sid} HAND {level} has invalid area_ha")
    expected_zones = {(sid, h) for sid in table_ids for h in LEVELS}
    if len(zone_keys) != EXPECTED_COUNT * len(LEVELS) or set(zone_keys) != expected_zones:
        errors.append("Water zones must have one feature per settlement at HAND 2, 5 and 10 m")
    if len(zone_keys) != len(set(zone_keys)):
        errors.append("Water zones contain duplicate settlement/threshold features")
    summary["water_level_zones"] = len(zones)

    inventory_path = root / "settlements/settlement_inventory.csv"
    inventory = _csv(inventory_path, root, errors,
                     {"settlement_id", "name", "source", "observation_date"}, comment="#")
    if not inventory.empty and "settlement_id" in inventory:
        ids = set(inventory["settlement_id"].dropna().astype(str))
        if len(inventory) != EXPECTED_COUNT or ids != table_ids:
            errors.append("Settlement inventory identifiers/count do not match screening table")
        summary["inventory_rows"] = len(inventory)

    registry_path = root / "data/metadata/datasets.csv"
    registry = _csv(registry_path, root, errors, {
        "dataset_id", "source_name", "provider", "license", "acquisition_date",
        "temporal_coverage", "crs", "relative_path", "checksum",
    })
    if registry.empty:
        warnings.append("Dataset source registry has no source records")
    else:
        for col in ("dataset_id", "source_name", "provider", "license"):
            if col in registry and registry[col].isna().any():
                errors.append(f"Dataset registry has missing {col}")
        if "dataset_id" in registry and registry["dataset_id"].duplicated().any():
            errors.append("Dataset registry contains duplicate dataset_id values")
        summary["registered_sources"] = len(registry)

    imagery_path = root / "data/metadata/imagery_catalog.csv"
    imagery = _csv(imagery_path, root, errors, {
        "imagery_id", "source_name", "provider", "license", "acquisition_date", "year",
        "resolution", "crs",
    })
    if not imagery.empty:
        if imagery["imagery_id"].duplicated().any():
            errors.append("Imagery catalogue contains duplicate imagery_id values")
        epochs = {str(e["label"]): e for e in config["imagery"]["epochs"]}
        counts: dict[str, int] = {}
        for _, row in imagery.iterrows():
            image_id = str(row["imagery_id"])
            sid, sep, label = image_id.rpartition("_")
            if not sep or sid not in table_ids or label not in epochs:
                errors.append(f"Unexpected imagery_id: {image_id}")
                continue
            counts[sid] = counts.get(sid, 0) + 1
            try:
                acquired = date.fromisoformat(str(row["acquisition_date"]))
                epoch = epochs[label]
                if not date.fromisoformat(epoch["start"]) <= acquired <= date.fromisoformat(epoch["end"]):
                    errors.append(f"{image_id} acquisition date is outside configured epoch dates")
                if acquired.month not in config["imagery"]["dry_season_months"]:
                    errors.append(f"{image_id} acquisition is outside configured dry-season months")
                if str(row["year"]) != str(acquired.year):
                    errors.append(f"{image_id} year does not match acquisition_date")
            except (TypeError, ValueError):
                errors.append(f"{image_id} has an invalid acquisition date/year")
            for col in ("source_name", "provider", "license"):
                if pd.isna(row[col]) or not str(row[col]).strip():
                    errors.append(f"{image_id} is missing {col}")
        if not table.empty and "epochs_with_imagery" in table:
            lookup = table.set_index("settlement_id")["epochs_with_imagery"]
            for sid in table_ids:
                if counts.get(sid, 0) != int(lookup[sid]):
                    errors.append(f"{sid} imagery count differs from epochs_with_imagery")
        summary["imagery_records"] = len(imagery)

    log_path = root / "data/metadata/processing_log.csv"
    log = _csv(log_path, root, errors, {
        "log_id", "source_path", "output_path", "processing_date", "method_or_script",
        "parameters", "software_environment",
    })
    if log.empty:
        warnings.append("Processing log has no run records/checksums/environment capture")

    cache_dir = cache_dir or (Path(os.environ["KARNALI_CACHE"]) if os.environ.get("KARNALI_CACHE") else None)
    if cache_dir is None:
        warnings.append("Raster alignment skipped: raw/cache rasters are not committed; pass --cache-dir")
    else:
        summary["ghsl_rasters_checked"] = _raster_check(cache_dir, config["ghsl_epochs"], errors, warnings)
    return errors, warnings, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, help="Cache containing ghsl/karnali_built_s_E<year>.tif")
    args = parser.parse_args()
    errors, warnings, summary = validate(ROOT, args.cache_dir)
    print(json.dumps({"summary": summary, "warnings": warnings, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
