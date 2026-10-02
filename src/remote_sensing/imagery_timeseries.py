"""Select and read cloud-free satellite image chips per epoch from Microsoft Planetary Computer.

Collections (all openly licensed, read in place as Cloud-Optimized GeoTIFFs, nothing stored):
  landsat-c2-l1   Landsat 1-5 MSS (1972-1992), 60 m, green/red/nir08 -> false colour
  landsat-c2-l2   Landsat 4-9 TM/ETM+/OLI surface reflectance, 30 m, true colour
  sentinel-2-l2a  Sentinel-2 surface reflectance, 10 m, true colour

For each epoch, candidate scenes in the epoch's date window and season are ranked by
scene cloud cover; the best ``max_candidates`` are checked with the scene QA band over
the chip itself. Among those under the chip cloud/shadow and no-data limits, the winner
is terrain-corrected first, then closest to the target year, then highest sun elevation.
Every choice is returned with its scene ID, date, sensor and measured chip cloud
fraction so it can be catalogued.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import numpy as np
import planetary_computer as pc
import pystac_client
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

GDAL_ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MAX_RETRY="4",
                GDAL_HTTP_RETRY_DELAY="2", VSI_CACHE="TRUE", GDAL_HTTP_MULTIRANGE="YES")

# Per-collection band recipe: display bands, QA band, and how to decode cloud/no-data.
SENSORS = {
    "landsat-c2-l1": {"bands": ["nir08", "red", "green"], "qa": "qa_pixel", "res": 60,
                      "display": "false colour (NIR-red-green): vegetation red, water dark"},
    "landsat-c2-l2": {"bands": ["red", "green", "blue"], "qa": "qa_pixel", "res": 30,
                      "display": "true colour"},
    "sentinel-2-l2a": {"bands": ["B04", "B03", "B02"], "qa": "SCL", "res": 10,
                       "display": "true colour"},
}


@dataclass
class Epoch:
    label: str          # e.g. "1972" or "2026 (latest)"
    target_year: int
    collection: str
    start: str          # ISO date, inclusive
    end: str            # ISO date, inclusive
    exclude_platforms: tuple = ()


@dataclass
class Chip:
    epoch: str
    collection: str
    item_id: str
    platform: str
    acquired: str
    sun_elevation: float | None
    scene_cloud_cover: float | None
    chip_cloud_fraction: float
    chip_nodata_fraction: float
    resolution_m: int
    display: str
    rgb: np.ndarray     # (3, h, w) float32: surface reflectance (L2/S2) or DN (MSS)


def bad_mask(collection: str, qa: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (obscured, nodata) boolean masks from a QA array.

    obscured = cloud, cloud shadow, cirrus or snow/ice (snow hides settlements and
    saturates the display, so it is treated as unusable for this purpose).
    nodata   = fill, outside the scene footprint (QA 0 after warping) or SLC-off gaps.
    """
    if collection == "sentinel-2-l2a":
        nodata = qa == 0
        obscured = np.isin(qa, [3, 8, 9, 10, 11])
    else:
        qa = qa.astype(np.uint16)
        nodata = (qa == 0) | ((qa & 1) > 0)
        obscured = (((qa >> 1) & 1) | ((qa >> 3) & 1) | ((qa >> 4) & 1) | ((qa >> 5) & 1)) > 0
    return obscured & ~nodata, nodata


def read_band(href: str, bounds, crs: str, res: float, resampling=Resampling.bilinear) -> np.ndarray:
    """Read a band warped onto the chip grid (bounds in ``crs``) at ``res`` metres."""
    w = int(round((bounds[2] - bounds[0]) / res))
    h = int(round((bounds[3] - bounds[1]) / res))
    transform = rasterio.transform.from_bounds(*bounds, w, h)
    with rasterio.Env(**GDAL_ENV), rasterio.open(href) as src:
        with WarpedVRT(src, crs=crs, transform=transform, width=w, height=h,
                       resampling=resampling) as vrt:
            return vrt.read(1)


def in_season(d: dt.datetime, months: list[int]) -> bool:
    return d.month in months


def best_chip(catalog: pystac_client.Client, epoch: Epoch, lonlat: tuple[float, float],
              bounds, crs: str, months: list[int], max_candidates: int,
              max_cloud: float, max_nodata: float) -> Chip | None:
    spec = SENSORS[epoch.collection]
    items = catalog.search(collections=[epoch.collection],
                           intersects={"type": "Point", "coordinates": list(lonlat)},
                           datetime=f"{epoch.start}/{epoch.end}", max_items=400).item_collection()
    items = [i for i in items if in_season(i.datetime, months)
             and i.properties.get("platform") not in epoch.exclude_platforms]
    # Landsat 7 scan-line corrector failed on 2003-05-31; striped scenes are used only
    # when no other scene exists for the epoch.
    slc_off = [i for i in items if i.properties.get("platform") == "landsat-7"
               and i.datetime.date() > dt.date(2003, 5, 31)]
    if len(slc_off) < len(items):
        items = [i for i in items if i not in slc_off]
    items.sort(key=lambda i: (i.properties.get("eo:cloud_cover", 100),
                              abs(i.datetime.year - epoch.target_year)))
    tried = []
    for item in items[:max_candidates]:
        item = pc.sign(item)
        try:
            qa = read_band(item.assets[spec["qa"]].href, bounds, crs, spec["res"], Resampling.nearest)
        except Exception:  # unreadable asset: skip candidate
            continue
        cloud, nodata = bad_mask(epoch.collection, qa)
        valid = max(1, (~nodata).sum())
        tried.append((item, float(cloud.sum() / valid), float(nodata.mean())))
    if not tried:
        return None
    ok = [t for t in tried if t[1] <= max_cloud and t[2] <= max_nodata]
    if ok:
        # Prefer terrain-corrected scenes (Landsat L1TP/L2SP), then closeness to the
        # target year, then higher sun elevation (less terrain shadow).
        item, cf, nf = min(ok, key=lambda t: ("_L1GS_" in t[0].id or "_L1GT_" in t[0].id,
                                              abs(t[0].datetime.year - epoch.target_year),
                                              -(t[0].properties.get("view:sun_elevation") or 0)))
    else:
        item, cf, nf = min(tried, key=lambda t: (t[2] > max_nodata, t[1]))
    item = pc.sign(item)
    rgb = np.stack([read_band(item.assets[b].href, bounds, crs, spec["res"]).astype(np.float32)
                    for b in spec["bands"]])
    rgb = to_reflectance(epoch.collection, rgb, item.datetime.date())
    return Chip(epoch=epoch.label, collection=epoch.collection, item_id=item.id,
                platform=item.properties.get("platform", "unknown"),
                acquired=item.datetime.date().isoformat(),
                sun_elevation=item.properties.get("view:sun_elevation"),
                scene_cloud_cover=item.properties.get("eo:cloud_cover"),
                chip_cloud_fraction=round(cf, 4), chip_nodata_fraction=round(nf, 4),
                resolution_m=spec["res"], display=spec["display"], rgb=rgb)


def open_catalog() -> pystac_client.Client:
    return pystac_client.Client.open(STAC_URL)


def to_reflectance(collection: str, dn: np.ndarray, date: dt.date) -> np.ndarray:
    """Surface reflectance for L2 products; MSS L1 stays in DN (0 = no data -> NaN)."""
    out = dn.astype(np.float32)
    out[dn == 0] = np.nan
    if collection == "landsat-c2-l2":
        return out * 2.75e-5 - 0.2
    if collection == "sentinel-2-l2a":
        # Processing baseline 04.00 (from 2022-01-25) adds a -1000 radiometric offset.
        return (out - (1000 if date >= dt.date(2022, 1, 25) else 0)) / 10000
    return out


def stretch(chip_or_rgb, lo_pct: float = 2, hi_pct: float = 98, max_refl: float = 0.25,
            gamma: float = 1.3) -> np.ndarray:
    """Display RGB in 0-1.

    Surface-reflectance chips (Landsat L2, Sentinel-2) use one fixed scale (0-max_refl,
    gamma) so brightness is comparable between dates; MSS DN chips use a per-band
    percentile stretch.
    """
    rgb = getattr(chip_or_rgb, "rgb", chip_or_rgb)
    coll = getattr(chip_or_rgb, "collection", "landsat-c2-l1")
    if coll in ("landsat-c2-l2", "sentinel-2-l2a"):
        out = np.clip(np.nan_to_num(rgb, nan=0) / max_refl, 0, 1) ** (1 / gamma)
        return np.moveaxis(out, 0, -1)
    out = np.zeros(rgb.shape, dtype=np.float32)
    for b in range(rgb.shape[0]):
        v = rgb[b][np.isfinite(rgb[b])]
        if v.size == 0:
            continue
        lo, hi = np.percentile(v, [lo_pct, hi_pct])
        out[b] = np.clip((np.nan_to_num(rgb[b], nan=lo) - lo) / max(hi - lo, 1e-6), 0, 1)
    return np.moveaxis(out, 0, -1)
